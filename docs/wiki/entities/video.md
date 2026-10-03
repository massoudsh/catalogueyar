# Video

> تشخیص فایل ویدئو و استخراج فریم برای تغذیهٔ مرحلهٔ vision.

## مسئولیت‌ها
- `is_video(path)` — پسوند در `{.mp4,.mov,.m4v,.webm,.avi,.mkv}`.
- `extract_video_frames(video_path, output_dir, max_frames=5)` — ffmpeg با `fps=1`،
  scale حداکثر عرض ۱۰۲۴، خروجی `frame-%02d.jpg`.

## وابستگی‌ها
- [[entities/catalog-router]] — قبل از vision، هر آپلود ویدئویی را به فریم تبدیل می‌کند
- [[concepts/catalog-pipeline]] — مرحلهٔ پیش‌پردازش مدیا
- [[concepts/engine-config]] — خطاها با `EngineCallError` به `502` map می‌شوند

## قراردادها / Edge cases
- بدون باینری `ffmpeg` در PATH → `EngineCallError` («ffmpeg … نصب نیست»).
- شکست subprocess یا صفر فریم → `EngineCallError`.
- timeout استخراج ۳۰ ثانیه.
- فریم‌ها در پوشهٔ موقت router ساخته و در `finally` همراه آپلودها پاک می‌شوند.
- ویدئو داخل محدودهٔ همان سقف ۱–۵ فایل آپلودی است (هر فایل ویدئو تا ۵ فریم می‌سازد؛ مجموع
  فریم‌ها می‌تواند از ۵ بیشتر شود اگر چند ویدئو بیاید).

## منابع کد
- `backend/app/pipeline/video.py`
