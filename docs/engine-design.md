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

- تنظیمات در `backend/app/config.py` — از env vars خوانده می‌شود (`OPENAI_API_KEY` و ۳ نام مدل قابل override).
- بدون `OPENAI_API_KEY` هر سه مرحله‌ی مدل‌محور خطای `503` با پیام روشن برمی‌گردانند (`EngineNotConfiguredError`).
- خطای فراخوانی مدل / ffmpeg / publish → `502` (`EngineCallError`).
- فایل‌های آپلودی و فریم‌ها در `tempfile` موقت ذخیره و در `finally` پاک می‌شوند.
- **Auth + rate limit**: `auth.py` با `CATALOGYAR_API_KEYS` / `CATALOGYAR_RATE_LIMIT_PER_MINUTE`.
- **تاریخچه / ویرایش / feedback**: `storage.py` + endpointهای history/detail/PATCH.
- **مارکت‌پلیس**: `marketplaces.py` — export و publish برای digikala/basalam/torob.
- مرجع HTTP: `docs/api.md`. ویکی زنده: `docs/wiki/`.
- **Retry/backoff** (issue #1، پیاده‌سازی‌شده): هر سه فراخوانی مدل از `pipeline/retry.py`
  (`call_with_retry`) رد می‌شوند — فقط خطای موقت (قطعی شبکه/تایم‌اوت/`429`/`5xx`) با backoff نمایی
  و jitter دوباره تلاش می‌شود؛ خطای `4xx` کلاینت (مثل `400`/`401`/`403`) بدون retry بالا می‌رود.
  تنظیمات: `CATALOGYAR_MODEL_MAX_ATTEMPTS` (پیش‌فرض ۳، هرگز بی‌نهایت)،
  `CATALOGYAR_MODEL_RETRY_BASE_DELAY` (۰.۵s) و `CATALOGYAR_MODEL_RETRY_MAX_DELAY` (۸s).
- **Cache تحلیل تصویر** (issue #2، پیاده‌سازی‌شده): کلید از SHA-256 بایت‌های عکس + نام مدل + نسخه‌ی
  schema/prompt ساخته می‌شود (`pipeline/cache.py`)، روی دیسک در
  `CATALOGYAR_IMAGE_CACHE_DIR` / `CATALOGYAR_VISION_CACHE_DIR` (پیش‌فرض
  `$CATALOGYAR_DATA_DIR/vision-cache`) ذخیره و با TTL (`CATALOGYAR_IMAGE_CACHE_TTL_SECONDS`،
  پیش‌فرض ۷ روز) منقضی می‌شود. هر خطای cache فقط warning است و به فراخوانی عادی مدل برمی‌گردد؛
  hit/miss هم لاگ می‌شود و هم در `cache.stats()` شمرده می‌شود.

## چرا OpenAI-compatible API

- یک SDK برای vision + speech-to-text + chat با یک کلید.
- Interface هر ماژول مستقل از provider است؛ عوض کردن مدل زیرین نیازی به تغییر schema عمومی ندارد.

## نقشه‌ی راه فیچرها

### موتور
1. ~~Retry/backoff~~ — ✅
2. ~~Cache تحلیل تصویر~~ — ✅ (دیسک، TTL، enable-flag، `cache.stats()` مشترک روی دیسک)
3. ~~پردازش ویدئو (فریم‌گیری)~~ — ✅ (`pipeline/video.py` + ffmpeg)
4. ~~تشخیص چند رنگ / variant از ست عکس~~ — ✅ (پرامپت vision+generate)
5. **مدل گفتار فارسی اختصاصی‌تر** اگر whisper برای لهجه‌های محلی کافی نبود
   (`CATALOGYAR_SPEECH_MODEL` از الان overrideپذیر است).

### محصول
6. ~~ویرایش خروجی + ثبت feedback~~ — ✅ (`PATCH /catalog/{id}` + جدول feedback + UI کم‌اطمینان)
7. ~~یادگیری سبک از تاریخچه فروشنده~~ — ✅ `seller_context` + `recent_feedback` در پرامپت generate
8. ~~خروجی/انتشار مارکت‌پلیس~~ — ✅ export + publish با URL از env (اتصال واقعی وابسته به credential)
9. ~~خروجی دو زبانه (FA + EN)~~ — ✅ فیلد `english`
10. ~~Auth و rate limiting~~ — ✅ Bearer API key
11. ~~اعتبارسنجی سخت دسته~~ — ✅ `enforce_category` روی `store_category_list`

### باقی‌مانده / سخت‌تر
- مدل گفتار فارسی اختصاصی‌تر از whisper (نیاز به انتخاب/هاست مدل جایگزین).
- یکپارچگی عمیق‌تر با API رسمی هر مارکت‌پلیس (الان POST عمومی با payload داخلی است؛ نیاز به credential و قرارداد رسمی).
