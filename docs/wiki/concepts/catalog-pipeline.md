# Catalog Pipeline

> فلوی پردازش چندمرحله‌ای که از عکس/ویس فروشنده به خروجی ساختاریافته‌ی کاتالوگ می‌رسد.

## مراحل (فعلی: ۴ تابع خالص، بدون اتصال واقعی به مدل)
1. **vision** — [[entities/vision]] `analyze_images(image_paths) -> ImageAnalysis`
2. **speech** (اختیاری) — [[entities/speech]] `transcribe_voice(audio_path) -> str`
3. **merge** — `backend/app/pipeline/merge.py:18` `merge_evidence(image_analysis, voice_transcript, seller_hint) -> MergedEvidence`
   شواهد سه‌منبعی (تصویر + صدا + راهنمای متنی فروشنده) را در یک ساختار واحد جمع می‌کند. تنها
   مرحله‌ای که همین الان کاملاً پیاده‌سازی شده (بدون نیاز به مدل خارجی، صرفاً map کردن فیلدها).
4. **generate** — [[entities/generate]] `generate_catalog(evidence, category_list) -> CatalogGenerateResponse`

## اتصال به API
[[entities/catalog-router]] در حال حاضر این pipeline را صدا نمی‌زند (endpoint همیشه `501`
برمی‌گرداند). قدم بعدی پروژه: در `generate_catalog_endpoint` فایل‌های آپلودی را ذخیره‌ی موقت کرده،
این ۴ مرحله را پشت‌سرهم صدا بزند و خروجی `generate_catalog` را برگرداند.

## چرا این ساختار
هر مرحله پشت یک interface ساده (تابع خالص با ورودی/خروجی مشخص) قرار دارد تا اتصال به مدل
چندوجهی/گفتار فارسی واقعی در فاز پیاده‌سازی، بدون تغییر ساختار API انجام شود.

## منابع کد
- `backend/app/pipeline/merge.py` — تنها پیاده‌سازی کامل فعلی
- `docs/mvp-design.md` — طراحی اصلی pipeline ۷ مرحله‌ای (نسخه‌ی کامل‌تر آینده)
