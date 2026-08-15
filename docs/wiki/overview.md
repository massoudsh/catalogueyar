# Overview — کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول: فروشنده به‌جای پرکردن فرم، عکس/ویدئو/ویس محصول را می‌فرستد
و سیستم خروجی ساختاریافته‌ی کاتالوگ (عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها) را تولید می‌کند.

## معماری فعلی (فاز MVP — اسکلت)
Backend تنها با FastAPI، بدون بیلد سنگین:

```
backend/app/
  main.py            # FastAPI app + health check
  api/catalog.py      # POST /catalog/generate
  schemas/catalog.py   # مدل‌های Pydantic ورودی/خروجی
  pipeline/
    vision.py          # تحلیل تصویر محصول (اسکلت)
    speech.py           # رونویسی ویس فارسی (اسکلت)
    merge.py             # ادغام شواهد چندمنبعی
    generate.py           # تولید خروجی نهایی کاتالوگ (اسکلت)
```

جریان درخواست: `POST /catalog/generate` → (آینده) `vision.analyze_images` → `speech.transcribe_voice`
→ `merge.merge_evidence` → `generate.generate_catalog` → پاسخ `CatalogGenerateResponse`.
جزئیات کامل فلو در [[concepts/catalog-pipeline]].

## وضعیت
اسکلت API و pipeline آماده است؛ اتصال واقعی به مدل تحلیل تصویر و گفتار فارسی هنوز پیاده نشده
(عمداً `NotImplementedError` / پاسخ `501`) — قدم بعدی پروژه همین اتصال است.

## مستندات محصول
- `docs/product-doc.md` — مسئله، راه‌حل، بازار هدف، مدل درآمدی، نقشه راه
- `docs/mvp-design.md` — طراحی دقیق ورودی/خروجی JSON و pipeline ۷ مرحله‌ای

## ریپو
`https://github.com/massoudsh/catalogueyar` — برنچ `main`.
