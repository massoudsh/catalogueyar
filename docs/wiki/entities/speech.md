# Speech

> رونویسی ویس فارسی فروشنده به متن.

## مسئولیت‌ها
- `transcribe_voice(audio_path) -> str` — فقط وقتی [[entities/catalog-router]] ویس دریافت کند.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — خروجی وارد `merge.merge_evidence`
- [[concepts/engine-config]] — `OPENAI_API_KEY`, `CATALOGYAR_SPEECH_MODEL` (پیش‌فرض `whisper-1`)
- `backend/app/pipeline/retry.py` — `with_retry` دور `audio.transcriptions.create`

## قراردادها / Edge cases
- `language="fa"` صریح پاس داده می‌شود.
- فایل در هر تلاش retry دوباره باز می‌شود (داخل closure).
- بدون کلید → `EngineNotConfiguredError`؛ خطای مدل/IO → `EngineCallError`.

## منابع کد
- `backend/app/pipeline/speech.py` — `transcribe_voice`
