import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from openai import (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

from app.pipeline import cache
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.generate import generate_catalog
from app.pipeline.merge import MergedEvidence, merge_evidence
from app.pipeline.retry import call_with_retry
from app.pipeline.speech import transcribe_voice
from app.pipeline.vision import ImageAnalysis, analyze_images

_API_URL = "https://api.openai.com/v1/chat/completions"

_VISION_JSON = json.dumps(
    {"detected_type": "کیف", "colors": ["مشکی"], "material_guess": "چرم", "text_on_package": []}
)

_CATALOG_JSON = json.dumps(
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


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content

    def create(self, **_kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class CountingCompletions(FakeCompletions):
    """مثل FakeCompletions ولی تعداد فراخوانی مدل را می‌شمارد (برای اثبات cache hit بودن)."""

    def __init__(self, content: str):
        super().__init__(content)
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        return super().create(**kwargs)


class FlakyCompletions(FakeCompletions):
    """اولین فراخوانی را با خطای موقت شکست می‌دهد تا مسیر retry تست شود."""

    def __init__(self, content: str, error: Exception):
        super().__init__(content)
        self.error = error
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise self.error
        return super().create(**kwargs)


def _request() -> httpx.Request:
    return httpx.Request("POST", _API_URL)


def _transient_error() -> APIConnectionError:
    """خطای موقت شبکه (همان کلاسی که SDK موقع قطع اتصال raise می‌کند)."""
    return APIConnectionError(request=_request())


def _status_error(kind, status_code: int):
    """خطای HTTP واقعی SDK با کد وضعیت دلخواه (401/400/500/429/...)."""
    return kind("خطای تست", response=httpx.Response(status_code, request=_request()), body=None)


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
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.NamedTemporaryFile(suffix=".jpg") as image, patch(
            "app.pipeline.cache.IMAGE_CACHE_DIR", cache_dir
        ), patch("app.pipeline.vision.OPENAI_API_KEY", "test-key"), patch(
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


class RetryTests(unittest.TestCase):
    """retry/backoff فراخوانی مدل — فقط روی خطای موقت."""

    def setUp(self):
        # sleep واقعی نمی‌خوابیم؛ فقط تأخیرهای درخواستی را ثبت می‌کنیم.
        sleeper = patch("app.pipeline.retry.sleep")
        self.sleep = sleeper.start()
        self.addCleanup(sleeper.stop)

    def test_transient_error_is_retried_and_then_succeeds(self):
        calls = []

        def call() -> str:
            calls.append(1)
            if len(calls) == 1:
                raise _transient_error()
            return "ok"

        self.assertEqual(call_with_retry(call, operation="test"), "ok")
        self.assertEqual(len(calls), 2)
        self.sleep.assert_called_once()
        self.assertGreater(self.sleep.call_args.args[0], 0)

    def test_server_and_rate_limit_errors_are_retried(self):
        for error in (_status_error(InternalServerError, 500), _status_error(RateLimitError, 429)):
            with self.subTest(error=type(error).__name__):
                self.sleep.reset_mock()
                calls = []

                def call(error=error):
                    calls.append(1)
                    raise error

                with self.assertRaises(type(error)):
                    call_with_retry(call, operation="test")
                # پیش‌فرض MODEL_MAX_ATTEMPTS=3 → دو تلاش دوباره
                self.assertEqual(len(calls), 3)
                self.assertEqual(self.sleep.call_count, 2)

    def test_client_errors_are_not_retried(self):
        errors = (
            _status_error(AuthenticationError, 401),
            _status_error(PermissionDeniedError, 403),
            _status_error(BadRequestError, 400),
        )
        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.sleep.reset_mock()
                calls = []

                def call(error=error):
                    calls.append(1)
                    raise error

                with self.assertRaises(type(error)):
                    call_with_retry(call, operation="test")
                self.assertEqual(len(calls), 1)
                self.sleep.assert_not_called()

    def test_non_transient_application_error_is_not_retried(self):
        calls = []

        def call():
            calls.append(1)
            raise ValueError("خطای برنامه")

        with self.assertRaises(ValueError):
            call_with_retry(call, operation="test")
        self.assertEqual(len(calls), 1)
        self.sleep.assert_not_called()

    def test_giving_up_is_bounded_by_max_attempts(self):
        with patch("app.pipeline.retry.MODEL_MAX_ATTEMPTS", 2):
            calls = []

            def call():
                calls.append(1)
                raise _transient_error()

            with self.assertRaises(APIConnectionError):
                call_with_retry(call, operation="test")
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.sleep.call_count, 1)

    def test_backoff_is_exponential_capped_and_jittered(self):
        with patch("app.pipeline.retry.MODEL_MAX_ATTEMPTS", 4), patch(
            "app.pipeline.retry.MODEL_RETRY_BASE_DELAY", 1.0
        ), patch("app.pipeline.retry.MODEL_RETRY_MAX_DELAY", 4.0):

            def call():
                raise _transient_error()

            with self.assertRaises(APIConnectionError):
                call_with_retry(call, operation="test")

        delays = [call.args[0] for call in self.sleep.call_args_list]
        # هر پله: بین نصف و کلِ سقف نمایی همان پله (jitter)، و هرگز بیشتر از max.
        for delay, ceiling in zip(delays, (1.0, 2.0, 4.0)):
            self.assertGreaterEqual(delay, ceiling / 2)
            self.assertLessEqual(delay, ceiling)
        self.assertEqual(delays, sorted(delays))

    def test_retry_after_header_is_respected_and_capped(self):
        error = _status_error(RateLimitError, 429)
        error.response.headers["retry-after"] = "2"  # type: ignore[union-attr]
        calls = []

        def call():
            calls.append(1)
            raise error

        with patch("app.pipeline.retry.MODEL_MAX_ATTEMPTS", 2), patch("app.pipeline.retry.MODEL_RETRY_MAX_DELAY", 8.0):
            with self.assertRaises(RateLimitError):
                call_with_retry(call, operation="test")

        self.assertEqual(self.sleep.call_args.args[0], 2.0)

    def test_generate_retries_transient_error_end_to_end(self):
        completions = FlakyCompletions(_CATALOG_JSON, _transient_error())
        with patch("app.pipeline.generate.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.generate.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=completions))
        ):
            result = generate_catalog(MergedEvidence(detected_type="کیف"))

        self.assertEqual(completions.calls, 2)
        self.assertEqual(result.title, "کیف چرمی مشکی")

    def test_generate_does_not_retry_client_error_end_to_end(self):
        completions = FlakyCompletions(_CATALOG_JSON, _status_error(AuthenticationError, 401))
        with patch("app.pipeline.generate.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.generate.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=completions))
        ):
            with self.assertRaises(EngineCallError):
                generate_catalog(MergedEvidence(detected_type="کیف"))

        self.assertEqual(completions.calls, 1)
        self.sleep.assert_not_called()


class ImageCacheTests(unittest.TestCase):
    """cache تحلیل تصویر بر اساس hash محتوای عکس."""

    def setUp(self):
        cache_dir = tempfile.TemporaryDirectory()
        self.addCleanup(cache_dir.cleanup)
        for target, value in (
            ("app.pipeline.cache.IMAGE_CACHE_DIR", cache_dir.name),
            ("app.pipeline.cache.IMAGE_CACHE_ENABLED", True),
            ("app.pipeline.cache.IMAGE_CACHE_TTL_SECONDS", 3600.0),
        ):
            patcher = patch(target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        cache.reset_stats()
        self.addCleanup(cache.reset_stats)

    def _image(self, content: bytes) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(content)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink, missing_ok=True)
        return tmp.name

    def _analyze(self, paths: list[str], completions: CountingCompletions) -> ImageAnalysis:
        with patch("app.pipeline.vision.OPENAI_API_KEY", "test-key"), patch(
            "app.pipeline.vision.OpenAI", return_value=SimpleNamespace(chat=SimpleNamespace(completions=completions))
        ):
            return analyze_images(paths)

    def test_cache_key_is_content_based_not_path_based(self):
        self.assertEqual(cache.build_key("m", "v1", [b"abc"]), cache.build_key("m", "v1", [b"abc"]))
        self.assertNotEqual(cache.build_key("m", "v1", [b"abc"]), cache.build_key("m", "v1", [b"abd"]))
        self.assertNotEqual(cache.build_key("m", "v1", [b"abc"]), cache.build_key("other-model", "v1", [b"abc"]))
        self.assertNotEqual(cache.build_key("m", "v1", [b"abc"]), cache.build_key("m", "v2", [b"abc"]))
        # مرزهای عکس‌ها هم بدون ابهام‌اند (نه صرفاً الحاق ساده‌ی بایت‌ها)
        self.assertNotEqual(cache.build_key("m", "v1", [b"ab", b"c"]), cache.build_key("m", "v1", [b"abc"]))

    def test_same_image_bytes_hit_cache_and_skip_second_model_call(self):
        completions = CountingCompletions(_VISION_JSON)
        first = self._image(b"same-image-bytes")
        second = self._image(b"same-image-bytes")  # همان محتوا، نام/مسیر متفاوت

        first_result = self._analyze([first], completions)
        second_result = self._analyze([second], completions)

        self.assertEqual(completions.calls, 1, "عکس تکراری نباید دوباره به مدل فرستاده شود")
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_result, ImageAnalysis("کیف", ["مشکی"], "چرم", []))
        self.assertEqual(cache.stats()["hits"], 1)
        self.assertEqual(cache.stats()["stores"], 1)

    def test_different_image_bytes_are_a_cache_miss(self):
        completions = CountingCompletions(_VISION_JSON)

        self._analyze([self._image(b"first-image")], completions)
        self._analyze([self._image(b"second-image")], completions)

        self.assertEqual(completions.calls, 2)
        self.assertEqual(cache.stats()["hits"], 0)
        self.assertEqual(cache.stats()["stores"], 2)

    def test_expired_entry_is_refetched_from_model(self):
        completions = CountingCompletions(_VISION_JSON)
        path = self._image(b"image-bytes")

        self._analyze([path], completions)
        with patch("app.pipeline.cache.IMAGE_CACHE_TTL_SECONDS", -1.0):  # هر ورودی منقضی است
            self._analyze([path], completions)

        self.assertEqual(completions.calls, 2)
        self.assertEqual(cache.stats()["expired"], 1)

    def test_disabled_cache_always_calls_model(self):
        completions = CountingCompletions(_VISION_JSON)
        path = self._image(b"image-bytes")

        with patch("app.pipeline.cache.IMAGE_CACHE_ENABLED", False):
            self._analyze([path], completions)
            self._analyze([path], completions)

        self.assertEqual(completions.calls, 2)
        self.assertEqual(cache.stats()["hits"], 0)

    def test_broken_cache_degrades_to_normal_call(self):
        completions = CountingCompletions(_VISION_JSON)
        blocker = self._image(b"not-a-directory")  # یک فایل که به‌جای دایرکتوری cache داده می‌شود

        with patch("app.pipeline.cache.IMAGE_CACHE_DIR", blocker):
            result = self._analyze([self._image(b"image-bytes")], completions)

        self.assertEqual(completions.calls, 1)
        self.assertEqual(result, ImageAnalysis("کیف", ["مشکی"], "چرم", []))
        self.assertGreater(cache.stats()["errors"], 0)

    def test_corrupt_cache_entry_degrades_to_normal_call(self):
        completions = CountingCompletions(_VISION_JSON)
        path = self._image(b"image-bytes")
        key = cache.build_key("gpt-4o-mini", "v1", [Path(path).read_bytes()])

        self._analyze([path], completions)  # ورودی سالم نوشته می‌شود
        Path(cache.IMAGE_CACHE_DIR, f"{key}.json").write_text("{ not json", encoding="utf-8")
        self._analyze([path], completions)

        self.assertEqual(completions.calls, 2)
        self.assertEqual(cache.stats()["hits"], 0)


if __name__ == "__main__":
    unittest.main()
