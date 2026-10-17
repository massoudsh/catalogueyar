import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.catalog import router as catalog_router

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = BASE_DIR.parents[1] / "frontend" / "dist"

# Origins for the Vite frontend (comma-separated). Production uses same-origin assets.
_CORS_DEFAULT = "http://127.0.0.1:5173,http://localhost:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CATALOGYAR_CORS_ORIGINS", _CORS_DEFAULT).split(",")
    if origin.strip()
]

app = FastAPI(
    title="کاتالوگ‌یار API",
    description="دستیار هوشمند ساخت کاتالوگ محصول از روی عکس، ویدئو و ویس فروشنده",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.router.routes.extend(catalog_router.routes)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{path:path}", include_in_schema=False)
async def frontend(path: str) -> FileResponse:
    index_file = FRONTEND_DIST_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=503, detail="Frontend assets are not built")

    requested_file = (FRONTEND_DIST_DIR / path).resolve()
    try:
        requested_file.relative_to(FRONTEND_DIST_DIR.resolve())
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Not found") from error

    if path and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(index_file)
