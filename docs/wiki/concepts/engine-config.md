# Engine Config

> تنظیمات env، خطاهای مشترک موتور، retry و cache تصویر.

## `backend/app/config.py`
همه از محیط؛ نمونه در `backend/.env.example`:

| متغیر | نقش | پیش‌فرض |
|---|---|---|
| `OPENAI_API_KEY` | کلید مدل؛ بدون آن vision/speech/generate → `EngineNotConfiguredError` | — |
| `CATALOGYAR_VISION_MODEL` | مدل vision | `gpt-4o-mini` |
| `CATALOGYAR_SPEECH_MODEL` | مدل speech | `whisper-1` |
| `CATALOGYAR_GENERATE_MODEL` | مدل generate | `gpt-4o-mini` |
| `CATALOGYAR_DATA_DIR` | ریشهٔ دادهٔ محلی | `/tmp/catalogyar` |
| `CATALOGYAR_DATABASE_PATH` | فایل SQLite | `$DATA_DIR/catalogyar.sqlite3` |
| `CATALOGYAR_VISION_CACHE_DIR` | دایرکتوری cache تصویر | `$DATA_DIR/vision-cache` |
| `CATALOGYAR_API_KEYS` | `seller:key,...` برای [[entities/auth]] | خالی = development |
| `CATALOGYAR_RATE_LIMIT_PER_MINUTE` | سقف درخواست / seller / دقیقه | `30` |
| `CATALOGYAR_REQUEST_TIMEOUT_SECONDS` | timeout publish مارکت‌پلیس | `12` |
| `DIGIKALA_PUBLISH_URL` / `DIGIKALA_TOKEN` | انتشار دیجی‌کالا | خالی |
| `BASALAM_PUBLISH_URL` / `BASALAM_TOKEN` | انتشار باسلام | خالی |
| `TOROB_PUBLISH_URL` / `TOROB_TOKEN` | انتشار ترب | خالی |

## خطاها — `pipeline/errors.py`
- `EngineNotConfiguredError` → HTTP `503` در router.
- `EngineCallError` → HTTP `502` (مدل، ffmpeg، یا publish).

## Retry — `pipeline/retry.py`
- `with_retry(operation, attempts=3, base_delay=0.2)` — فقط روی
  `APIConnectionError` / `APITimeoutError` / `RateLimitError` / `TimeoutError` / `ConnectionError`.
- backoff نمایی ساده: `base_delay * 2**attempt`. بعد از اتمام تلاش‌ها همان exception اصلی raise می‌شود.
- تلاش‌ها و delay در کد hard-coded است (دیگر envهای `MODEL_MAX_ATTEMPTS` نیستند).

## Cache تصویر — `pipeline/cache.py`
- کلید از hash محتوای فایل‌ها (مسیرها sorted)؛ فایل JSON در `VISION_CACHE_DIR`.
- بدون TTL و بدون flag خاموش/روشن جدا؛ نوشتن اتمیک.
- مصرف فقط در [[entities/vision]].

## منابع کد
- `backend/app/config.py`
- `backend/app/pipeline/errors.py`
- `backend/app/pipeline/retry.py`
- `backend/app/pipeline/cache.py`
