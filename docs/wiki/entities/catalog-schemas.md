# Catalog Schemas

> مدل‌های Pydantic ورودی/خروجی endpoint کاتالوگ.

## مسئولیت‌ها
- `CatalogGenerateRequest` — فیلدهای فرمی جانبی (`seller_hint`, `store_category_list`).
- `CatalogGenerateResponse` — خروجی نهایی: `title`, `category`, `description`, `attributes`,
  `variants`, `missing_info_questions`, `source_evidence`.
- زیرمدل‌ها: `Attribute` (name/value/confidence)، `Variant` (type/options)،
  `Category` (suggested/confidence)، `SourceEvidence` (ردیابی این‌که هر فیلد از کجا آمده:
  عکس / صدا / متن روی بسته‌بندی).

## وابستگی‌ها
- [[entities/catalog-router]] — به‌عنوان `response_model`
- [[entities/generate]] — این ماژول همین schema را برای ساخت خروجی نهایی پر می‌کند

## قراردادها / Edge cases
- تمام فیلدهای `confidence` بین ۰ و ۱ محدود شده‌اند (`Field(ge=0.0, le=1.0)`).
- `SourceEvidence` طراحی شده تا شفافیت منبع هر داده (چرا این عنوان/رنگ پیشنهاد شد) حفظ شود.

## منابع کد
- `backend/app/schemas/catalog.py:31` — `CatalogGenerateResponse`
- `backend/app/schemas/catalog.py:15` — `SourceEvidence`
