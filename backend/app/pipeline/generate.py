"""تولید خروجی ساختاریافته‌ی کاتالوگ از شواهد ادغام‌شده با یک مدل زبانی.

عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها و سؤالات تکمیلی را
از روی MergedEvidence می‌سازد.
"""

import json

from openai import OpenAI, OpenAIError

from app.config import GENERATE_MODEL, OPENAI_API_KEY
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.merge import MergedEvidence
from app.pipeline.retry import call_with_retry
from app.schemas.catalog import (
    Attribute,
    CatalogGenerateResponse,
    Category,
    SourceEvidence,
    Variant,
)

_SYSTEM_PROMPT = (
    "تو موتور تولید کاتالوگ محصول برای فروشنده‌های یک بازار آنلاین فارسی‌زبان هستی. "
    "از روی شواهد داده‌شده (تحلیل تصویر، متن پیاده‌شده از ویس، راهنمای فروشنده) یک "
    "پیش‌نویس کامل کاتالوگ بساز. فقط چیزهایی را با اطمینان بالا بنویس که واقعاً از "
    "شواهد قابل استنتاج است؛ حدس بی‌پایه نزن. اگر دسته‌بندی مجاز داده شده، مقدار "
    "suggested باید دقیقاً یکی از همان‌ها باشد. برای فیلدهایی که از هیچ منبعی قابل "
    "استخراج نیستند (مثل قیمت دقیق، موجودی، سایزبندی) به‌جای حدس، سؤال متناظر را در "
    "missing_info_questions بگذار. خروجی را فقط و دقیقاً به‌صورت یک JSON با این "
    "ساختار برگردان:\n"
    '{"title": "", "category": {"suggested": "", "confidence": 0.0}, '
    '"description": "", '
    '"attributes": [{"name": "", "value": "", "confidence": 0.0}], '
    '"variants": [{"type": "", "options": [""]}], '
    '"missing_info_questions": [""], '
    '"source_evidence": {"from_image": [""], "from_voice": [""], "from_text_on_package": [""]}}'
)


def _evidence_to_prompt(evidence: MergedEvidence, category_list: list[str] | None) -> str:
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
    return "\n".join(lines)


def generate_catalog(
    evidence: MergedEvidence,
    category_list: list[str] | None = None,
) -> CatalogGenerateResponse:
    """از شواهد ادغام‌شده یک پیش‌نویس کامل کاتالوگ می‌سازد.

    نیازمند متغیر محیطی ``OPENAI_API_KEY``. نام مدل با ``CATALOGYAR_GENERATE_MODEL``
    قابل تغییر است (پیش‌فرض: ``gpt-4o-mini``). فراخوانی مدل با retry/backoff
    (فقط روی خطای موقت شبکه/``429``/``5xx``) انجام می‌شود.
    """
    if not OPENAI_API_KEY:
        raise EngineNotConfiguredError(
            "متغیر محیطی OPENAI_API_KEY تنظیم نشده — بدون کلید نمی‌توان کاتالوگ تولید کرد"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    def _call_model() -> str:
        response = client.chat.completions.create(
            model=GENERATE_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _evidence_to_prompt(evidence, category_list)},
            ],
        )
        return response.choices[0].message.content or "{}"

    try:
        raw = call_with_retry(_call_model, operation="generate")
        data = json.loads(raw)
    except (OpenAIError, json.JSONDecodeError) as exc:
        raise EngineCallError(f"خطا در تولید کاتالوگ: {exc}") from exc

    return CatalogGenerateResponse(
        title=data.get("title", ""),
        category=Category(**(data.get("category") or {"suggested": "", "confidence": 0.0})),
        description=data.get("description", ""),
        attributes=[Attribute(**a) for a in data.get("attributes") or []],
        variants=[Variant(**v) for v in data.get("variants") or []],
        missing_info_questions=list(data.get("missing_info_questions") or []),
        source_evidence=SourceEvidence(**(data.get("source_evidence") or {})),
    )


__all__ = [
    "generate_catalog",
    "Attribute",
    "Category",
    "SourceEvidence",
    "Variant",
]
