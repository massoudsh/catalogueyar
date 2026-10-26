# Frontend App

> رابط React مدرن کاتالوگ‌یار برای generate و edit روی API فست‌API.

## مسئولیت‌ها
- لندینگ برند-محور در `/` (Vite).
- فضای تعاملی `/workspace`: آپلود ۱–۵ عکس/ویدئو + ویس اختیاری، فراخوانی
  `POST /catalog/generate`، نمایش/ویرایش فیلدها، `PATCH /catalog/{draft_id}`،
  و لیست `GET /catalog/history`.
- اعتبارسنجی ورودی با Zod؛ انیمیشن سبک با Framer Motion؛ استایل Tailwind.
- `VITE_API_BASE_URL` (پیش‌فرض same-origin) و `VITE_API_KEY` اختیاری.
- بخش SEO/FAQ: خلاصه و کلیدواژه و FAQ قابل‌ویرایش/حذف؛ ذخیره با PATCH و درج در خروجی JSON.
- بخش منشأ: شواهد مدل از تصویر، ویس و متن بسته‌بندی؛ راستی‌آزمایی مستقل نیست.
- آمادگی محتوا: پنج بررسی هم‌وزن برای عنوان/توضیح/دسته/ویژگی/سؤال؛ امتیاز ۰–۱۰۰ تأیید بازارگاه یا صحت ادعا نیست.
- دریافت JSON ذخیره‌شده برای digikala/basalam/torob؛ سه نام یک payload عمومی دارند و UI چیزی منتشر نمی‌کند؛ تا ذخیرهٔ اصلاحات غیرفعال است.
- جست‌وجوی عنوان/دسته در حداکثر ۲۰ draft اخیر با نرمال‌سازی فارسی؛ خطای دریافت تاریخچه جدا از حالت خالی است.
- خطای انتخاب بیش از پنج رسانه همراه حذف تک‌فایل، حذف پیام تکراری ذخیره، focus قابل مشاهده و reduced motion.

## وابستگی‌ها
- [[entities/catalog-router]] — generate / history / detail / edit
- [[entities/catalog-schemas]] — شکل پاسخ و `CatalogUpdate`
- [[concepts/engine-config]] — CORS از طریق `CATALOGYAR_CORS_ORIGINS` در `main.py`

## قراردادها / Edge cases
- در development، Vite درخواست API را به `:8000` proxy می‌کند؛ health در دسترس نبودن backend را نمایش می‌دهد.
- اگر `CATALOGYAR_API_KEYS` ست باشد، `VITE_API_KEY` لازم است.
- رابط legacy حذف شده است؛ FastAPI در production از `frontend/dist` روی `/` و `/workspace` سرو می‌کند. بدون build این دو مسیر `503` و asset/مسیر ناشناخته `404` می‌گیرند.
- اصلاحات ذخیره‌نشده قبل از تولید مجدد/تعویض draft تأیید می‌گیرند؛ reload/بستن صفحه هشدار دارد، اما blocker سراسری مسیریابی داخلی پیاده‌سازی نشده است.
- ۴۰ تست backend و syntax فرانت بررسی شده‌اند؛ type-check/lint/build به‌دلیل دسترس‌نبودن npm registry و تست بصری به‌دلیل محدودیت محیط اجرا نشده‌اند.

## منابع کد
- `frontend/src/App.tsx:25` — reduced motion
- `frontend/src/components/CatalogEditor.tsx:19` — ویرایش، شواهد، چک‌لیست و دریافت JSON
- `frontend/src/components/HistoryList.tsx:14` — جست‌وجوی فارسی و خطای تاریخچه
- `frontend/src/components/GeneratePanel.tsx:25` — ورودی و حذف فایل
- `frontend/src/pages/WorkspacePage.tsx:79` — ذخیرهٔ فیلدها و پیام وضعیت واحد
- `frontend/src/lib/api.ts:114` — دریافت JSON با احراز هویت موجود
- `frontend/src/index.css:53` — focus قابل مشاهده
- `frontend/README.md` — راهنمای اجرا
