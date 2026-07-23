"""تولید خروجی ساختاریافته‌ی کاتالوگ از شواهد ادغام‌شده.

عنوان، دسته‌بندی، توضیح، ویژگی‌ها، واریانت‌ها و سؤالات تکمیلی را
از روی MergedEvidence می‌سازد.

نسخه‌ی MVP: این ماژول پشت یک interface ساده قرار دارد تا اتصال به مدل
زبانی واقعی (تولید متن ساختاریافته) در فاز پیاده‌سازی جایگزین شود.
"""

from app.pipeline.merge import MergedEvidence
from app.schemas.catalog import (
    Attribute,
    CatalogGenerateResponse,
    Category,
    SourceEvidence,
    Variant,
)


def generate_catalog(
    evidence: MergedEvidence,
    category_list: list[str] | None = None,
) -> CatalogGenerateResponse:
    """از شواهد ادغام‌شده یک پیش‌نویس کامل کاتالوگ می‌سازد.

    TODO: اتصال به مدل زبانی واقعی برای تولید عنوان/توضیح/ویژگی در فاز پیاده‌سازی.
    """
    raise NotImplementedError("موتور تولید کاتالوگ هنوز پیاده‌سازی نشده است")


__all__ = [
    "generate_catalog",
    "Attribute",
    "Category",
    "SourceEvidence",
    "Variant",
]
