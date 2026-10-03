import os
from pathlib import Path

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VISION_MODEL = os.environ.get("CATALOGYAR_VISION_MODEL", "gpt-4o-mini")
SPEECH_MODEL = os.environ.get("CATALOGYAR_SPEECH_MODEL", "whisper-1")
GENERATE_MODEL = os.environ.get("CATALOGYAR_GENERATE_MODEL", "gpt-4o-mini")
DATA_DIR = Path(os.environ.get("CATALOGYAR_DATA_DIR", "/tmp/catalogyar"))
DATABASE_PATH = Path(os.environ.get("CATALOGYAR_DATABASE_PATH", str(DATA_DIR / "catalogyar.sqlite3")))
# مسیر cache vision: IMAGE_CACHE_DIR جدید؛ VISION_CACHE_DIR برای سازگاری با env/تست قدیمی.
VISION_CACHE_DIR = Path(
    os.environ.get("CATALOGYAR_IMAGE_CACHE_DIR")
    or os.environ.get("CATALOGYAR_VISION_CACHE_DIR")
    or str(DATA_DIR / "vision-cache")
)
API_KEYS = os.environ.get("CATALOGYAR_API_KEYS", "")
RATE_LIMIT_PER_MINUTE = int(os.environ.get("CATALOGYAR_RATE_LIMIT_PER_MINUTE", "30"))
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("CATALOGYAR_REQUEST_TIMEOUT_SECONDS", "12"))
MARKETPLACE_ENDPOINTS = {
    "digikala": os.environ.get("DIGIKALA_PUBLISH_URL"),
    "basalam": os.environ.get("BASALAM_PUBLISH_URL"),
    "torob": os.environ.get("TOROB_PUBLISH_URL"),
}
MARKETPLACE_TOKENS = {
    "digikala": os.environ.get("DIGIKALA_TOKEN"),
    "basalam": os.environ.get("BASALAM_TOKEN"),
    "torob": os.environ.get("TOROB_TOKEN"),
}

# --- Retry/backoff فراخوانی مدل ---
MODEL_MAX_ATTEMPTS = int(os.environ.get("CATALOGYAR_MODEL_MAX_ATTEMPTS", "3"))
MODEL_RETRY_BASE_DELAY = float(os.environ.get("CATALOGYAR_MODEL_RETRY_BASE_DELAY", "0.5"))
MODEL_RETRY_MAX_DELAY = float(os.environ.get("CATALOGYAR_MODEL_RETRY_MAX_DELAY", "8.0"))

# --- Cache تحلیل تصویر ---
IMAGE_CACHE_ENABLED = os.environ.get("CATALOGYAR_IMAGE_CACHE_ENABLED", "1").strip().lower() not in (
    "0",
    "false",
    "no",
)
IMAGE_CACHE_DIR = str(VISION_CACHE_DIR)
IMAGE_CACHE_TTL_SECONDS = float(os.environ.get("CATALOGYAR_IMAGE_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60)))
