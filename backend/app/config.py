"""تنظیمات موتور هوش مصنوعی — همه از متغیر محیطی خوانده می‌شوند، هیچ کلیدی در کد نیست."""

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VISION_MODEL = os.environ.get("CATALOGYAR_VISION_MODEL", "gpt-4o-mini")
SPEECH_MODEL = os.environ.get("CATALOGYAR_SPEECH_MODEL", "whisper-1")
GENERATE_MODEL = os.environ.get("CATALOGYAR_GENERATE_MODEL", "gpt-4o-mini")
