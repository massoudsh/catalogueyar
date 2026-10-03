# Generate

> تولید خروجی نهایی ساختاریافتهٔ کاتالوگ از شواهد ادغام‌شده.

## مسئولیت‌ها
- `generate_catalog(evidence, category_list=None, history=None) -> CatalogGenerateResponse`
- عنوان، دسته، توضیح، ویژگی‌ها، واریانت‌ها، سؤالات تکمیلی، `source_evidence` و `english`.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — آخرین مرحلهٔ مدل‌محور قبل از store
- [[entities/catalog-schemas]] — `CatalogGenerateResponse` / `EnglishCatalog`
- [[entities/storage]] — `seller_context` به‌عنوان `history` برای لحن/دسته
- [[concepts/engine-config]] — `OPENAI_API_KEY`, `CATALOGYAR_GENERATE_MODEL`
- `backend/app/pipeline/retry.py` — `call_with_retry`

## قراردادها / Edge cases
- پرامپت: فقط از شواهد؛ چند رنگ → `variants` با type رنگ؛ نسخهٔ انگلیسی در `english`.
- اگر `category_list` باشد، `suggested` باید یکی از همان‌ها باشد (قید prompt، نه validation سخت).
- اگر `history` بیاید، عنوان و دستهٔ چند draft اخیر به پرامپت اضافه می‌شود.
- JSON نامعتبر یا خطای مدل → `EngineCallError`؛ بدون کلید → `EngineNotConfiguredError`.
- cache ندارد (ورودی متنی؛ تکرار یکسان کم است).

## منابع کد
- `backend/app/pipeline/generate.py` — `generate_catalog`
