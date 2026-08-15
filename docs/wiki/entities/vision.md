# Vision

> تحلیل تصویر محصول: نوع، رنگ، جنس ظاهری، متن روی بسته‌بندی.

## مسئولیت‌ها
- `analyze_images(image_paths) -> ImageAnalysis` — قدم اول pipeline.
- `ImageAnalysis` dataclass: `detected_type`, `colors`, `material_guess`, `text_on_package`.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — اولین مرحله؛ `ImageAnalysis` ورودی مرحله‌ی merge است

## قراردادها / Edge cases
- فعلاً `NotImplementedError` — پشت یک interface ساده تا در فاز پیاده‌سازی به مدل چندوجهی
  واقعی (vision model) وصل شود. این تصمیم عمدی معماری MVP است، نه باگ.

## منابع کد
- `backend/app/pipeline/vision.py:18` — `analyze_images`
- `backend/app/pipeline/vision.py:11` — `ImageAnalysis`
