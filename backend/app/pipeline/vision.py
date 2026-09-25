import base64
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, VISION_MODEL
from app.pipeline.cache import cache_key, read_cache, write_cache
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.retry import with_retry


@dataclass
class ImageAnalysis:
    detected_type: str | None = None
    colors: list[str] = field(default_factory=list)
    material_guess: str | None = None
    text_on_package: list[str] = field(default_factory=list)


_SYSTEM_PROMPT = (
    "تو یک تحلیل‌گر تصویر محصول برای یک بازار آنلاین ایرانی هستی. "
    "رنگ‌های اصلی قابل مشاهده در همه عکس‌ها را جداگانه استخراج کن تا اگر محصول در چند رنگ دیده شد به‌عنوان variant استفاده شود. "
    "فقط بر اساس آنچه واقعاً در عکس‌ها دیده می‌شود پاسخ بده و حدس بی‌پایه نزن. "
    "خروجی را دقیقاً و فقط به‌صورت یک JSON با همین کلیدها برگردان:\n"
    '{"detected_type": "نوع محصول یا null", '
    '"colors": ["رنگ‌های اصلی قابل مشاهده"], '
    '"material_guess": "حدس جنس ظاهری یا null", '
    '"text_on_package": ["متن‌های خوانا روی بسته‌بندی یا برچسب، در صورت وجود"]}'
)


def _image_to_data_url(path: str) -> str:
    suffix = Path(path).suffix.lstrip(".").lower() or "jpeg"
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{data}"


def _parse_analysis(data: dict) -> ImageAnalysis:
    return ImageAnalysis(
        detected_type=data.get("detected_type"),
        colors=list(dict.fromkeys(data.get("colors") or [])),
        material_guess=data.get("material_guess"),
        text_on_package=list(data.get("text_on_package") or []),
    )


def analyze_images(image_paths: list[str]) -> ImageAnalysis:
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان تصویر را تحلیل کرد"
        )

    key = cache_key(image_paths)
    cached = read_cache(key)
    if cached is not None:
        return _parse_analysis(cached)

    content: list[dict] = [{"type": "text", "text": "این عکس‌های محصول را تحلیل کن."}]
    for path in image_paths:
        content.append({"type": "image_url", "image_url": {"url": _image_to_data_url(path)}})

    client = OpenAI(api_key=OPENAI_API_KEY)

    def call_model():
        return client.chat.completions.create(
            model=VISION_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        )

    try:
        response = with_retry(call_model)
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
    except (OpenAIError, json.JSONDecodeError, OSError) as exc:
        raise EngineCallError(f"خطا در تحلیل تصویر: {exc}") from exc

    analysis = _parse_analysis(data)
    write_cache(key, asdict(analysis))
    return analysis
