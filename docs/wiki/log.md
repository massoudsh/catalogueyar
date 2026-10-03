# Log

## [2026-08-15] update | راه‌اندازی ویکی دانش پروژه (docs/wiki/) طبق Vault Recipe؛ مستندسازی اسکلت فعلی backend (router, schemas, ۴ ماژول pipeline)
## [2026-08-15] update | موتور واقعی وصل شد (vision/speech/generate → OpenAI-compatible API)، config.py + errors.py اضافه شد، endpoint دیگر 501 نمی‌دهد؛ تحقیق رقبا و roadmap فیچر در docs/
## [2026-08-23] update | تست‌های واحد mock شده برای pipeline vision/speech/generate و مسیرهای خطا اضافه شد.
## [2026-09-19] update | issue #1 بسته شد: `pipeline/retry.py` (`call_with_retry`) — retry/backoff نمایی با jitter فقط روی خطای موقت (شبکه/`429`/`5xx`؛ `4xx` کلاینت و JSON نامعتبر بدون retry)، قابل تنظیم با `CATALOGYAR_MODEL_MAX_ATTEMPTS`/`..._BASE_DELAY`/`..._MAX_DELAY` و هرگز بی‌نهایت. در vision/speech/generate وصل شد.
## [2026-09-19] update | issue #2 بسته شد: `pipeline/cache.py` — cache تحلیل تصویر بر اساس SHA-256 بایت‌های عکس + مدل + `_ANALYSIS_CACHE_VERSION`، فایل JSON روی دیسک با TTL (`CATALOGYAR_IMAGE_CACHE_TTL_SECONDS`)، افت امن به فراخوانی عادی مدل در هر خطای I/O، و observability با لاگ hit/miss و `cache.stats()`. صفحات [[concepts/engine-config]]، [[entities/vision]]، [[entities/speech]]، [[entities/generate]]، [[overview]] و [[index]] آپدیت شدند؛ `docs/engine-design.md` دو آیتم اول roadmap را «انجام‌شده» علامت زد.
