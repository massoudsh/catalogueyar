# Catalog Router

> لایهٔ API کاتالوگ — generate، تاریخچه، ویرایش، export و publish.

## مسئولیت‌ها
- `POST /catalog/generate` — آپلود ۱–۵ عکس/ویدئو + ویس اختیاری؛ اجرای [[concepts/catalog-pipeline]]؛
  ذخیرهٔ draft در [[entities/storage]].
- `GET /catalog/history` — لیست draftهای فروشندهٔ فعلی.
- `GET /catalog/{draft_id}` — جزئیات یک draft.
- `PATCH /catalog/{draft_id}` — ویرایش جزئی فیلدها (`CatalogUpdate`) و ثبت feedback.
- `GET /catalog/{draft_id}/export/{marketplace}` — payload آمادهٔ انتشار بدون HTTP بیرونی.
- `POST /catalog/{draft_id}/publish/{marketplace}` — ارسال به endpoint مارکت‌پلیس
  ([[entities/marketplaces]]).
- همه endpointها از `Depends(current_seller)` ([[entities/auth]]) عبور می‌کنند.

## وابستگی‌ها
- [[entities/catalog-schemas]] — `CatalogGenerateResponse` / `CatalogDraft` / `CatalogUpdate`
- [[concepts/catalog-pipeline]] — فلوی generate
- [[entities/video]] — اگر فایل ویدئو باشد قبل از vision فریم می‌گیرد
- [[entities/storage]] — create/list/get/update draft + seller_context برای generate
- [[entities/marketplaces]] — export/publish
- [[concepts/engine-config]] — map خطای موتور به HTTP

## قراردادها / Edge cases
- ۰ یا بیش از ۵ مدیا → `400`.
- ویدئو با ffmpeg به حداکثر ۵ فریم JPG تبدیل می‌شود؛ فریم‌ها و فایل‌های موقت در `finally` پاک می‌شوند.
- بدون کلید مدل → `503`؛ خطای فراخوانی مدل/ffmpeg/publish → `502`.
- draft ناموجود یا متعلق به seller دیگر → `404`.
- marketplace ناشناخته در export → `400`؛ publish بدون endpoint یا خطای شبکه → `502`.

## منابع کد
- `backend/app/api/catalog.py` — همه routeها
- `backend/app/main.py` — mount router + UI استاتیک `/`
