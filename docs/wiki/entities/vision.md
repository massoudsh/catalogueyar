# Vision

> تحلیل تصویر محصول: نوع، رنگ، جنس ظاهری، متن روی بسته‌بندی.

## مسئولیت‌ها
- `analyze_images(image_paths) -> ImageAnalysis` — قدم vision در pipeline.
- `ImageAnalysis` dataclass: `detected_type`, `colors`, `material_guess`, `text_on_package`.
- رنگ‌ها با `dict.fromkeys` یکتا می‌شوند تا برای variants چندرنگ آماده باشند.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — بعد از [[entities/video]]؛ خروجی وارد merge می‌شود
- [[concepts/engine-config]] — `OPENAI_API_KEY`, `CATALOGYAR_VISION_MODEL`, cache dir/TTL/enable, retry
- `backend/app/pipeline/retry.py` — `call_with_retry` دور `chat.completions.create`
- `backend/app/pipeline/cache.py` — `build_key` / `get` / `put` / `invalidate`

## قراردادها / Edge cases
- هر فایل یک‌بار خوانده می‌شود (هم برای hash محتوا، هم برای data URL).
- کلید cache = SHA-256 از digest محتوای عکس‌ها + نام مدل + `_ANALYSIS_CACHE_VERSION`؛
  ترتیب آپلود در کلید اثر دارد؛ نام/مسیر فایل نه.
- hit → بدون فراخوانی مدل؛ اگر payload با schema فعلی نخواند → `invalidate` + miss.
- miss موفق → `put` اتمیک (temp + `os.replace`) زیر
  `CATALOGYAR_IMAGE_CACHE_DIR` / `CATALOGYAR_VISION_CACHE_DIR`.
- TTL پیش‌فرض ۷ روز (`CATALOGYAR_IMAGE_CACHE_TTL_SECONDS`)؛
  `CATALOGYAR_IMAGE_CACHE_ENABLED=0` cache را خاموش می‌کند.
- خروجی باید JSON باشد؛ JSON نامعتبر یا خطای OpenAI → `EngineCallError`.
- خطای موقت فقط از طریق `call_with_retry` (شبکه / `429` / `5xx` / `408`) تکرار می‌شود.
- بدون `OPENAI_API_KEY` → `EngineNotConfiguredError` قبل از مدل.

## منابع کد
- `backend/app/pipeline/vision.py` — `analyze_images`, `ImageAnalysis`, `_ANALYSIS_CACHE_VERSION`
- `backend/app/pipeline/cache.py` — cache دیسکی با TTL
