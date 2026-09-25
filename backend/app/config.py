import os
from pathlib import Path

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VISION_MODEL = os.environ.get("CATALOGYAR_VISION_MODEL", "gpt-4o-mini")
SPEECH_MODEL = os.environ.get("CATALOGYAR_SPEECH_MODEL", "whisper-1")
GENERATE_MODEL = os.environ.get("CATALOGYAR_GENERATE_MODEL", "gpt-4o-mini")
DATA_DIR = Path(os.environ.get("CATALOGYAR_DATA_DIR", "/tmp/catalogyar"))
DATABASE_PATH = Path(os.environ.get("CATALOGYAR_DATABASE_PATH", str(DATA_DIR / "catalogyar.sqlite3")))
VISION_CACHE_DIR = Path(os.environ.get("CATALOGYAR_VISION_CACHE_DIR", str(DATA_DIR / "vision-cache")))
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
