# مرجع API — کاتالوگ‌یار

Base URL محلی: `http://127.0.0.1:8000`  
OpenAPI خودکار: `/docs`

## احراز هویت
هدر اختیاری مگر اینکه `CATALOGYAR_API_KEYS` تنظیم شده باشد:

```
Authorization: Bearer <api_key>
```

بدون پیکربندی کلید، همه درخواست‌ها با `seller_id=development` پذیرفته می‌شوند. عبور از
`CATALOGYAR_RATE_LIMIT_PER_MINUTE` → `429`.

## Health و UI
| روش | مسیر | توضیح |
|---|---|---|
| GET | `/` و `/workspace` | رابط React/Vite از `frontend/dist`؛ بدون build: `503` |
| GET | `/health` | `{"status":"ok"}` |

React/Vite در production از همان origin API سرو می‌شود؛ asset یا مسیر ناشناخته `404` است، نه HTML لندینگ. در توسعه، Vite روی `5173` مسیرهای `/catalog` و `/health` را proxy می‌کند.
CORS با `CATALOGYAR_CORS_ORIGINS` (پیش‌فرض `http://127.0.0.1:5173,http://localhost:5173`)
فعال است. راهنما: `frontend/README.md`.

## کاتالوگ

### `POST /catalog/generate`
Multipart form:

| فیلد | نوع | اجباری | توضیح |
|---|---|---|---|
| `images` | فایل(ها) | بله | ۱ تا ۵ عکس یا ویدئو |
| `voice_note` | فایل صوتی | خیر | ویس فارسی |
| `seller_hint` | form string | خیر | راهنمای متنی کوتاه |
| `store_category_list` | form string (تکرارپذیر) | خیر | دسته‌های مجاز پلتفرم |

پاسخ: `CatalogGenerateResponse` (عنوان، دسته، توضیح، attributes، variants،
`missing_info_questions`، `source_evidence`، `english`، و `draft_id` برای ویرایش بعدی).
سه فیلد محتوایی نیز برمی‌گردند: `short_description` (رشته)، `seo_keywords` (آرایهٔ رشته) و
`faqs` (آرایهٔ `{question, answer}`). برای draftهای قدیمی، مقدار پیش‌فرض رشتهٔ خالی و آرایه‌های خالی است.
این محتوا از مدل است و پیش از انتشار باید بازبینی شود؛ تضمین صحت یا رتبهٔ SEO نیست.
اگر `store_category_list` داده شود، `category.suggested` حتماً یکی از همان‌ها خواهد بود.
Draft هم‌زمان در SQLite ذخیره می‌شود؛ اصلاح‌های PATCH قبلی فروشنده وارد پرامپت generate می‌شوند.

خطاها: `400` تعداد مدیا؛ `401` کلید؛ `429` نرخ؛ `503` بدون `OPENAI_API_KEY`؛ `502` مدل/ffmpeg.

### `GET /catalog/history`
لیست `CatalogDraft[]` فروشندهٔ فعلی (حداکثر ۲۰).

### `GET /catalog/{draft_id}`
یک draft؛ `404` اگر نباشد یا مال seller دیگر باشد.

### `PATCH /catalog/{draft_id}`
بدنهٔ JSON جزئی (`CatalogUpdate`): هر یک از `title`, `description`, `category`, `attributes`,
`variants`, `missing_info_questions`, `english`, `short_description`, `seo_keywords`, `faqs`.
تغییرات پس از اعتبارسنجی مدل‌های تو‌در‌تو در جدول feedback ثبت می‌شود؛ FAQ بدون `question` یا `answer` به `422` می‌انجامد.

### `GET /catalog/{draft_id}/export/{marketplace}`
`marketplace` ∈ `digikala` | `basalam` | `torob`.  
برمی‌گرداند payload JSON شامل محتوای SEO/FAQ بدون تماس بیرونی. نام ناشناخته → `400`.
فرمت خروجی برای هر سه نام یکسان و عمومی است؛ سازگاری با API رسمی بازارگاه‌ها تضمین نشده و به آداپتر سفارشی نیاز دارد.

### `POST /catalog/{draft_id}/publish/{marketplace}`
همان payload را به URL/token تنظیم‌شده در env POST می‌کند.  
بدون endpoint یا خطای شبکه → `502`. موفقیت:
`{"marketplace":"…","status":"published","response":"…"}`.

## مدل‌های پاسخ (خلاصه)
جزئیات فیلدها در `docs/mvp-design.md` و `docs/wiki/entities/catalog-schemas.md`.
نسخهٔ انگلیسی در فیلد اختیاری `english` است.

## پیکربندی مرتبط
Auth، retry، cache تصویر و endpointهای مارکت‌پلیس از env خوانده می‌شوند — جدول خلاصه در
`README.md`، مرجع کامل در `backend/.env.example` و `docs/wiki/concepts/engine-config.md`.
