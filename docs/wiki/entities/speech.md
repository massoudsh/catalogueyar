# Speech

> رونویسی ویس فارسی فروشنده به متن.

## مسئولیت‌ها
- `transcribe_voice(audio_path) -> str` — قدم دوم pipeline (اختیاری، فقط اگر ویس ارسال شده).

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — دومین مرحله (خروجی‌اش وارد `merge.merge_evidence` می‌شود)

## قراردادها / Edge cases
- فعلاً `NotImplementedError` — پشت interface ساده تا به مدل تشخیص گفتار فارسی واقعی وصل شود.
- ویس اختیاری است؛ اگر فروشنده ویس نفرستد این مرحله اصلاً صدا زده نمی‌شود.

## منابع کد
- `backend/app/pipeline/speech.py:8` — `transcribe_voice`
