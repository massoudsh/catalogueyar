"""تحلیل تصویر محصول با یک مدل چندوجهی (vision): تشخیص نوع، رنگ، جنس ظاهری و متن روی بسته‌بندی."""

import base64
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, VISION_MODEL
from app.pipeline import cache
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.retry import call_with_retry

logger = logging.getLogger(__name__)

# با هر تغییر معنادار در پرامپت یا ساختار خروجی این نسخه را بامپ کن؛ چون بخشی از کلید cache است،
# ورودی‌های قدیمی خودکار miss می‌شوند (invalidasyon بدون پاک‌کردن دستی).
_ANALYSIS_CACHE_VERSION = "v1"


@dataclass
class ImageAnalysis:
    detected_type: str | None = None
    colors: list[str] = field(default_factory=list)
    material_guess: str | None = None
    text_on_package: list[str] = field(default_factory=list)


_SYSTEM_PROMPT = (
    "تو یک تحلیل‌گر تصویر محصول برای یک بازار آنلاین ایرانی هستی. "
    "فقط بر اساس آنچه واقعاً در عکس‌ها دیده می‌شود پاسخ بده و حدس بی‌پایه نزن؛ "
    "اگر چیزی از عکس مشخص نیست مقدار آن را null یا لیست خالی بگذار. "
    "خروجی را دقیقاً و فقط به‌صورت یک JSON با همین کلیدها برگردان:\n"
    '{"detected_type": "نوع محصول یا null", '
    '"colors": ["رنگ‌های اصلی قابل مشاهده"], '
    '"material_guess": "حدس جنس ظاهری یا null", '
    '"text_on_package": ["متن‌های خوانا روی بسته‌بندی یا برچسب، در صورت وجود"]}'
)


def _image_to_data_url(data: bytes, path: str) -> str:
    suffix = Path(path).suffix.lstrip(".").lower() or "jpeg"
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
    return f"data:image/{mime};base64,{base64.b64encode(data).decode('ascii')}"


def analyze_images(image_paths: list[str]) -> ImageAnalysis:
    """عکس‌های محصول را با مدل vision تحلیل کرده و شواهد بصری برمی‌گرداند.

    نیازمند متغیر محیطی ``OPENAI_API_KEY``. نام مدل با ``CATALOGYAR_VISION_MODEL``
    قابل تغییر است (پیش‌فرض: ``gpt-4o-mini``).

    نتیجه بر اساس hash محتوای عکس‌ها cache می‌شود ([[concepts/engine-config]]) تا عکس تکراری
    دوباره به مدل فرستاده نشود؛ خطای cache فقط لاگ می‌شود و به فراخوانی عادی مدل برمی‌گردد.
    فراخوانی مدل با retry/backoff (فقط روی خطای موقت) انجام می‌شود.
    """
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان تصویر را تحلیل کرد"
        )

    # هر فایل فقط یک‌بار خوانده می‌شود: هم برای hash محتوا، هم برای ساخت data URL.
    images = [(path, Path(path).read_bytes()) for path in image_paths]
    cache_key = cache.build_key(VISION_MODEL, _ANALYSIS_CACHE_VERSION, [data for _, data in images])

    cached_payload = cache.get(cache_key)
    if cached_payload is not None:
        try:
            return ImageAnalysis(**cached_payload)
        except TypeError as exc:
            logger.warning("ورودی cache با schema فعلی تحلیل تصویر نمی‌خواند، نادیده گرفته شد: %s", exc)

    content: list[dict] = [{"type": "text", "text": "این عکس‌های محصول را تحلیل کن."}]
    for path, data in images:
        content.append({"type": "image_url", "image_url": {"url": _image_to_data_url(data, path)}})

    client = OpenAI(api_key=OPENAI_API_KEY)

    def _call_model() -> str:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content or "{}"

    try:
        raw = call_with_retry(_call_model, operation="vision")
        data = json.loads(raw)
    except (OpenAIError, json.JSONDecodeError) as exc:
        raise EngineCallError(f"خطا در تحلیل تصویر: {exc}") from exc

    analysis = ImageAnalysis(
        detected_type=data.get("detected_type"),
        colors=list(data.get("colors") or []),
        material_guess=data.get("material_guess"),
        text_on_package=list(data.get("text_on_package") or []),
    )
    cache.put(cache_key, asdict(analysis))
    return analysis
