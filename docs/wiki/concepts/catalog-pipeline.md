# Catalog Pipeline

> فلوی پردازش چندمرحله‌ای که از عکس/ویس فروشنده به خروجی ساختاریافته‌ی کاتالوگ می‌رسد.

## مراحل (۴ تابع، ۳ تا از آن‌ها الان یک مدل واقعی صدا می‌زنند)
1. **vision** — [[entities/vision]] `analyze_images(image_paths) -> ImageAnalysis` (مدل vision واقعی)
2. **speech** (اختیاری) — [[entities/speech]] `transcribe_voice(audio_path) -> str` (مدل speech-to-text واقعی)
3. **merge** — `backend/app/pipeline/merge.py:18` `merge_evidence(image_analysis, voice_transcript, seller_hint) -> MergedEvidence`
   شواهد سه‌منبعی (تصویر + صدا + راهنمای متنی فروشنده) را در یک ساختار واحد جمع می‌کند. تنها
   مرحله‌ای که بدون فراخوانی مدل خارجی کار می‌کند (صرفاً map کردن فیلدها).
4. **generate** — [[entities/generate]] `generate_catalog(evidence, category_list) -> CatalogGenerateResponse` (مدل زبانی واقعی)

## اتصال به API
[[entities/catalog-router]] این ۴ مرحله را پشت‌سرهم صدا می‌زند: فایل‌های آپلودی موقت ذخیره،
pipeline اجرا، و در `finally` فایل‌های موقت پاک می‌شوند. خطاهای موتور (کلید نبود/فراخوانی fail شد)
در [[concepts/engine-config]] به کد HTTP مناسب (`503`/`502`) map می‌شوند.

## چرا این ساختار
هر مرحله پشت یک interface ساده (تابع خالص با ورودی/خروجی مشخص) قرار دارد تا اتصال به مدل
چندوجهی/گفتار فارسی واقعی در فاز پیاده‌سازی، بدون تغییر ساختار API انجام شود.

## آزمون‌پذیری
`backend/tests/test_pipeline.py` با mock کردن OpenAI، قرارداد ساختاریافته‌ی vision/speech/generate، ادغام شواهد و دو مسیر خطا (کلید مفقود و JSON نامعتبر) را بدون API یا اعتبارنامهٔ واقعی می‌سنجد.

## منابع کد
- `backend/app/pipeline/merge.py:18` — ادغام شواهد
- `backend/tests/test_pipeline.py` — تست‌های واحد pipeline با mock مدل
- `docs/mvp-design.md` — طراحی اصلی pipeline ۷ مرحله‌ای (نسخه‌ی کامل‌تر آینده)
