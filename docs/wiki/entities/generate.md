# Generate

> تولید خروجی نهایی و ساختاریافته‌ی کاتالوگ از شواهد ادغام‌شده.

## مسئولیت‌ها
- `generate_catalog(evidence: MergedEvidence, category_list=None) -> CatalogGenerateResponse`
- آخرین مرحله‌ی pipeline؛ عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها و سؤالات تکمیلی را می‌سازد.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — مرحله‌ی چهارم/آخر
- [[entities/catalog-schemas]] — همین schema `CatalogGenerateResponse` را پر می‌کند

## قراردادها / Edge cases
- فعلاً `NotImplementedError` — پشت interface ساده تا به مدل زبانی واقعی (تولید متن ساختاریافته
  فارسی) وصل شود؛ قدم بعدی پروژه دقیقاً همین اتصال است.

## منابع کد
- `backend/app/pipeline/generate.py:20` — `generate_catalog`
