# Vision

> تحلیل تصویر محصول: نوع، رنگ، جنس ظاهری، متن روی بسته‌بندی.

## مسئولیت‌ها
- `analyze_images(image_paths) -> ImageAnalysis` — قدم اول pipeline.
- `ImageAnalysis` dataclass: `detected_type`, `colors`, `material_guess`, `text_on_package`.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — اولین مرحله؛ `ImageAnalysis` ورودی مرحله‌ی merge است
- [[concepts/engine-config]] — `OPENAI_API_KEY` و `CATALOGYAR_VISION_MODEL`

## قراردادها / Edge cases
- عکس‌ها به data URL (base64) تبدیل و در یک پیام چندبخشی به مدل vision فرستاده می‌شوند.
- خروجی مدل باید JSON خالص باشد (`response_format=json_object`)؛ در صورت JSON نامعتبر یا خطای
  شبکه، `EngineCallError` می‌دهد.
- بدون `OPENAI_API_KEY` بلافاصله `EngineNotConfiguredError` می‌دهد (بدون فراخوانی شبکه).

## منابع کد
- `backend/app/pipeline/vision.py:18` — `analyze_images`
- `backend/app/pipeline/vision.py:11` — `ImageAnalysis`
