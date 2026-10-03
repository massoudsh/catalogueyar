import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.catalog import router as catalog_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Origins for the Vite frontend (comma-separated). Static UI on same origin needs no CORS.
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

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.router.routes.extend(catalog_router.routes)


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
