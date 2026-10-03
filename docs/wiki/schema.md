# Schema — قوانین ویکی این پروژه

منبع کامل قوانین در `/CLAUDE.md` (ریشه‌ی پروژه) است — همان‌جا را برای جزئیات کامل بخوان.
این فایل فقط تنظیمات مخصوص «کاتالوگ‌یار» را نگه می‌دارد.

## گروه‌بندی entity ها در این پروژه
- **api** — routerهای FastAPI (`entities/catalog-router.md`)
- **schema** — مدل‌های Pydantic (`entities/catalog-schemas.md`)
- **pipeline** — مراحل پردازش (video, vision, speech, merge, generate + retry/cache)
- **platform** — auth، storage، marketplaces

## قرارداد نام‌گذاری فایل
`{نام-کوتاه-کباب-کیس}.md` — مثال: `catalog-router.md`, `engine-config.md`.

## وضعیت فعلی پروژه (برای زمینه‌ی lint)
موتور واقعی وصل است (دیگر اسکلت/۵۰۱ نیست). ویکی باید endpointهای history/edit/export/publish،
ویدئو، auth، SQLite و فیلد `english` را پوشش دهد. نقطهٔ شروع: [[overview]] و [[index]].
