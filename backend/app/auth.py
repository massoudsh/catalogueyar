import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException

from app.config import API_KEYS, RATE_LIMIT_PER_MINUTE

_request_times: dict[str, deque[float]] = defaultdict(deque)


def _keys() -> dict[str, str]:
    return {entry.split(":", 1)[0]: entry.split(":", 1)[1] for entry in API_KEYS.split(",") if ":" in entry}


def current_seller(authorization: str | None = Header(default=None)) -> str:
    configured = _keys()
    if not configured:
        seller_id = "development"
    else:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer API key لازم است")
        token = authorization.removeprefix("Bearer ")
        seller_id = next((seller for seller, key in configured.items() if key == token), "")
        if not seller_id:
            raise HTTPException(status_code=401, detail="API key نامعتبر است")

    now = time.monotonic()
    requests = _request_times.setdefault(seller_id, deque())
    while requests and now - requests[0] >= 60:
        requests.popleft()
    if len(requests) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="تعداد درخواست‌ها بیش از حد مجاز است")
    requests.append(now)
    return seller_id
