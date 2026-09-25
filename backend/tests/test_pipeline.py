import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.auth import current_seller
from app.marketplaces import export_payload
from app.pipeline.cache import cache_key
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.generate import generate_catalog
from app.pipeline.merge import MergedEvidence, merge_evidence
from app.pipeline.speech import transcribe_voice
from app.pipeline.vision import ImageAnalysis, analyze_images
from app.schemas.catalog import CatalogGenerateResponse, CatalogUpdate
from app.storage import create_draft, get_draft, seller_context, update_draft


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content
        self.calls = 0

    def create(self, **_kwargs):
        self.calls += 1
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class PipelineTests(unittest.TestCase):
    def test_merge_preserves_all_sources(self):
        evidence = merge_evidence(
            ImageAnalysis("لیوان", ["آبی", "قرمز"], "شیشه", ["Made in Iran"]),
            "لیوان ۵۰۰ میلی‌لیتری",
            "مناسب هدیه",
        )
        self.assertEqual(evidence.detected_type, "لیوان")
        self.assertEqual(evidence.colors, ["آبی", "قرمز"])
        self.assertEqual(evidence.voice_transcript, "لیوان ۵۰۰ میلی‌لیتری")
        self.assertEqual(evidence.seller_hint, "مناسب هدیه")

    def test_vision_returns_structured_analysis_from_model_response_and_caches(self):
        response = json.dumps(
            {"detected_type": "کیف", "colors": ["مشکی", "مشکی"], "material_guess": "چرم", "text_on_package": []}
        )
        fake = FakeCompletions(response)
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.NamedTemporaryFile(suffix=".jpg") as image, patch(
            "app.pipeline.vision.OPENAI_API_KEY", "test-key"
        ), patch("app.pipeline.cache.VISION_CACHE_DIR", Path(cache_dir)), patch(
            "app.pipeline.vision.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=fake))
        ):
            image.write(b"image")
            image.flush()
            result = analyze_images([image.name])
            cached = analyze_images([image.name])

        self.assertEqual(result, ImageAnalysis("کیف", ["مشکی"], "چرم", []))
        self.assertEqual(cached, result)
        self.assertEqual(fake.calls, 1)

    def test_cache_key_depends_on_file_content(self):
        with tempfile.NamedTemporaryFile() as first, tempfile.NamedTemporaryFile() as second:
            first.write(b"same")
            second.write(b"same")
            first.flush()
            second.flush()
            self.assertEqual(cache_key([first.name]), cache_key([second.name]))

    def test_speech_returns_transcript_from_model_response(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3") as audio, patch("app.pipeline.speech.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.speech.OpenAI",
            return_value=SimpleNamespace(
                audio=SimpleNamespace(transcriptions=SimpleNamespace(create=lambda **_kwargs: SimpleNamespace(text="  متن فارسی  ")))
            ),
        ):
            audio.write(b"audio")
            audio.flush()
            self.assertEqual(transcribe_voice(audio.name), "متن فارسی")

    def test_generate_builds_catalog_response_from_model_json_with_english(self):
        response = json.dumps(
            {
                "title": "کیف چرمی مشکی",
                "category": {"suggested": "کیف", "confidence": 0.9},
                "description": "یک کیف چرمی مشکی.",
                "attributes": [{"name": "جنس", "value": "چرم", "confidence": 0.8}],
                "variants": [{"type": "رنگ", "options": ["مشکی", "قهوه‌ای"]}],
                "missing_info_questions": ["ابعاد کیف چیست؟"],
                "source_evidence": {"from_image": ["کیف مشکی"], "from_voice": [], "from_text_on_package": []},
                "english": {
                    "title": "Black leather bag",
                    "description": "A black leather bag.",
                    "attributes": [{"name": "Material", "value": "Leather", "confidence": 0.8}],
                },
            }
        )
        with patch("app.pipeline.generate.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.generate.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(response)))
        ):
            result = generate_catalog(MergedEvidence(detected_type="کیف", colors=["مشکی", "قهوه‌ای"]))

        self.assertEqual(result.title, "کیف چرمی مشکی")
        self.assertEqual(result.category.suggested, "کیف")
        self.assertEqual(result.variants[0].options, ["مشکی", "قهوه‌ای"])
        self.assertEqual(result.english.title, "Black leather bag")

    def test_missing_key_fails_without_calling_model(self):
        with patch("app.pipeline.vision.OPENAI_API_KEY", ""):
            with self.assertRaises(EngineNotConfiguredError):
                analyze_images(["unused.jpg"])

    def test_invalid_model_json_is_reported_as_engine_error(self):
        with patch("app.pipeline.generate.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.generate.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions("not-json")))
        ):
            with self.assertRaises(EngineCallError):
                generate_catalog(MergedEvidence())

    def test_auth_maps_bearer_key_and_rate_limits(self):
        with patch("app.auth.API_KEYS", "seller-1:secret"), patch("app.auth.RATE_LIMIT_PER_MINUTE", 1), patch(
            "app.auth._request_times", {}
        ):
            self.assertEqual(current_seller("Bearer secret"), "seller-1")
            with self.assertRaises(HTTPException) as ctx:
                current_seller("Bearer secret")
            self.assertEqual(ctx.exception.status_code, 429)

    def test_storage_persists_history_and_feedback_updates(self):
        catalog = CatalogGenerateResponse(
            title="کیف",
            category={"suggested": "کیف", "confidence": 0.9},
            description="توضیح",
            attributes=[],
            variants=[],
            missing_info_questions=[],
            source_evidence={},
        )
        with tempfile.TemporaryDirectory() as data_dir, patch("app.storage.DATABASE_PATH", Path(data_dir) / "db.sqlite3"):
            draft = create_draft("seller", catalog)
            self.assertEqual(get_draft("seller", draft.id).catalog.title, "کیف")
            updated = update_draft("seller", draft.id, CatalogUpdate(title="کیف جدید"))
            self.assertEqual(updated.catalog.title, "کیف جدید")
            self.assertEqual(seller_context("seller")[0].title, "کیف جدید")

    def test_marketplace_export_uses_catalog_fields(self):
        catalog = CatalogGenerateResponse(
            title="کیف",
            category={"suggested": "کیف", "confidence": 0.9},
            description="توضیح",
            attributes=[],
            variants=[],
            missing_info_questions=[],
            source_evidence={},
        )
        payload = export_payload("digikala", catalog)
        self.assertEqual(payload["title"], "کیف")
        self.assertEqual(payload["category"], "کیف")


if __name__ == "__main__":
    unittest.main()
