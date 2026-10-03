# Index

## Overview
- [[overview]] — یک‌نگاه کلی کاتالوگ‌یار و معماری فعلی

## Entities
- [[entities/catalog-router]] — endpointهای `/catalog/*` (generate/history/edit/export/publish)
- [[entities/catalog-schemas]] — مدل‌های Pydantic ورودی/خروجی، Draft و Update
- [[entities/auth]] — Bearer API key seller-scoped و rate limit
- [[entities/storage]] — SQLite drafts، feedback و seller_context
- [[entities/marketplaces]] — export/publish به digikala / basalam / torob
- [[entities/video]] — تشخیص ویدئو و فریم‌گیری با ffmpeg
- [[entities/vision]] — تحلیل تصویر محصول (+ cache روی دیسک)
- [[entities/speech]] — رونویسی ویس فارسی (+ retry)
- [[entities/generate]] — تولید کاتالوگ نهایی (+ english + تاریخچه‌ی فروشنده)

## Concepts
- [[concepts/catalog-pipeline]] — فلو پردازش (video → vision → speech → merge → generate → store)
- [[concepts/engine-config]] — تنظیمات env، خطاهای موتور، retry و cache
