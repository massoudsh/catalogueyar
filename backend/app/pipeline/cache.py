"""Cache تحلیل تصویر بر اساس hash محتوا.

کلید cache از SHA-256 **بایت‌های عکس‌ها** (+ نام مدل + نسخه‌ی schema/prompt) ساخته می‌شود، نه از
نام یا مسیر فایل؛ پس همان عکس با اسم/مسیر دیگر هم cache hit می‌شود. ترتیب عکس‌ها بخشی از کلید است.

Backend: فایل JSON روی دیسک — بدون dependency جدید (نه Redis و نه DB در این ریپو موجود نیست).
هر ورودی یک فایل ``<key>.json`` با ``created_at`` و payload است.

Invalidation: ورودی قدیمی‌تر از ``CATALOGYAR_IMAGE_CACHE_TTL_SECONDS`` در اولین خواندن بعدی
منقضی حساب و حذف می‌شود؛ تغییر نسخه‌ی schema/prompt یا نام مدل هم چون در کلید می‌آید، ورودی‌های
قدیمی را خودکار miss می‌کند. خاموش کردن کامل با ``CATALOGYAR_IMAGE_CACHE_ENABLED=0``.

هر خطای I/O به‌جای fail کردن درخواست فقط warning لاگ می‌شود و مسیر عادی (فراخوانی مدل) ادامه
می‌یابد — یعنی cache همیشه «اختیاری» است. hit/miss هم لاگ می‌شود و هم در ``stats()`` شمرده
می‌شود (شمارنده‌ها in-process‌اند؛ با چند worker هر کدام شمارنده‌ی خودش را دارد).
"""

import hashlib
import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path

from app.config import IMAGE_CACHE_DIR, IMAGE_CACHE_ENABLED, IMAGE_CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)

_COUNTERS = {"hits": 0, "misses": 0, "stores": 0, "expired": 0, "errors": 0}
_LOCK = threading.Lock()


def _bump(name: str) -> None:
    with _LOCK:
        _COUNTERS[name] += 1


def stats() -> dict[str, int]:
    """شمارنده‌های in-process برای اثبات کارکرد cache."""
    with _LOCK:
        return dict(_COUNTERS)


def reset_stats() -> None:
    with _LOCK:
        for name in _COUNTERS:
            _COUNTERS[name] = 0


def build_key(model: str, version: str, image_bytes: list[bytes]) -> str:
    """کلید cache از محتوای عکس‌ها + مدل + نسخه‌ی schema می‌سازد."""
    digest = hashlib.sha256()
    digest.update(model.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(version.encode("utf-8"))
    for data in image_bytes:
        # digest هر عکس به‌جای خود بایت‌ها: طول ثابت است، پس الحاق بدون ابهام می‌ماند.
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def _entry_path(key: str) -> Path:
    return Path(IMAGE_CACHE_DIR) / f"{key}.json"


def get(key: str) -> dict | None:
    """payload ذخیره‌شده را برمی‌گرداند یا ``None`` (miss / منقضی / خطای خواندن)."""
    if not IMAGE_CACHE_ENABLED:
        return None

    path = _entry_path(key)
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
        created_at = float(entry["created_at"])
        payload = entry["payload"]
        if not isinstance(payload, dict):
            raise ValueError("payload ذخیره‌شده dict نیست")
    except FileNotFoundError:
        _bump("misses")
        logger.debug("image-analysis cache miss key=%s", key[:12])
        return None
    except Exception as exc:  # ورودی خراب/ناخوانا نباید درخواست را fail کند
        _bump("errors")
        _bump("misses")
        logger.warning("خواندن cache تحلیل تصویر ناموفق بود (نادیده گرفته شد): %s", exc)
        return None

    age = time.time() - created_at
    if age > IMAGE_CACHE_TTL_SECONDS:
        _bump("expired")
        _bump("misses")
        logger.info("image-analysis cache expired key=%s (age=%.0f ثانیه)", key[:12], age)
        _remove(path)
        return None

    _bump("hits")
    logger.info("image-analysis cache hit key=%s — فراخوانی مدل انجام نشد", key[:12])
    return payload


def put(key: str, payload: dict) -> None:
    """نتیجه را ذخیره می‌کند؛ خطای نوشتن فقط لاگ می‌شود."""
    if not IMAGE_CACHE_ENABLED:
        return

    path = _entry_path(key)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = json.dumps({"created_at": time.time(), "payload": payload}, ensure_ascii=False)
        # نوشتن اتمیک: temp در همان دایرکتوری، بعد rename — خواننده هیچ‌وقت فایل نیمه‌نوشته نمی‌بیند.
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
            tmp.write(entry)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)
    except Exception as exc:  # cache نباید مسیر اصلی را خراب کند
        _bump("errors")
        logger.warning("ذخیره‌ی cache تحلیل تصویر ناموفق بود (نادیده گرفته شد): %s", exc)
        return

    _bump("stores")
    logger.debug("image-analysis cache store key=%s", key[:12])


def _remove(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        logger.debug("حذف ورودی cache ناموفق بود: %s", exc)
