# کاتالوگ‌یار — Frontend

رابط React (Vite + TypeScript + Tailwind) برای ساخت و ویرایش کاتالوگ روی API فست‌API.

## پیش‌نیاز

- Node.js 20+
- بک‌اند در حال اجرا روی `http://127.0.0.1:8000` (پیش‌فرض)

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
| `VITE_API_BASE_URL` | آدرس API — پیش‌فرض `http://127.0.0.1:8000` |
| `VITE_API_KEY` | Bearer اختیاری وقتی `CATALOGYAR_API_KEYS` روی بک‌اند ست است |

Vite همچنین `/catalog` و `/health` را به بک‌اند پروکسی می‌کند؛ اگر `VITE_API_BASE_URL` را خالی بگذاری و کد را طوری تغییر دهی که از relative URL استفاده کند، پروکسی فعال می‌شود. پیکربندی فعلی به‌صورت پیش‌فرض به `127.0.0.1:8000` می‌زند و CORS روی بک‌اند اجازهٔ origin فرانت را می‌دهد.

## صفحات

| مسیر | نقش |
|---|---|
| `/` | لندینگ برند-محور |
| `/workspace` | آپلود رسانه، `POST /catalog/generate`، ویرایش draft با `PATCH /catalog/{id}`، تاریخچه |

## اسکریپت‌ها

- `npm run dev` — توسعه
- `npm run build` — بیلد production
- `npm run preview` — پیش‌نمایش بیلد
