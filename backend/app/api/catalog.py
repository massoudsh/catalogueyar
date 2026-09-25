import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import current_seller
from app.marketplaces import export_payload, publish
from app.pipeline.errors import EngineCallError, EngineNotConfiguredError
from app.pipeline.generate import generate_catalog
from app.pipeline.merge import merge_evidence
from app.pipeline.speech import transcribe_voice
from app.pipeline.video import extract_video_frames, is_video
from app.pipeline.vision import analyze_images
from app.schemas.catalog import CatalogDraft, CatalogGenerateResponse, CatalogUpdate
from app.storage import create_draft, get_draft, list_drafts, seller_context, update_draft

router = APIRouter(prefix="/catalog", tags=["catalog"])


async def _write_temp(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower() or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(upload.file, tmp)
        return tmp.name


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="کاتالوگ پیدا نشد")


@router.post("/generate", response_model=CatalogGenerateResponse)
async def generate_catalog_endpoint(
    images: list[UploadFile] = File(..., description="۱ تا ۵ عکس یا ویدئوی محصول"),
    voice_note: UploadFile | None = File(None, description="ویس فارسی اختیاری"),
    seller_hint: str | None = Form(None),
    store_category_list: list[str] | None = Form(None),
    seller_id: str = Depends(current_seller),
) -> CatalogGenerateResponse:
    if not images or len(images) > 5:
        raise HTTPException(status_code=400, detail="باید بین ۱ تا ۵ تصویر یا ویدئو ارسال شود")

    temp_paths: list[str] = []
    frame_dir = Path(tempfile.mkdtemp(prefix="catalogyar-frames-"))
    try:
        media_paths = [await _write_temp(image) for image in images]
        temp_paths.extend(media_paths)
        image_paths: list[str] = []
        for media_path in media_paths:
            if is_video(media_path):
                frames = extract_video_frames(media_path, str(frame_dir))
                image_paths.extend(frames)
                temp_paths.extend(frames)
            else:
                image_paths.append(media_path)

        voice_path: str | None = None
        if voice_note is not None:
            voice_path = await _write_temp(voice_note)
            temp_paths.append(voice_path)

        image_analysis = analyze_images(image_paths)
        voice_transcript = transcribe_voice(voice_path) if voice_path else None
        evidence = merge_evidence(image_analysis, voice_transcript, seller_hint)
        catalog = generate_catalog(evidence, store_category_list, seller_context(seller_id))
        create_draft(seller_id, catalog)
        return catalog
    except EngineNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EngineCallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        for path in temp_paths:
            Path(path).unlink(missing_ok=True)
        shutil.rmtree(frame_dir, ignore_errors=True)


@router.get("/history", response_model=list[CatalogDraft])
async def catalog_history(seller_id: str = Depends(current_seller)) -> list[CatalogDraft]:
    return list_drafts(seller_id)


@router.get("/{draft_id}", response_model=CatalogDraft)
async def catalog_detail(draft_id: str, seller_id: str = Depends(current_seller)) -> CatalogDraft:
    draft = get_draft(seller_id, draft_id)
    if draft is None:
        raise _not_found()
    return draft


@router.patch("/{draft_id}", response_model=CatalogDraft)
async def edit_catalog(draft_id: str, update: CatalogUpdate, seller_id: str = Depends(current_seller)) -> CatalogDraft:
    draft = update_draft(seller_id, draft_id, update)
    if draft is None:
        raise _not_found()
    return draft


@router.get("/{draft_id}/export/{marketplace}")
async def export_catalog(draft_id: str, marketplace: str, seller_id: str = Depends(current_seller)) -> dict:
    draft = get_draft(seller_id, draft_id)
    if draft is None:
        raise _not_found()
    try:
        return export_payload(marketplace, draft.catalog)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{draft_id}/publish/{marketplace}")
async def publish_catalog(draft_id: str, marketplace: str, seller_id: str = Depends(current_seller)) -> dict:
    draft = get_draft(seller_id, draft_id)
    if draft is None:
        raise _not_found()
    try:
        return publish(marketplace, draft.catalog)
    except (ValueError, EngineCallError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
