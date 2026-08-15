# Catalog Router

> endpoint اصلی API — دریافت عکس/ویس فروشنده و شروع pipeline ساخت کاتالوگ.

## مسئولیت‌ها
- تعریف `POST /catalog/generate` زیر prefix `/catalog`.
- اعتبارسنجی ورودی: ۱ تا ۵ عکس اجباری، ویس اختیاری، `seller_hint` و `store_category_list` اختیاری.
- ذخیره‌ی موقت فایل‌های آپلودی (`tempfile.NamedTemporaryFile`) و صدا زدن pipeline کامل:
  [[concepts/catalog-pipeline]]. پاک‌سازی فایل‌های موقت در `finally` تضمین می‌شود.

## وابستگی‌ها
- [[entities/catalog-schemas]] — `CatalogGenerateResponse` به‌عنوان `response_model`
- [[concepts/catalog-pipeline]] — فلوی پردازش که حالا به این endpoint وصل است
- [[concepts/engine-config]] — خطاهای `EngineNotConfiguredError`/`EngineCallError` را به کد HTTP مناسب map می‌کند

## قراردادها / Edge cases
- اگر تعداد عکس ۰ یا بیشتر از ۵ باشد → `400`.
- اگر `OPENAI_API_KEY` تنظیم نشده → `503` (پیام روشن، نه `501` مبهم قبلی).
- اگر فراخوانی مدل fail شود (شبکه/format) → `502`.
- فایل‌های موقت همیشه پاک می‌شوند، حتی در مسیر خطا.

## منابع کد
- `backend/app/api/catalog.py:10` — `generate_catalog_endpoint`
