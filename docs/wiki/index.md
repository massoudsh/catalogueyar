# Index

## Overview
- [[overview]] — یک‌نگاه کلی کاتالوگ‌یار و معماری فعلی

## Entities (5 صفحه)
- [[entities/catalog-router]] — endpoint `POST /catalog/generate`، حالا واقعاً pipeline را صدا می‌زند
- [[entities/catalog-schemas]] — مدل‌های Pydantic ورودی/خروجی کاتالوگ
- [[entities/vision]] — تحلیل تصویر محصول با مدل vision واقعی (+ cache بر اساس hash محتوا)
- [[entities/speech]] — رونویسی ویس فارسی با مدل speech-to-text واقعی (+ retry)
- [[entities/generate]] — تولید خروجی نهایی کاتالوگ با مدل زبانی واقعی (+ retry)

## Concepts (2 صفحه)
- [[concepts/catalog-pipeline]] — فلو کامل ۴مرحله‌ای پردازش (vision → speech → merge → generate)
- [[concepts/engine-config]] — تنظیمات مدل/retry/cache (`config.py`)، خطاهای مشترک موتور
  (`errors.py`) و ماژول‌های مشترک `retry.py`/`cache.py`
