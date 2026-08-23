import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.generate import generate_catalog
from app.pipeline.merge import MergedEvidence, merge_evidence
from app.pipeline.speech import transcribe_voice
from app.pipeline.vision import ImageAnalysis, analyze_images


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content

    def create(self, **_kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class PipelineTests(unittest.TestCase):
    def test_merge_preserves_all_sources(self):
        evidence = merge_evidence(
            ImageAnalysis("لیوان", ["آبی"], "شیشه", ["Made in Iran"]),
            "لیوان ۵۰۰ میلی‌لیتری",
            "مناسب هدیه",
        )
        self.assertEqual(evidence.detected_type, "لیوان")
        self.assertEqual(evidence.colors, ["آبی"])
        self.assertEqual(evidence.voice_transcript, "لیوان ۵۰۰ میلی‌لیتری")
        self.assertEqual(evidence.seller_hint, "مناسب هدیه")

    def test_vision_returns_structured_analysis_from_model_response(self):
        response = json.dumps(
            {"detected_type": "کیف", "colors": ["مشکی"], "material_guess": "چرم", "text_on_package": []}
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image, patch("app.pipeline.vision.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.vision.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(response)))
        ):
            image.write(b"image")
            image.flush()
            result = analyze_images([image.name])

        self.assertEqual(result, ImageAnalysis("کیف", ["مشکی"], "چرم", []))

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

    def test_generate_builds_catalog_response_from_model_json(self):
        response = json.dumps(
            {
                "title": "کیف چرمی مشکی",
                "category": {"suggested": "کیف", "confidence": 0.9},
                "description": "یک کیف چرمی مشکی.",
                "attributes": [{"name": "جنس", "value": "چرم", "confidence": 0.8}],
                "variants": [],
                "missing_info_questions": ["ابعاد کیف چیست؟"],
                "source_evidence": {"from_image": ["کیف مشکی"], "from_voice": [], "from_text_on_package": []},
            }
        )
        with patch("app.pipeline.generate.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.generate.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(response)))
        ):
            result = generate_catalog(MergedEvidence(detected_type="کیف", colors=["مشکی"]))

        self.assertEqual(result.title, "کیف چرمی مشکی")
        self.assertEqual(result.category.suggested, "کیف")
        self.assertEqual(result.attributes[0].value, "چرم")

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


if __name__ == "__main__":
    unittest.main()
