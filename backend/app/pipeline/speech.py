from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, SPEECH_MODEL
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.retry import with_retry


def transcribe_voice(audio_path: str) -> str:
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان ویس را رونویسی کرد"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    def call_model():
        with open(audio_path, "rb") as audio_file:
            return client.audio.transcriptions.create(
                model=SPEECH_MODEL,
                file=audio_file,
                language="fa",
            )

    try:
        transcript = with_retry(call_model)
    except (OpenAIError, OSError) as exc:
        raise EngineCallError(f"خطا در رونویسی ویس: {exc}") from exc

    return transcript.text.strip()
