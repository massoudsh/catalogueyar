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

## اجرا با Docker

نیازمند Docker Engine و Compose v2 روی سرور:

```bash
cp backend/.env.example backend/.env
# تنظیمات موتور و کلیدهای احراز هویت فروشنده را در backend/.env وارد کنید.
docker compose up -d --build
```

- Dockerfile چندمرحله‌ای با Node.js 22 فرانت را build می‌کند؛ image نهایی Python 3.12، FastAPI، خروجی Vite و ffmpeg دارد و با کاربر غیر-root اجرا می‌شود.
- Compose فقط پورت `127.0.0.1:8000` سرور را باز می‌کند؛ reverse proxy همان سرور باید HTTPS را terminate و درخواست‌ها را به این پورت هدایت کند.
- رابط `/` و `/workspace` و API از یک origin سرو می‌شوند. متغیرهای `VITE_*` در runtime اعمال نمی‌شوند؛ هیچ کلید فروشنده‌ای در build فرانت قرار نمی‌گیرد. image پیش‌فرض هدر Bearer نمی‌فرستد؛ برای API محافظت‌شده، احراز هویت سمت سرور در reverse proxy یا مدیریت session لازم است. کلید فروشنده را در باندل عمومی قرار ندهید.
- `backend/.env` فقط در runtime وارد کانتینر می‌شود؛ `.dockerignore` فایل‌های env، ابزار محلی، attachmentها و خروجی‌های build محلی را از context خارج می‌کند.
- volume نام‌دار `catalogyar-data`، SQLite و cache را در `/data` نگه می‌دارد. Compose مسیرهای داده را صریحاً override می‌کند؛ تنظیمات دیگر از env می‌آیند. `docker compose down` داده را نگه می‌دارد؛ `down -v` آن را حذف می‌کند.
- healthcheck مسیر `/health` را بررسی می‌کند؛ دسترسی موتور یا سلامت build فرانت را تضمین نمی‌کند. فقط یک worker استفاده می‌شود چون rate limit فعلی درون‌پردازشی است.
- داده‌های قدیمی مسیر host خودکار منتقل نمی‌شوند؛ پیش از استقرار، از SQLite نسخهٔ پشتیبان بگیرید و انتقال به volume را جداگانه انجام دهید.

بیلد و smoke test واقعی image باید روی سرور انجام شود؛ در محیط فعلی Docker build اجرا نشده است.

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
