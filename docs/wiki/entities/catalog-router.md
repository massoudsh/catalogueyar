# Catalog Router

> endpoint اصلی API — دریافت عکس/ویس فروشنده و شروع pipeline ساخت کاتالوگ.

## مسئولیت‌ها
- تعریف `POST /catalog/generate` زیر prefix `/catalog`.
- اعتبارسنجی ورودی: ۱ تا ۵ عکس اجباری، ویس اختیاری، `seller_hint` اختیاری.
- (آینده) صدا زدن pipeline کامل: [[concepts/catalog-pipeline]].

## وابستگی‌ها
- [[entities/catalog-schemas]] — `CatalogGenerateResponse` به‌عنوان `response_model`
- [[concepts/catalog-pipeline]] — فلوی پردازش که هنوز به این endpoint وصل نشده

## قراردادها / Edge cases
- اگر تعداد عکس ۰ یا بیشتر از ۵ باشد → `400`.
- فعلاً همیشه `501` برمی‌گرداند (`این قابلیت هنوز پیاده‌سازی نشده است`) چون اتصال pipeline انجام نشده.

## منابع کد
- `backend/app/api/catalog.py:10` — `generate_catalog_endpoint`
