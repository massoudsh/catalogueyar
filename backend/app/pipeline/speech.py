"""رونویسی ویس فارسی فروشنده به متن با یک مدل speech-to-text."""

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, SPEECH_MODEL
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError


def transcribe_voice(audio_path: str) -> str:
    """فایل صوتی فارسی را به متن تبدیل می‌کند.

    نیازمند متغیر محیطی ``OPENAI_API_KEY``. نام مدل با ``CATALOGYAR_SPEECH_MODEL``
    قابل تغییر است (پیش‌فرض: ``whisper-1``).
    """
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان ویس را رونویسی کرد"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=SPEECH_MODEL,
                file=audio_file,
                language="fa",
            )
    except OpenAIError as exc:
        raise EngineCallError(f"خطا در رونویسی ویس: {exc}") from exc

    return transcript.text.strip()
