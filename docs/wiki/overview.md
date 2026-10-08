# Overview — کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول: فروشنده به‌جای پرکردن فرم، عکس/ویدئو/ویس محصول را می‌فرستد
و سیستم خروجی ساختاریافته‌ی کاتالوگ (عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها، نسخه‌ی انگلیسی)
را تولید می‌کند. رابط RTL استاتیک روی `/` سرو می‌شود؛ فرانت مدرن React در `frontend/`
(Vite، مسیرهای `/` و `/workspace`).

## معماری فعلی
Backend با FastAPI؛ draftها در SQLite؛ انتشار به مارکت‌پلیس از env؛ فرانت جدا با CORS:

```
backend/app/
  main.py              # FastAPI + static RTL UI روی / + CORS برای Vite
  config.py             # مدل‌ها، DB، API keys، endpoint مارکت‌پلیس‌ها
  auth.py               # Bearer API key seller-scoped + rate limit
  storage.py            # SQLite drafts + feedback + seller_context
  marketplaces.py       # export/publish برای digikala|basalam|torob
  api/catalog.py        # generate / history / detail / edit / export / publish
  schemas/catalog.py     # Pydantic ورودی/خروجی + Draft/Update
  pipeline/
    errors.py             # EngineNotConfiguredError / EngineCallError
    retry.py               # call_with_retry روی خطای موقت شبکه/429/5xx
    cache.py                # cache JSON تحلیل تصویر (hash محتوا + TTL)
    video.py                 # ffmpeg فریم‌گیری از ویدئو
    vision.py                 # تحلیل تصویر (مدل vision)
    speech.py                  # رونویسی ویس فارسی
    merge.py                    # ادغام شواهد (بدون مدل)
    generate.py                  # خروجی نهایی کاتالوگ (+ english + history)
frontend/
  src/                   # React UI: لندینگ + workspace (generate/edit/history)
```

جریان `POST /catalog/generate`: auth → ویدئو→فریم (در صورت نیاز) → vision → speech → merge →
generate(+seller history) → create_draft → پاسخ. جزئیات: [[concepts/catalog-pipeline]].

## وضعیت
موتور به API سازگار با OpenAI وصل است (پیش‌فرض `gpt-4o-mini` / `whisper-1`). بدون
`OPENAI_API_KEY` → `503`. Auth اختیاری است: اگر `CATALOGYAR_API_KEYS` خالی باشد seller=`development`.
ویدئو، تاریخچه/ویرایش draft، خروجی انگلیسی، export/publish مارکت‌پلیس، اعتبارسنجی دسته،
یادگیری از feedback، UI استاتیک فیلدهای کم‌اطمینان، و فرانت Vite (generate + edit mode)
پیاده‌سازی شده‌اند. فرانت: [[entities/frontend-app]].
تنظیمات: [[concepts/engine-config]]. جزئیات موتور: `docs/engine-design.md`. API: `docs/api.md`.

## مستندات محصول
- `docs/product-doc.md` — مسئله، راه‌حل، بازار، مدل درآمدی، نقشه راه
- `docs/mvp-design.md` — طراحی ورودی/خروجی و pipeline اولیه
- `docs/engine-design.md` — معماری موتور + وضعیت فیچرها
- `docs/api.md` — مرجع endpointها
- `docs/competitor-research.md` — جایگاه بازار

## ریپو
`https://github.com/massoudsh/catalogueyar` — برنچ `main`.
