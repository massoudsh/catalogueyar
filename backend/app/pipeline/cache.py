import hashlib
import json
import os
from pathlib import Path
from typing import Any

from app.config import VISION_CACHE_DIR


def cache_key(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        payload = Path(path).read_bytes()
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def read_cache(key: str) -> dict[str, Any] | None:
    path = VISION_CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_cache(key: str, payload: dict[str, Any]) -> None:
    VISION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = VISION_CACHE_DIR / f"{key}.json"
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)
