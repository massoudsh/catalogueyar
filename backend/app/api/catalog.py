"""API endpoint: POST /catalog/generate — ساخت کاتالوگ از عکس(ها) و ویس اختیاری."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.catalog import CatalogGenerateResponse

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/generate", response_model=CatalogGenerateResponse)
async def generate_catalog_endpoint(
    images: list[UploadFile] = File(..., description="۱ تا ۵ عکس محصول"),
    voice_note: UploadFile | None = File(None, description="ویس فارسی اختیاری"),
    seller_hint: str | None = Form(None),
) -> CatalogGenerateResponse:
    if not images or len(images) > 5:
        raise HTTPException(status_code=400, detail="باید بین ۱ تا ۵ عکس ارسال شود")

    # TODO: ذخیره‌ی موقت فایل‌ها و اتصال pipeline واقعی (vision -> speech -> merge -> generate)
    raise HTTPException(status_code=501, detail="این قابلیت هنوز پیاده‌سازی نشده است (MVP در حال ساخت)")
