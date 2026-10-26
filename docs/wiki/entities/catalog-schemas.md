# Catalog Schemas

> مدل‌های Pydantic ورودی/خروجی endpoint کاتالوگ و draftها.

## مسئولیت‌ها
- `CatalogGenerateResponse` — خروجی نهایی: `title`, `category`, `description`, `attributes`,
  `variants`, `missing_info_questions`, `source_evidence`، محتوای `short_description`, `seo_keywords`, `faqs`، اختیاری `english`
  (`EnglishCatalog`: title/description/attributes)، و اختیاری `draft_id` (فقط پاسخ HTTP).
- `FAQItem` — پرسش و پاسخ اجباری `question` و `answer`؛ FAQ/کلیدواژه برای draft قدیمی `[]` و خلاصه `""` هستند.
- `CatalogDraft` — wrapper ذخیره‌شده: `id`, `seller_id`, `created_at`, `updated_at`, `catalog`.
- `CatalogUpdate` — PATCH جزئی شامل خلاصه، کلیدواژه و FAQ؛ مدل‌های بدون مصرف `CatalogGenerateRequest` و `MarketplacePayload` حذف شده‌اند.
- زیرمدل‌ها: `Attribute` (name/value/confidence)، `Variant` (type/options)،
  `Category` (suggested/confidence)، `SourceEvidence` (from_image / from_voice / from_text_on_package).

## وابستگی‌ها
- [[entities/catalog-router]] — response_modelها و بدنهٔ PATCH
- [[entities/generate]] — پر کردن `CatalogGenerateResponse` از JSON مدل
- [[entities/storage]] — serialize/deserialize draft در SQLite
- [[entities/marketplaces]] — خواندن فیلدهای catalog برای export

## قراردادها / Edge cases
- تمام `confidence` بین ۰ و ۱ (`Field(ge=0.0, le=1.0)`).
- `english` می‌تواند `null` باشد اگر مدل برنگرداند؛ generate معمولاً آن را می‌سازد.
- `CatalogUpdate` فقط کلیدهای غیر-`None` را روی draft اعمال می‌کند و همان تغییرات در جدول
  `feedback` لاگ می‌شود ([[entities/storage]]).

## منابع کد
- `backend/app/schemas/catalog.py:15` — `FAQItem`
- `backend/app/schemas/catalog.py:37` — خروجی کاتالوگ
- `backend/app/schemas/catalog.py:61` — فیلدهای PATCH
