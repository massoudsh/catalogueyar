# Vision

> تحلیل تصویر محصول: نوع، رنگ، جنس ظاهری، متن روی بسته‌بندی.

## مسئولیت‌ها
- `analyze_images(image_paths) -> ImageAnalysis` — قدم vision در pipeline.
- `ImageAnalysis` dataclass: `detected_type`, `colors`, `material_guess`, `text_on_package`.
- رنگ‌ها با `dict.fromkeys` یکتا می‌شوند تا برای variants چندرنگ آماده باشند.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — بعد از [[entities/video]]؛ خروجی وارد merge می‌شود
- [[concepts/engine-config]] — `OPENAI_API_KEY`, `CATALOGYAR_VISION_MODEL`, cache dir, retry
- `backend/app/pipeline/retry.py` — `with_retry` دور فراخوانی مدل
- `backend/app/pipeline/cache.py` — `cache_key` / `read_cache` / `write_cache`

## قراردادها / Edge cases
- کلید cache = SHA-256 از digestهای SHA-256 محتوای فایل‌ها با **مسیرهای sorted**؛ ترتیب آپلود در
  کلید اثر ندارد. نام مدل در کلید نیست.
- hit → بدون فراخوانی مدل، `_parse_analysis` روی JSON دیسک.
- miss موفق → `write_cache` اتمیک (`.tmp` + `os.replace`) زیر `CATALOGYAR_VISION_CACHE_DIR`.
- TTL/enable-flag جداگانه ندارد؛ پاک‌سازی دستی یا عوض کردن dir.
- خروجی باید JSON باشد؛ JSON نامعتبر یا خطای OpenAI → `EngineCallError`.
- خطای موقت (`APIConnectionError` / `APITimeoutError` / `RateLimitError` / timeout سیستمی) تا
  ۳ بار با backoff نمایی (`with_retry`) تکرار می‌شود.
- بدون `OPENAI_API_KEY` → `EngineNotConfiguredError` قبل از مدل.

## منابع کد
- `backend/app/pipeline/vision.py` — `analyze_images`, `ImageAnalysis`
- `backend/app/pipeline/cache.py` — cache دیسکی
