"""ادغام شواهد چندمنبعی (تصویر + صدا + راهنمای متنی فروشنده) به یک نمای واحد."""

from dataclasses import dataclass, field

from app.pipeline.vision import ImageAnalysis


@dataclass
class MergedEvidence:
    detected_type: str | None = None
    colors: list[str] = field(default_factory=list)
    material_guess: str | None = None
    text_on_package: list[str] = field(default_factory=list)
    voice_transcript: str | None = None
    seller_hint: str | None = None


def merge_evidence(
    image_analysis: ImageAnalysis,
    voice_transcript: str | None = None,
    seller_hint: str | None = None,
) -> MergedEvidence:
    """شواهد استخراج‌شده از منابع مختلف را در یک ساختار واحد ادغام می‌کند."""
    return MergedEvidence(
        detected_type=image_analysis.detected_type,
        colors=image_analysis.colors,
        material_guess=image_analysis.material_guess,
        text_on_package=image_analysis.text_on_package,
        voice_transcript=voice_transcript,
        seller_hint=seller_hint,
    )
