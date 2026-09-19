"""رونویسی ویس فارسی فروشنده به متن با یک مدل speech-to-text."""

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, SPEECH_MODEL
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.retry import call_with_retry


def transcribe_voice(audio_path: str) -> str:
    """فایل صوتی فارسی را به متن تبدیل می‌کند.

    نیازمند متغیر محیطی ``OPENAI_API_KEY``. نام مدل با ``CATALOGYAR_SPEECH_MODEL``
    قابل تغییر است (پیش‌فرض: ``whisper-1``). فراخوانی مدل با retry/backoff
    (فقط روی خطای موقت شبکه/``429``/``5xx``) انجام می‌شود.
    """
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان ویس را رونویسی کرد"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    def _call_model() -> str:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=SPEECH_MODEL,
                file=audio_file,
                language="fa",
            )
        return transcript.text.strip()

    try:
        return call_with_retry(_call_model, operation="speech")
    except OpenAIError as exc:
        raise EngineCallError(f"خطا در رونویسی ویس: {exc}") from exc
