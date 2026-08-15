# Generate

> تولید خروجی نهایی و ساختاریافته‌ی کاتالوگ از شواهد ادغام‌شده.

## مسئولیت‌ها
- `generate_catalog(evidence: MergedEvidence, category_list=None) -> CatalogGenerateResponse`
- آخرین مرحله‌ی pipeline؛ عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها و سؤالات تکمیلی را می‌سازد.

## وابستگی‌ها
- [[concepts/catalog-pipeline]] — مرحله‌ی چهارم/آخر
- [[entities/catalog-schemas]] — همین schema `CatalogGenerateResponse` را پر می‌کند
- [[concepts/engine-config]] — `OPENAI_API_KEY` و `CATALOGYAR_GENERATE_MODEL`

## قراردادها / Edge cases
- پرامپت صریحاً از مدل می‌خواهد فقط از شواهد استنتاج کند و برای فیلدهای غیرقابل‌استخراج
  (قیمت، موجودی، سایز دقیق) سؤال در `missing_info_questions` بگذارد، نه حدس بزند.
- اگر `category_list` داده شده، از مدل خواسته می‌شود `suggested` را دقیقاً از همان لیست انتخاب کند
  (ولی این قید سمت prompt است، نه اعتبارسنجی سخت در کد — ریسک شناخته‌شده، در roadmap).
- خروجی JSON parse و به مدل‌های Pydantic (`Attribute`, `Variant`, `Category`, `SourceEvidence`) map می‌شود.

## منابع کد
- `backend/app/pipeline/generate.py:20` — `generate_catalog`
