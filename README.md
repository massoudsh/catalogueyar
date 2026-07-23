# کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول — فروشنده محصولش را نشان می‌دهد (عکس/ویدئو/ویس)، به‌جای اینکه فرم پر کند.

## ساختار پروژه

```
docs/
  product-doc.md     # مستند محصول: مسئله، راه‌حل، بازار، مدل درآمدی، نقشه راه
  mvp-design.md       # طراحی دقیق ورودی/خروجی و pipeline نسخه‌ی اول
backend/
  app/
    main.py            # FastAPI entrypoint
    api/catalog.py      # POST /catalog/generate
    pipeline/            # مراحل پردازش: vision, speech, merge, generate
    schemas/catalog.py   # مدل‌های ورودی/خروجی
```

## وضعیت فعلی

اسکلت اولیه‌ی API آماده است؛ endpoint اصلی (`POST /catalog/generate`) ساختار درخواست/پاسخ را دارد اما اتصال واقعی به مدل‌های تحلیل تصویر/گفتار هنوز پیاده‌سازی نشده (`NotImplementedError` / پاسخ `501`).

## اجرای محلی (بعد از پیاده‌سازی pipeline)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
