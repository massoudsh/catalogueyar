from fastapi import FastAPI

from app.api.catalog import router as catalog_router

app = FastAPI(
    title="کاتالوگ‌یار API",
    description="دستیار هوشمند ساخت کاتالوگ محصول از روی عکس، ویدئو و ویس فروشنده",
    version="0.1.0",
)

app.include_router(catalog_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
