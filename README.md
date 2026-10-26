# کاتالوگ‌یار (CatalogYar)

دستیار هوشمند ساخت کاتالوگ محصول — فروشنده محصولش را نشان می‌دهد (عکس/ویدئو/ویس)، به‌جای اینکه فرم پر کند.

## ساختار پروژه

```
docs/
  product-doc.md         # مستند محصول
  mvp-design.md           # طراحی ورودی/خروجی اولیه
  engine-design.md         # معماری موتور + وضعیت فیچرها
  api.md                    # مرجع HTTP endpointها
  competitor-research.md     # تحقیق رقبا
  wiki/                       # ویکی دانش زنده — قوانین در CLAUDE.md
backend/
  app/
    main.py            # FastAPI، API و سرو خروجی Vite در production
    api/catalog.py      # generate/history/edit/export/publish
    pipeline/            # video, vision, speech, merge, generate, retry, cache
    schemas/catalog.py   # مدل‌های ورودی/خروجی
    storage.py           # SQLite draft و feedback
    auth.py              # Bearer API key و rate limit
    marketplaces.py      # export/publish مارکت‌پلیس
frontend/
  src/                   # React + Vite + Tailwind + Zod + Framer Motion
```

## مستندات

| سند | محتوا |
|---|---|
| `docs/wiki/overview.md` | نقطهٔ شروع ایجنت/توسعه‌دهنده |
| `docs/api.md` | مرجع endpointها |
| `docs/engine-design.md` | موتور AI و checklist فیچر |
| `docs/product-doc.md` | مسئله، بازار، نقشه راه |
| `docs/mvp-design.md` | قرارداد JSON اولیه |
| `docs/competitor-research.md` | مقایسهٔ رقبا، پنج قابلیت جدید و ممیزی فایل/UX با محدودیت‌های اعتبارسنجی |
| `frontend/README.md` | اجرای UI مدرن |
| `CLAUDE.md` | قوانین نگهداری ویکی |

`docs/wiki/` ویکی زنده است: بعد از هر تغییر معنایی در کد، صفحهٔ مرتبط را به‌روز کنید.

## وضعیت فعلی

اپ FastAPI به‌همراه رابط React/Vite آماده است. در production، FastAPI خروجی build‌شدهٔ `frontend/dist` را روی `/` سرو می‌کند.
`POST /catalog/generate` عکس یا ویدئو، ویس اختیاری، توضیح فروشنده و دسته‌های مجاز را می‌گیرد و
draft ساختاریافتهٔ فارسی/انگلیسی می‌سازد. draftها در SQLite ذخیره می‌شوند؛ history، detail،
edit، export و publish برای digikala/basalam/torob در دسترس‌اند. خروجی بازارگاهی JSON عمومی برای اتصال سفارشی است، نه آداپتر رسمی تأییدشده.
بستهٔ SEO/FAQ قابل‌ویرایش، نمایش شواهد، چک‌لیست آمادگی، دانلود JSON ذخیره‌شده و جست‌وجوی فارسی ۲۰ پیش‌نویس اخیر در workspace در دسترس‌اند.
برای جزئیات HTTP ببینید `docs/api.md`.

## اجرای محلی

### بک‌اند

```bash
cd backend
cp .env.example .env   # OPENAI_API_KEY را پر کنید؛ ffmpeg برای ویدئو لازم است
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- پس از build فرانت، رابط: `http://127.0.0.1:8000/`
- OpenAPI: `http://127.0.0.1:8000/docs`

### فرانت (Vite)

```bash
cd frontend
cp .env.example .env   # برای deployment same-origin خالی بگذارید
npm install
npm run build
```

خروجی `frontend/dist` توسط FastAPI روی `/` سرو می‌شود. برای توسعهٔ محلی به‌جای build، `npm run dev` را اجرا کنید؛ لندینگ `/` و فضای ساخت/ویرایش `/workspace` هستند.

## متغیرهای محیطی (خلاصه)

| متغیر | نقش |
|---|---|
| `OPENAI_API_KEY` | الزامی برای vision/speech/generate؛ بدون آن `503` |
| `CATALOGYAR_*_MODEL` | override نام مدل‌ها (vision / speech / generate) |
| `CATALOGYAR_DATA_DIR` / `CATALOGYAR_DATABASE_PATH` | مسیر داده و SQLite |
| `CATALOGYAR_IMAGE_CACHE_*` / `CATALOGYAR_VISION_CACHE_DIR` | cache تحلیل تصویر (enable، dir، TTL) |
| `CATALOGYAR_MODEL_MAX_ATTEMPTS` / `…_RETRY_*_DELAY` | retry/backoff فراخوانی مدل |
| `CATALOGYAR_API_KEYS` / `CATALOGYAR_RATE_LIMIT_PER_MINUTE` | auth seller-scoped + rate limit |
| `CATALOGYAR_CORS_ORIGINS` | origins مجاز برای فرانت Vite (پیش‌فرض `:5173`) |
| `DIGIKALA_*` / `BASALAM_*` / `TOROB_*` | URL/token انتشار مارکت‌پلیس |
| `VITE_API_BASE_URL` / `VITE_API_KEY` | فرانت → آدرس API و Bearer اختیاری |

جزئیات کامل: `backend/.env.example`، `frontend/.env.example` و `docs/wiki/concepts/engine-config.md`.
