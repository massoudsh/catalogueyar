# Engine Config

> تنظیمات مشترک موتور هوش مصنوعی (کلید API، نام مدل‌ها) و خطاهای مشترک بین سه مرحله‌ی
> مدل‌محور pipeline ([[entities/vision]], [[entities/speech]], [[entities/generate]]).

## `backend/app/config.py`
همه از env var خوانده می‌شود، هیچ کلیدی در کد نیست:
- `OPENAI_API_KEY` — بدون این، هر سه مرحله بلافاصله `EngineNotConfiguredError` می‌دهند.
- `CATALOGYAR_VISION_MODEL` (پیش‌فرض `gpt-4o-mini`)
- `CATALOGYAR_SPEECH_MODEL` (پیش‌فرض `whisper-1`)
- `CATALOGYAR_GENERATE_MODEL` (پیش‌فرض `gpt-4o-mini`)

نمونه در `backend/.env.example`.

## `backend/app/pipeline/errors.py`
- `EngineNotConfiguredError(RuntimeError)` — کلید/تنظیمات مدل مقداردهی نشده. [[entities/catalog-router]] این را به `503` map می‌کند.
- `EngineCallError(RuntimeError)` — فراخوانی مدل بیرونی fail شد (شبکه، خطای provider، JSON نامعتبر). به `502` map می‌شود.

## چرا این جداسازی
هر سه ماژول مدل‌محور همین دو خطا و همین سه تنظیم را به‌صورت یکسان استفاده می‌کنند؛ به‌جای
تکرار در هر فایل، یک نقطه‌ی مشترک برای تغییر provider یا رفتار خطا وجود دارد.

## منابع کد
- `backend/app/config.py`
- `backend/app/pipeline/errors.py`
