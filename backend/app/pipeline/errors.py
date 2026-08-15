"""خطاهای مشترک موتور هوش مصنوعی pipeline."""


class EngineNotConfiguredError(RuntimeError):
    """کلید/تنظیمات مدل هنوز مقداردهی نشده (مثلاً OPENAI_API_KEY خالی است)."""


class EngineCallError(RuntimeError):
    """فراخوانی مدل بیرونی (vision/speech/generate) با خطا مواجه شد."""
