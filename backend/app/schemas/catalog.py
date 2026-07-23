from pydantic import BaseModel, Field


class Attribute(BaseModel):
    name: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


class Variant(BaseModel):
    type: str
    options: list[str]


class SourceEvidence(BaseModel):
    from_image: list[str] = []
    from_voice: list[str] = []
    from_text_on_package: list[str] = []


class Category(BaseModel):
    suggested: str
    confidence: float = Field(ge=0.0, le=1.0)


class CatalogGenerateRequest(BaseModel):
    seller_hint: str | None = None
    store_category_list: list[str] | None = None


class CatalogGenerateResponse(BaseModel):
    title: str
    category: Category
    description: str
    attributes: list[Attribute]
    variants: list[Variant]
    missing_info_questions: list[str]
    source_evidence: SourceEvidence
