# کاتالوگ‌یار — Frontend

رابط React (Vite + TypeScript + Tailwind) برای ساخت و ویرایش کاتالوگ روی API فست‌API.

## پیش‌نیاز

- Node.js 20+
- بک‌اند در حال اجرا روی `http://127.0.0.1:8000` برای development proxy

## اجرا

```bash
cd frontend
cp .env.example .env   # در صورت نیاز VITE_API_BASE_URL / VITE_API_KEY را تنظیم کن
npm install
npm run dev
```

مرورگر: `http://127.0.0.1:5173`

### بک‌اند همزمان

```bash
cd backend
cp .env.example .env   # OPENAI_API_KEY را پر کنید
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## متغیرها

| متغیر | توضیح |
|---|---|
| `VITE_API_BASE_URL` | آدرس API جداگانه؛ خالی یعنی همان origin (پیش‌فرض) یا proxy توسعهٔ Vite |
| `VITE_API_KEY` | Bearer اختیاری وقتی `CATALOGYAR_API_KEYS` روی بک‌اند ست است |

Vite در development مسیرهای `/catalog` و `/health` را به بک‌اند proxy می‌کند. در production، ابتدا `npm run build` را اجرا کنید و FastAPI خروجی `frontend/dist` را در همان origin سرو می‌کند؛ در نتیجه لازم نیست `VITE_API_BASE_URL` تنظیم شود.

## صفحات

| مسیر | نقش |
|---|---|
| `/` | لندینگ برند-محور |
| `/workspace` | آپلود رسانه، `POST /catalog/generate`، ویرایش draft با `PATCH /catalog/{id}`، تاریخچه |

## فضای کار

- بستهٔ خلاصهٔ فارسی، کلیدواژه و FAQ قابل‌ویرایش؛ منشأ شواهد تصویر/ویس/بسته‌بندی در بخش جداگانه دیده می‌شود.
- امتیاز آمادگی محتوا، یک چک‌لیست محلی است و تأیید صحت یا پذیرش بازارگاه نیست.
- دانلود JSON نسخهٔ ذخیره‌شده برای اتصال سفارشی دیجی‌کالا/باسلام/ترب؛ فرمت هر سه یکسان است و دکمهٔ دانلود چیزی منتشر نمی‌کند.
- جست‌وجوی فارسی عنوان و دسته در ۲۰ پیش‌نویس اخیر؛ خطای دریافت تاریخچه جدا از حالت خالی نمایش داده می‌شود.
- پیش از تولید مجدد یا انتخاب پیش‌نویس دیگر، اصلاحات ذخیره‌نشده تأیید می‌گیرند؛ بستن/reload صفحه هشدار دارد. خروجی تا ذخیره غیرفعال می‌ماند.
- کنترل‌های قابل فوکوس و reduced motion رعایت شده‌اند؛ آزمون بصری و انطباق کامل دسترس‌پذیری هنوز نیازمند بررسی مستقل‌اند.

بررسی رقبا و محدودیت‌های این تحویل: `docs/competitor-research.md`.

## اسکریپت‌ها

- `npm run dev` — توسعه
- `npm run build` — بیلد production
- `npm run preview` — پیش‌نمایش بیلد
