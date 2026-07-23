"""تحلیل تصویر محصول: تشخیص نوع، رنگ، جنس ظاهری و متن روی بسته‌بندی.

نسخه‌ی MVP: این ماژول پشت یک interface ساده قرار دارد تا اتصال به مدل
چندوجهی واقعی (تصویر -> توصیف ساختاریافته) در فاز پیاده‌سازی جایگزین شود.
"""

from dataclasses import dataclass, field


@dataclass
class ImageAnalysis:
    detected_type: str | None = None
    colors: list[str] = field(default_factory=list)
    material_guess: str | None = None
    text_on_package: list[str] = field(default_factory=list)


def analyze_images(image_paths: list[str]) -> ImageAnalysis:
    """عکس‌های محصول را تحلیل کرده و شواهد بصری برمی‌گرداند.

    TODO: اتصال به مدل چندوجهی واقعی (vision model) در فاز پیاده‌سازی.
    """
    raise NotImplementedError("اتصال به مدل تحلیل تصویر هنوز پیاده‌سازی نشده است")
