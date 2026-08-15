# Speech

> رونویسی ویس فارسی فروشنده به متن.

## مسئولیت‌ها
- `transcribe_voice(audio_path) -> str` — قدم دوم pipeline (اختیاری، فقط اگر ویس ارسال شده).

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — دومین مرحله (خروجی‌اش وارد `merge.merge_evidence` می‌شود)
- [[concepts/engine-config]] — `OPENAI_API_KEY` و `CATALOGYAR_SPEECH_MODEL` (پیش‌فرض `whisper-1`)

## قراردادها / Edge cases
- `language="fa"` صریح به مدل پاس داده می‌شود.
- ویس اختیاری است؛ اگر فروشنده ویس نفرستد این مرحله اصلاً صدا زده نمی‌شود.
- بدون `OPENAI_API_KEY` → `EngineNotConfiguredError`؛ خطای شبکه/مدل → `EngineCallError`.

## منابع کد
- `backend/app/pipeline/speech.py:8` — `transcribe_voice`
