# کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول — فروشنده محصولش را نشان می‌دهد (عکس/ویدئو/ویس)، به‌جای اینکه فرم پر کند.

## ساختار پروژه

```
docs/
  product-doc.md     # مستند محصول: مسئله، راه‌حل، بازار، مدل درآمدی، نقشه راه
  mvp-design.md       # طراحی دقیق ورودی/خروجی و pipeline نسخه‌ی اول
  wiki/                # ویکی دانش زنده‌ی پروژه (entities/concepts) — قوانین در CLAUDE.md
backend/
  app/
    main.py            # FastAPI entrypoint
    api/catalog.py      # endpointهای generate/history/edit/export/publish
    pipeline/            # مراحل پردازش: retry, cache, video, vision, speech, merge, generate
    schemas/catalog.py   # مدل‌های ورودی/خروجی
    storage.py           # ذخیره‌سازی SQLite draft و feedback
    auth.py              # Bearer API key و rate limit
```

## ویکی دانش پروژه

`docs/wiki/` یک ویکی زنده و append-friendly است که کنار کد رشد می‌کند (به‌جای مستندسازی یک‌بار
و کهنه‌شدن). قوانین کامل نگهداری‌اش در `CLAUDE.md` است — هر ایجنت یا توسعه‌دهنده‌ای که روی این
ریپو کار می‌کند باید `docs/wiki/overview.md` و `docs/wiki/index.md` را ابتدا بخواند و بعد از هر
تغییر معنایی، صفحه‌ی مرتبط را به‌روز کند.

## وضعیت فعلی

اپ FastAPI آماده است و رابط RTL روی `/` سرو می‌شود. endpoint اصلی `POST /catalog/generate` عکس یا ویدئو، ویس اختیاری، توضیح فروشنده و دسته‌های مجاز را می‌گیرد و draft ساختاریافتهٔ فارسی/انگلیسی می‌سازد. draftها در SQLite ذخیره می‌شوند و endpointهای تاریخچه، جزئیات، ویرایش، export و publish برای بازارگاه‌ها در دسترس‌اند.

## اجرای محلی

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
