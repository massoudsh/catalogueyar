# Storage

> ذخیره‌سازی SQLite برای draft کاتالوگ، بازخورد ویرایش، و زمینهٔ تاریخچهٔ فروشنده.

## مسئولیت‌ها
- `create_draft(seller_id, catalog)` — UUID + INSERT در جدول `drafts`.
- `get_draft` / `list_drafts` — خواندن scoped به seller (لیست حداکثر ۲۰، جدیدترین اول).
- `update_draft` — اعمال `CatalogUpdate`، به‌روزرسانی `updated_at`، INSERT در `feedback`.
- `seller_context(seller_id, limit=5)` — آخرین کاتالوگ‌های فروشنده برای پرامپت generate
  ([[entities/generate]]).
- `recent_feedback(seller_id, limit=8)` — آخرین تغییرات PATCH برای یادگیری سبک در generate.

## وابستگی‌ها
- [[concepts/engine-config]] — `DATABASE_PATH` / `CATALOGYAR_DATA_DIR`
- [[entities/catalog-schemas]] — serialize با `model_dump_json` / `model_validate_json`
- [[entities/catalog-router]] — بعد از generate و در history/detail/edit

## قراردادها / Edge cases
- جداول در اولین اتصال ساخته می‌شوند (`CREATE TABLE IF NOT EXISTS`).
- مسیر DB از env؛ پیش‌فرض `/tmp/catalogyar/catalogyar.sqlite3`.
- `get_draft` / `update_draft` اگر id مال seller دیگر باشد `None` → router `404`.
- feedback فقط تغییرات PATCH را JSON می‌کند؛ `recent_feedback` همان‌ها را به پرامپت generate می‌دهد.

## منابع کد
- `backend/app/storage.py`
