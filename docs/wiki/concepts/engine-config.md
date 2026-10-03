# Engine Config

> تنظیمات مشترک موتور هوش مصنوعی (کلید API، نام مدل‌ها، retry/backoff، cache) و خطاهای مشترک بین
> سه مرحله‌ی مدل‌محور pipeline ([[entities/vision]], [[entities/speech]], [[entities/generate]]).

## `backend/app/config.py`
همه از env var خوانده می‌شود، هیچ کلیدی در کد نیست:
- `OPENAI_API_KEY` — بدون این، هر سه مرحله بلافاصله `EngineNotConfiguredError` می‌دهند.
- `CATALOGYAR_VISION_MODEL` (پیش‌فرض `gpt-4o-mini`)
- `CATALOGYAR_SPEECH_MODEL` (پیش‌فرض `whisper-1`)
- `CATALOGYAR_GENERATE_MODEL` (پیش‌فرض `gpt-4o-mini`)
- `CATALOGYAR_MODEL_MAX_ATTEMPTS` (پیش‌فرض `3`) — تعداد کل تلاش‌های فراخوانی مدل (شامل تلاش اول)؛
  هرگز بی‌نهایت نیست، `1` یعنی بدون retry.
- `CATALOGYAR_MODEL_RETRY_BASE_DELAY` (پیش‌فرض `0.5` ثانیه) و `CATALOGYAR_MODEL_RETRY_MAX_DELAY`
  (پیش‌فرض `8.0` ثانیه) — کف و سقف backoff نمایی.
- `CATALOGYAR_IMAGE_CACHE_ENABLED` (پیش‌فرض `1`؛ `0` = خاموش)
- `CATALOGYAR_IMAGE_CACHE_DIR` (پیش‌فرض `backend/.cache/image-analysis`؛ در `.gitignore` هست)
- `CATALOGYAR_IMAGE_CACHE_TTL_SECONDS` (پیش‌فرض `604800` = ۷ روز)

نمونه در `backend/.env.example`.

## `backend/app/pipeline/errors.py`
- `EngineNotConfiguredError(RuntimeError)` — کلید/تنظیمات مدل مقداردهی نشده. [[entities/catalog-router]] این را به `503` map می‌کند.
- `EngineCallError(RuntimeError)` — فراخوانی مدل بیرونی fail شد (شبکه، خطای provider، JSON نامعتبر). به `502` map می‌شود.

## `backend/app/pipeline/retry.py` — retry/backoff فراخوانی مدل
- `call_with_retry(call, operation=...)` نقطه‌ی مشترک فراخوانی مدل در هر سه مرحله است؛ کلاینت
  ساخته می‌شود و فقط `create(...)` داخل retry می‌رود (نه کل تابع مرحله).
- فقط خطای **موقت** دوباره تلاش می‌شود: `APIConnectionError`/`APITimeoutError`، `RateLimitError` (429)،
  `5xx`، و `ConnectionError`/`TimeoutError` سیستمی. خطای `4xx` کلاینت (مثل `400`/`401`/`403`) و
  خطای برنامه (مثل JSON نامعتبر مدل) **یک‌بار** اجرا و بلافاصله بالا می‌رود.
- تأخیر نمایی با jitter (هر پله بین نصف و کل سقف همان پله)؛ اگر provider هدر `Retry-After` بدهد،
  همان مقدار (سقف‌دار با max delay) استفاده می‌شود.
- بعد از تمام‌شدن تلاش‌ها، **همان خطای اصلی** دوباره raise می‌شود؛ پس map شدن خطا به `502`/`503`
  در [[entities/catalog-router]] دست‌نخورده می‌ماند. هر تلاش دوباره با `logger.warning` لاگ می‌شود.

## `backend/app/pipeline/cache.py` — cache تحلیل تصویر
- کلید = SHA-256 **بایت‌های عکس‌ها** + نام مدل + نسخه‌ی schema (`_ANALYSIS_CACHE_VERSION` در
  [[entities/vision]])؛ نام/مسیر فایل در کلید نمی‌آید، پس همان عکس با اسم دیگر hit می‌شود.
  ترتیب عکس‌ها بخشی از کلید است (عکس اولِ ست عکس معنادار است).
- Backend: فایل JSON روی دیسک — این ریپو نه Redis دارد نه DB. نوشتن اتمیک (temp + `os.replace`).
- Invalidation: TTL (پیش‌فرض ۷ روز) — ورودی کهنه در اولین خواندن بعدی حذف می‌شود؛ تغییر نام مدل
  یا بامپ `_ANALYSIS_CACHE_VERSION` هم چون در کلید می‌آید، ورودی‌های قدیمی را خودکار miss می‌کند.
- **Graceful degradation**: هر خطای I/O (دایرکتوری نبود، ورودی خراب، دیسک پر) فقط warning لاگ
  می‌شود و مسیر عادی (فراخوانی مدل) ادامه پیدا می‌کند — cache هرگز درخواست را fail نمی‌کند.
- Observability: هر hit/miss/expire یک خط لاگ دارد و `cache.stats()` شمارنده‌های
  `hits/misses/stores/expired/errors` را برمی‌گرداند (in-process؛ با چند worker هر worker جدا).

## چرا این جداسازی
هر سه ماژول مدل‌محور همین دو خطا و همین تنظیم‌ها را به‌صورت یکسان استفاده می‌کنند؛ به‌جای
تکرار در هر فایل، یک نقطه‌ی مشترک برای تغییر provider یا رفتار خطا وجود دارد. retry و cache هم
به همین دلیل در دو ماژول مشترک‌اند، نه کپی‌شده در هر مرحله.

## چطور تأیید کنیم که کار می‌کند
- **cache**: همان عکس را دو بار از `POST /catalog/generate` بفرست → در لاگ uvicorn خط
  `image-analysis cache hit key=...` می‌آید، `cache.stats()["hits"]` بالا می‌رود و درخواست دوم
  هزینه‌ی مدل ندارد. در تست‌ها `ImageCacheTests` (مثلاً
  `test_same_image_bytes_hit_cache_and_skip_second_model_call` فراخوانی مدل را می‌شمارد).
- **retry**: `RetryTests` خطای موقت (500/429/قطعی شبکه) را mock می‌کند و تعداد تلاش/تأخیرها را
  می‌سنجد؛ در محیط واقعی هر تلاش دوباره با `logger.warning` («فراخوانی vision ناموفق بود (تلاش
  ۱/۳)») دیده می‌شود. با `CATALOGYAR_MODEL_MAX_ATTEMPTS=1` می‌توان retry را کامل خاموش کرد.

## منابع کد
- `backend/app/config.py`
- `backend/app/pipeline/errors.py`
- `backend/app/pipeline/retry.py:64` — `call_with_retry`
- `backend/app/pipeline/retry.py:32` — `is_transient` (تفکیک خطای موقت از خطای کلاینت)
- `backend/app/pipeline/cache.py:52` — `build_key`
- `backend/app/pipeline/cache.py:68` — `get`
- `backend/app/pipeline/cache.py:103` — `put`
