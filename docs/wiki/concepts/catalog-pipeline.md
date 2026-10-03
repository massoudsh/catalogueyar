# Catalog Pipeline

> فلو از اولین آپلود مدیا تا draft ذخیره‌شدهٔ کاتالوگ.

## مراحل
1. **auth** — [[entities/auth]] تعیین `seller_id` و اعمال rate limit.
2. **video (اختیاری per-file)** — [[entities/video]] اگر پسوند ویدئو باشد → تا ۵ فریم JPG.
3. **vision** — [[entities/vision]] `analyze_images(image_paths) -> ImageAnalysis` (+ cache).
4. **speech (اختیاری)** — [[entities/speech]] `transcribe_voice` اگر ویس آمده باشد.
5. **merge** — `merge_evidence(image_analysis, voice_transcript, seller_hint) -> MergedEvidence`
   در `backend/app/pipeline/merge.py`؛ بدون فراخوانی مدل.
6. **generate** — [[entities/generate]] با `seller_context(seller_id)` به‌عنوان history.
7. **store** — [[entities/storage]] `create_draft`؛ پاسخ همان `CatalogGenerateResponse` است
   (metadata draft از history/detail خوانده می‌شود).

## اتصال به API
[[entities/catalog-router]] این مراحل را برای `POST /catalog/generate` پشت‌سرهم اجرا می‌کند و
فایل‌های موقت/فریم‌ها را در `finally` پاک می‌کند. مسیرهای بعدی (history/edit/export/publish)
روی draft ذخیره‌شده کار می‌کنند، نه دوباره روی pipeline کامل.

## خطاها
نگاه کنید به [[concepts/engine-config]]: کلید مفقود → `503`؛ مدل/ffmpeg/publish → `502`؛
ورودی نامعتبر → `400`؛ draft گم → `404`؛ rate limit → `429`.

## آزمون‌پذیری
`backend/tests/test_pipeline.py` با mock OpenAI قرارداد vision/speech/generate، ادغام شواهد،
storage و مسیرهای خطا را می‌سنجد.

## منابع کد
- `backend/app/api/catalog.py` — orchestration
- `backend/app/pipeline/merge.py` — ادغام شواهد
- `docs/mvp-design.md` — طراحی اولیهٔ ۷مرحله‌ای محصول
- `docs/api.md` — مرجع HTTP
