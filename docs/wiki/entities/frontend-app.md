# Frontend App

> رابط React مدرن کاتالوگ‌یار برای generate و edit روی API فست‌API.

## مسئولیت‌ها
- لندینگ برند-محور در `/` (Vite).
- فضای تعاملی `/workspace`: آپلود ۱–۵ عکس/ویدئو + ویس اختیاری، فراخوانی
  `POST /catalog/generate`، نمایش/ویرایش فیلدها، `PATCH /catalog/{draft_id}`،
  و لیست `GET /catalog/history`.
- اعتبارسنجی ورودی با Zod؛ انیمیشن سبک با Framer Motion؛ استایل Tailwind.
- `VITE_API_BASE_URL` (پیش‌فرض `http://127.0.0.1:8000`) و `VITE_API_KEY` اختیاری.

## وابستگی‌ها
- [[entities/catalog-router]] — generate / history / detail / edit
- [[entities/catalog-schemas]] — شکل پاسخ و `CatalogUpdate`
- [[concepts/engine-config]] — CORS از طریق `CATALOGYAR_CORS_ORIGINS` در `main.py`

## قراردادها / Edge cases
- بدون بک‌اند روی `:8000`، health در هدر آفلاین می‌شود و generate خطای شبکه می‌دهد.
- اگر `CATALOGYAR_API_KEYS` ست باشد، `VITE_API_KEY` لازم است.
- UI استاتیک قدیمی روی `backend/app/static` همچنان روی `/` بک‌اند سرو می‌شود؛ این فرانت جداست.

## منابع کد
- `frontend/src/App.tsx` — router
- `frontend/src/pages/WorkspacePage.tsx` — فلو اصلی
- `frontend/src/lib/api.ts` — کلاینت HTTP
- `frontend/README.md` — راهنمای اجرا
