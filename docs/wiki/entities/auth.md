# Auth

> احراز هویت seller-scoped با Bearer API key و rate limit درون‌حافظه‌ای.

## مسئولیت‌ها
- `current_seller(authorization)` — FastAPI dependency؛ `seller_id` را برای همه routeهای
  [[entities/catalog-router]] برمی‌گرداند.
- نگاشت `CATALOGYAR_API_KEYS` به صورت `seller_id:api_key,...`.
- محدودیت درخواست در دقیقه (`CATALOGYAR_RATE_LIMIT_PER_MINUTE`، پیش‌فرض ۳۰) با deque و
  `time.monotonic`.

## وابستگی‌ها
- [[concepts/engine-config]] — خواندن `API_KEYS` و `RATE_LIMIT_PER_MINUTE` از `config.py`
- [[entities/catalog-router]] — مصرف‌کنندهٔ اصلی `Depends(current_seller)`
- [[entities/storage]] — draftها با همین `seller_id` scoped می‌شوند

## قراردادها / Edge cases
- اگر هیچ کلیدی در env نباشد → seller ثابت `"development"` (مناسب اجرای محلی بدون auth).
- بدون هدر `Authorization: Bearer …` وقتی کلید پیکربندی شده → `401`.
- کلید نامعتبر → `401`.
- عبور از سقف نرخ → `429`.
- شمارنده per-process است؛ با چند worker هر process جداگانه می‌شمارد.

## منابع کد
- `backend/app/auth.py` — `current_seller`
- `backend/.env.example` — نمونهٔ `CATALOGYAR_API_KEYS`
