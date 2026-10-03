import json

from openai import OpenAI, OpenAIError

from app.config import GENERATE_MODEL, OPENAI_API_KEY
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.merge import MergedEvidence
from app.pipeline.retry import with_retry
from app.schemas.catalog import (
    Attribute,
    CatalogGenerateResponse,
    Category,
    EnglishCatalog,
    SourceEvidence,
    Variant,
)

_SYSTEM_PROMPT = (
    "تو موتور تولید کاتالوگ محصول برای فروشنده‌های یک بازار آنلاین فارسی‌زبان هستی. "
    "فقط بر اساس شواهد داده‌شده بنویس و حدس بی‌پایه نزن. اگر دسته‌بندی مجاز داده شده، suggested باید دقیقاً یکی از همان‌ها باشد. "
    "اگر چند رنگ در شواهد وجود دارد، آن‌ها را در variants با type رنگ قرار بده. "
    "همچنین نسخه انگلیسی title و description و attributes را در english تولید کن. "
    "برای اطلاعات ناموجود سؤال را در missing_info_questions بگذار. فقط JSON برگردان:\n"
    '{"title":"", "category":{"suggested":"","confidence":0.0}, "description":"", '
    '"attributes":[{"name":"","value":"","confidence":0.0}], '
    '"variants":[{"type":"","options":[""]}], "missing_info_questions":[""], '
    '"source_evidence":{"from_image":[""],"from_voice":[""],"from_text_on_package":[""]}, '
    '"english":{"title":"","description":"","attributes":[{"name":"","value":"","confidence":0.0}]}}'
)


def _evidence_to_prompt(
    evidence: MergedEvidence,
    category_list: list[str] | None,
    history: list[CatalogGenerateResponse] | None = None,
) -> str:
    lines = [
        f"نوع تشخیص‌داده‌شده از تصویر: {evidence.detected_type or 'نامشخص'}",
        f"رنگ‌های تشخیص‌داده‌شده: {', '.join(evidence.colors) or 'ندارد'}",
        f"حدس جنس ظاهری: {evidence.material_guess or 'نامشخص'}",
        f"متن روی بسته‌بندی: {', '.join(evidence.text_on_package) or 'ندارد'}",
        f"متن پیاده‌شده از ویس فروشنده: {evidence.voice_transcript or 'ندارد'}",
        f"راهنمای متنی فروشنده: {evidence.seller_hint or 'ندارد'}",
    ]
    if category_list:
        lines.append("دسته‌بندی‌های مجاز پلتفرم: " + ", ".join(category_list))
    if history:
        lines.append("نمونه‌های اخیر همین فروشنده برای حفظ لحن و دسته‌بندی:")
        lines.extend(f"- {item.title} | {item.category.suggested}" for item in history)
    return "\n".join(lines)


def _attributes(items: list[dict]) -> list[Attribute]:
    return [Attribute(**item) for item in items or []]


def generate_catalog(
    evidence: MergedEvidence,
    category_list: list[str] | None = None,
    history: list[CatalogGenerateResponse] | None = None,
) -> CatalogGenerateResponse:
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان کاتالوگ تولید کرد"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    def call_model():
        return client.chat.completions.create(
            model=GENERATE_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _evidence_to_prompt(evidence, category_list, history)},
            ],
        )

    try:
        response = with_retry(call_model)
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
    except (OpenAIError, json.JSONDecodeError, TypeError) as exc:
        raise EngineCallError(f"خطا در تولید کاتالوگ: {exc}") from exc

    english = data.get("english")
    return CatalogGenerateResponse(
        title=data.get("title", ""),
        category=Category(**(data.get("category") or {"suggested": "", "confidence": 0.0})),
        description=data.get("description", ""),
        attributes=_attributes(data.get("attributes") or []),
        variants=[Variant(**variant) for variant in data.get("variants") or []],
        missing_info_questions=list(data.get("missing_info_questions") or []),
        source_evidence=SourceEvidence(**(data.get("source_evidence") or {})),
        english=EnglishCatalog(
            title=english.get("title", ""),
            description=english.get("description", ""),
            attributes=_attributes(english.get("attributes") or []),
        ) if english else None,
    )
