import json
from urllib import request

from app.config import MARKETPLACE_ENDPOINTS, MARKETPLACE_TOKENS, REQUEST_TIMEOUT_SECONDS
from app.pipeline.errors import EngineCallError
from app.schemas.catalog import CatalogGenerateResponse

SUPPORTED_MARKETPLACES = frozenset(MARKETPLACE_ENDPOINTS)


def export_payload(marketplace: str, catalog: CatalogGenerateResponse) -> dict:
    if marketplace not in SUPPORTED_MARKETPLACES:
        raise ValueError(f"marketplace پشتیبانی نمی‌شود: {marketplace}")
    return {
        "title": catalog.title,
        "description": catalog.description,
        "category": catalog.category.suggested,
        "attributes": [attribute.model_dump() for attribute in catalog.attributes],
        "variants": [variant.model_dump() for variant in catalog.variants],
        "english": catalog.english.model_dump() if catalog.english else None,
    }


def publish(marketplace: str, catalog: CatalogGenerateResponse) -> dict:
    payload = export_payload(marketplace, catalog)
    endpoint = MARKETPLACE_ENDPOINTS[marketplace]
    if not endpoint:
        raise EngineCallError(f"endpoint انتشار {marketplace} تنظیم نشده است")
    headers = {"Content-Type": "application/json"}
    if MARKETPLACE_TOKENS[marketplace]:
        headers["Authorization"] = f"Bearer {MARKETPLACE_TOKENS[marketplace]}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
    except Exception as exc:
        raise EngineCallError(f"خطا در انتشار در {marketplace}: {exc}") from exc
    return {"marketplace": marketplace, "status": "published", "response": response_body}
