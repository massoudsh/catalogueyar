"""تنظیمات موتور هوش مصنوعی — همه از متغیر محیطی خوانده می‌شوند، هیچ کلیدی در کد نیست."""

import os
from pathlib import Path

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VISION_MODEL = os.environ.get("CATALOGYAR_VISION_MODEL", "gpt-4o-mini")
SPEECH_MODEL = os.environ.get("CATALOGYAR_SPEECH_MODEL", "whisper-1")
GENERATE_MODEL = os.environ.get("CATALOGYAR_GENERATE_MODEL", "gpt-4o-mini")

# --- Retry/backoff فراخوانی مدل (issue #1) ---
# تعداد کل تلاش‌ها (تلاش اول + تلاش‌های دوباره) — هرگز بی‌نهایت نیست.
MODEL_MAX_ATTEMPTS = int(os.environ.get("CATALOGYAR_MODEL_MAX_ATTEMPTS", "3"))
# تأخیر پایه‌ی backoff نمایی (ثانیه) و سقف آن.
MODEL_RETRY_BASE_DELAY = float(os.environ.get("CATALOGYAR_MODEL_RETRY_BASE_DELAY", "0.5"))
MODEL_RETRY_MAX_DELAY = float(os.environ.get("CATALOGYAR_MODEL_RETRY_MAX_DELAY", "8.0"))

# --- Cache تحلیل تصویر بر اساس hash محتوا (issue #2) ---
_BACKEND_ROOT = Path(__file__).resolve().parents[1]

# خاموش کردن cache با CATALOGYAR_IMAGE_CACHE_ENABLED=0.
IMAGE_CACHE_ENABLED = os.environ.get("CATALOGYAR_IMAGE_CACHE_ENABLED", "1").strip().lower() not in (
    "0",
    "false",
    "no",
)
# محل ذخیره‌ی cache روی دیسک (پیش‌فرض: backend/.cache/image-analysis).
IMAGE_CACHE_DIR = os.environ.get("CATALOGYAR_IMAGE_CACHE_DIR") or str(_BACKEND_ROOT / ".cache" / "image-analysis")
# TTL ورودی‌های cache؛ بعد از این مدت، ورودی کهنه محسوب و دوباره از مدل گرفته می‌شود (پیش‌فرض ۷ روز).
IMAGE_CACHE_TTL_SECONDS = float(os.environ.get("CATALOGYAR_IMAGE_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60)))
