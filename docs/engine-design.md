# موتور هوش مصنوعی — طراحی و وضعیت فیچرها

## وضعیت فعلی (پیاده‌سازی‌شده)

`POST /catalog/generate` موتور کامل را صدا می‌زند و draft را ذخیره می‌کند:

```
عکس / ویدئو (+ ویس اختیاری)
    │
    ▼
video.extract_video_frames()  → ffmpeg (فقط فایل ویدئو) → فریم JPG
    │
    ▼
vision.analyze_images()       → مدل vision (+ cache دیسکی)
    │
    ▼
speech.transcribe_voice()     → whisper اگر ویس بود
    │
    ▼
merge.merge_evidence()        → بدون مدل
    │
    ▼
generate.generate_catalog()   → JSON نهایی (+ english + تاریخچه فروشنده)
    │
    ▼
storage.create_draft()        → SQLite
```

- تنظیمات در `backend/app/config.py` از env.
- بدون `OPENAI_API_KEY` → `503` (`EngineNotConfiguredError`).
- خطای مدل / ffmpeg / publish → `502` (`EngineCallError`).
- فایل‌های موقت و فریم‌ها در `finally` پاک می‌شوند.
- **Retry**: `pipeline/retry.py` → `with_retry` (۳ تلاش، backoff نمایی روی خطای موقت شبکه/۴۲۹).
- **Cache تصویر**: `pipeline/cache.py` — کلید hash محتوا، فایل JSON در `CATALOGYAR_VISION_CACHE_DIR`.
- **Auth + rate limit**: `auth.py` با `CATALOGYAR_API_KEYS`.
- **تاریخچه / ویرایش / feedback**: `storage.py` + endpointهای history/detail/PATCH.
- **مارکت‌پلیس**: `marketplaces.py` — export و publish برای digikala/basalam/torob.
- مرجع HTTP: `docs/api.md`. ویکی زنده: `docs/wiki/`.

## چرا OpenAI-compatible API

- یک SDK برای vision + speech-to-text + chat با یک کلید.
- Interface هر ماژول مستقل از provider است؛ عوض کردن مدل زیرین نیازی به تغییر schema عمومی ندارد.

## نقشه‌ی راه فیچرها

### موتور
1. ~~Retry/backoff~~ — ✅
2. ~~Cache تحلیل تصویر~~ — ✅ (نسخهٔ سادهٔ دیسکی؛ بدون TTL جدا)
3. ~~پردازش ویدئو (فریم‌گیری)~~ — ✅ (`pipeline/video.py` + ffmpeg)
4. ~~تشخیص چند رنگ / variant از ست عکس~~ — ✅ (پرامپت vision+generate)
5. **مدل گفتار فارسی اختصاصی‌تر** اگر whisper برای لهجه‌های محلی کافی نبود.

### محصول
6. ~~ویرایش خروجی + ثبت feedback~~ — ✅ (`PATCH /catalog/{id}` + جدول feedback)
7. ~~یادگیری سبک از تاریخچه فروشنده~~ — ✅ سبک (`seller_context` در پرامپت generate)
8. ~~خروجی/انتشار مارکت‌پلیس~~ — ✅ export + publish با URL از env (اتصال واقعی وابسته به credential)
9. ~~خروجی دو زبانه (FA + EN)~~ — ✅ فیلد `english`
10. ~~Auth و rate limiting~~ — ✅ Bearer API key

### باقی‌مانده / سخت‌تر
- UI تعاملی غنی‌تر روی فیلدهای low-confidence (الان RTL پایه روی `/` هست).
- اعتبارسنجی سخت `category.suggested ∈ store_category_list` سمت سرور.
- TTL/observability پیشرفته‌تر برای cache تصویر.
- حلقهٔ یادگیری واقعی از جدول feedback (فعلاً فقط ذخیره می‌شود).
- یکپارچگی عمیق‌تر با API رسمی هر مارکت‌پلیس (الان POST عمومی با payload داخلی است).
