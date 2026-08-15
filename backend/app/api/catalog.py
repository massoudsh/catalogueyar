"""API endpoint: POST /catalog/generate — ساخت کاتالوگ از عکس(ها) و ویس اختیاری."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.generate import generate_catalog
from app.pipeline.merge import merge_evidence
from app.pipeline.speech import transcribe_voice
from app.pipeline.vision import analyze_images
from app.schemas.catalog import CatalogGenerateResponse

router = APIRouter(prefix="/catalog", tags=["catalog"])


async def _write_temp(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await upload.read())
        return tmp.name


@router.post("/generate", response_model=CatalogGenerateResponse)
async def generate_catalog_endpoint(
    images: list[UploadFile] = File(..., description="۱ تا ۵ عکس محصول"),
    voice_note: UploadFile | None = File(None, description="ویس فارسی اختیاری"),
    seller_hint: str | None = Form(None),
    store_category_list: list[str] | None = Form(None),
) -> CatalogGenerateResponse:
    if not images or len(images) > 5:
        raise HTTPException(status_code=400, detail="باید بین ۱ تا ۵ عکس ارسال شود")

    temp_paths: list[str] = []
    try:
        image_paths = [await _write_temp(image) for image in images]
        temp_paths.extend(image_paths)

        voice_path: str | None = None
        if voice_note is not None:
            voice_path = await _write_temp(voice_note)
            temp_paths.append(voice_path)

        image_analysis = analyze_images(image_paths)
        voice_transcript = transcribe_voice(voice_path) if voice_path else None
        evidence = merge_evidence(image_analysis, voice_transcript, seller_hint)
        return generate_catalog(evidence, store_category_list)

    except EngineNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EngineCallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        for path in temp_paths:
            Path(path).unlink(missing_ok=True)
