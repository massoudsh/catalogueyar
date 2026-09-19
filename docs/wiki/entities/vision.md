# Vision

> تحلیل تصویر محصول: نوع، رنگ، جنس ظاهری، متن روی بسته‌بندی.

## مسئولیت‌ها
- `analyze_images(image_paths) -> ImageAnalysis` — قدم اول pipeline.
- `ImageAnalysis` dataclass: `detected_type`, `colors`, `material_guess`, `text_on_package`.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — اولین مرحله؛ `ImageAnalysis` ورودی مرحله‌ی merge است
- [[concepts/engine-config]] — `OPENAI_API_KEY`، `CATALOGYAR_VISION_MODEL`، تنظیمات retry و cache
- `backend/app/pipeline/retry.py` — فراخوانی مدل از `call_with_retry` رد می‌شود
- `backend/app/pipeline/cache.py` — cache نتیجه بر اساس hash محتوای عکس‌ها

## قراردادها / Edge cases
- عکس‌ها به data URL (base64) تبدیل و در یک پیام چندبخشی به مدل vision فرستاده می‌شوند. هر فایل
  فقط یک‌بار خوانده می‌شود (هم برای hash، هم برای data URL).
- **Cache**: قبل از فراخوانی مدل، کلید از SHA-256 محتوای عکس‌ها + نام مدل + `_ANALYSIS_CACHE_VERSION`
  ساخته و cache چک می‌شود؛ hit یعنی هیچ درخواستی به مدل نمی‌رود (لاگ `cache hit` + شمارنده‌ی
  `cache.stats()`). نتیجه‌ی موفق بعد از فراخوانی ذخیره می‌شود. بامپ `_ANALYSIS_CACHE_VERSION` تنها
  راه invalidate کردن دستی هنگام تغییر پرامپت/ساختار خروجی است.
- ترتیب عکس‌ها در کلید cache می‌آید: `[a, b]` با `[b, a]` یکسان حساب نمی‌شود (عکس اول/main photo
  معنادار است). نام و مسیر فایل در کلید اثر ندارد؛ تنها چیزی که از مسیر به مدل می‌رود پسوند فایل
  است (mime در data URL) که عمداً در کلید نیامده — دو فایل با بایت یکسان ولی پسوند متفاوت همان
  نتیجه را می‌گیرند (پیکسل‌ها یکسان است).
- ورودی cache خراب یا ناخوانا → warning و برگشت به فراخوانی عادی مدل (نه خطا به کاربر).
- خروجی مدل باید JSON خالص باشد (`response_format=json_object`)؛ JSON نامعتبر **retry نمی‌شود** و
  مستقیم `EngineCallError` می‌دهد.
- خطای موقت شبکه/`429`/`5xx` تا `CATALOGYAR_MODEL_MAX_ATTEMPTS` بار با backoff دوباره تلاش می‌شود؛
  خطای `4xx` کلاینت یک‌بار. در نهایت (بعد از تمام‌شدن تلاش‌ها) `EngineCallError` می‌دهد.
- بدون `OPENAI_API_KEY` بلافاصله `EngineNotConfiguredError` می‌دهد (بدون فراخوانی شبکه، و قبل از
  چک کردن cache).

## منابع کد
- `backend/app/pipeline/vision.py:49` — `analyze_images`
- `backend/app/pipeline/vision.py:23` — `ImageAnalysis`
- `backend/app/pipeline/vision.py:20` — `_ANALYSIS_CACHE_VERSION`
