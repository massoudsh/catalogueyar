# Overview — کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول: فروشنده به‌جای پرکردن فرم، عکس/ویدئو/ویس محصول را می‌فرستد
و سیستم خروجی ساختاریافته‌ی کاتالوگ (عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها) را تولید می‌کند.

## معماری فعلی (موتور واقعی وصل شده)
Backend تنها با FastAPI، بدون بیلد سنگین:

```
backend/app/
  main.py            # FastAPI app + health check
  config.py           # تنظیمات موتور (API key، نام مدل‌ها) از env
  api/catalog.py      # POST /catalog/generate — pipeline را واقعاً صدا می‌زند
  schemas/catalog.py   # مدل‌های Pydantic ورودی/خروجی
  pipeline/
    errors.py           # EngineNotConfiguredError / EngineCallError
    vision.py            # تحلیل تصویر — مدل vision واقعی (OpenAI-compatible)
    speech.py             # رونویسی ویس فارسی — مدل speech-to-text واقعی
    merge.py               # ادغام شواهد چندمنبعی (بدون فراخوانی مدل)
    generate.py             # تولید خروجی نهایی کاتالوگ — مدل زبانی واقعی
```

جریان درخواست: `POST /catalog/generate` → `vision.analyze_images` → `speech.transcribe_voice`
(اگر ویس بود) → `merge.merge_evidence` → `generate.generate_catalog` → پاسخ `CatalogGenerateResponse`.
جزئیات کامل فلو در [[concepts/catalog-pipeline]].

## وضعیت
موتور به یک مدل OpenAI-compatible وصل است (پیش‌فرض `gpt-4o-mini` برای vision/generate،
`whisper-1` برای speech). بدون `OPENAI_API_KEY` در env، endpoint خطای `503` روشن برمی‌گرداند
(نه `501` مبهم). جزئیات در `docs/engine-design.md`.

## مستندات محصول
- `docs/product-doc.md` — مسئله، راه‌حل، بازار هدف، مدل درآمدی، نقشه راه
- `docs/mvp-design.md` — طراحی دقیق ورودی/خروجی JSON و pipeline ۷ مرحله‌ای
- `docs/engine-design.md` — معماری موتور فعلی + نقشه‌ی راه فیچرهای بعدی
- `docs/competitor-research.md` — جایگاه در بازار جهانی و ایران

## ریپو
`https://github.com/massoudsh/catalogueyar` — برنچ `main`.
