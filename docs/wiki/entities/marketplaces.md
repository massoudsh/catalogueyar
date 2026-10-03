# Marketplaces

> تبدیل کاتالوگ داخلی به payload مارکت‌پلیس و انتشار HTTP اختیاری.

## مسئولیت‌ها
- `export_payload(marketplace, catalog)` — dict استاندارد: title, description, category,
  attributes, variants, english.
- `publish(marketplace, catalog)` — POST JSON به URL تنظیم‌شده در env با Bearer token اختیاری.
- مارکت‌پلیس‌های پشتیبانی‌شده: `digikala`, `basalam`, `torob` (`SUPPORTED_MARKETPLACES`).

## وابستگی‌ها
- [[concepts/engine-config]] — `MARKETPLACE_ENDPOINTS` / `MARKETPLACE_TOKENS` /
  `REQUEST_TIMEOUT_SECONDS`
- [[entities/catalog-schemas]] — خواندن فیلدهای `CatalogGenerateResponse`
- [[entities/catalog-router]] — `GET …/export/{marketplace}` و `POST …/publish/{marketplace}`

## قراردادها / Edge cases
- نام ناشناخته → `ValueError` → در export به `400`، در publish همراه خطای شبکه به `502`.
- اگر URL انتشار خالی باشد → `EngineCallError` («endpoint تنظیم نشده»).
- پاسخ خام provider به‌صورت رشته در `{"marketplace","status":"published","response"}` برمی‌گردد.
- timeout پیش‌فرض ۱۲ ثانیه (`CATALOGYAR_REQUEST_TIMEOUT_SECONDS`).

## منابع کد
- `backend/app/marketplaces.py`
- `backend/app/config.py` — نگاشت env به digikala/basalam/torob
