"""Retry/backoff برای فراخوانی مدل‌های بیرونی (vision/speech/generate).

فقط خطاهای **موقت** (قطعی شبکه، تایم‌اوت، `429` و `5xx`) دوباره تلاش می‌شوند؛ خطاهای
`4xx` کلاینت (مثل `400`/`401`/`403`) بلافاصله بالا می‌روند چون تکرارشان فقط تأخیر و
هزینه‌ی اضافه است. تعداد تلاش‌ها/تأخیرها در [[concepts/engine-config]] قابل تنظیم است.
"""

import logging
import random
from collections.abc import Callable
from time import sleep
from typing import TypeVar

from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from app.config import MODEL_MAX_ATTEMPTS, MODEL_RETRY_BASE_DELAY, MODEL_RETRY_MAX_DELAY

logger = logging.getLogger(__name__)

T = TypeVar("T")

# کدهای وضعیتی که با وجود 4xx بودن موقتی‌اند و ارزش تلاش دوباره دارند.
# (429 جداگانه با RateLimitError گرفته می‌شود.)
_TRANSIENT_STATUS_CODES = frozenset({408})


def _status_code(exc: BaseException) -> int | None:
    code = getattr(exc, "status_code", None)
    return code if isinstance(code, int) else None


def is_transient(exc: BaseException) -> bool:
    """آیا این خطا موقتی است (ارزش تلاش دوباره دارد)؟"""
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return True
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIStatusError):
        code = _status_code(exc) or 0
        return code >= 500 or code in _TRANSIENT_STATUS_CODES
    # خطای شبکه‌ی بیرون از SDK (مثلاً DNS/socket) — ولی نه هر OSError.
    return isinstance(exc, (ConnectionError, TimeoutError))


def _retry_after_seconds(exc: BaseException) -> float | None:
    """اگر provider هدر ``Retry-After`` داده باشد، همان را ترجیح بده."""
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if not headers:
        return None
    try:
        return max(0.0, float(headers.get("retry-after")))
    except (TypeError, ValueError):
        return None


def _backoff_delay(attempt: int, retry_after: float | None) -> float:
    """تأخیر نمایی با jitter؛ ``attempt`` شماره‌ی تلاشی است که شکست خورده (۱-پایه)."""
    if retry_after is not None:
        return min(retry_after, MODEL_RETRY_MAX_DELAY)
    ceiling = min(MODEL_RETRY_MAX_DELAY, MODEL_RETRY_BASE_DELAY * (2 ** (attempt - 1)))
    return random.uniform(ceiling / 2, ceiling)


def call_with_retry(call: Callable[[], T], *, operation: str) -> T:
    """``call`` را با backoff نمایی صدا می‌زند و در نهایت خطای اصلی را دوباره raise می‌کند.

    ``operation`` فقط برای پیام لاگ است (مثلاً ``"vision"``). تعداد کل تلاش‌ها با
    ``CATALOGYAR_MODEL_MAX_ATTEMPTS`` محدود است — retry هرگز بی‌نهایت نیست.
    """
    attempts = max(1, MODEL_MAX_ATTEMPTS)
    attempt = 1
    while True:
        try:
            return call()
        except Exception as exc:
            if not is_transient(exc) or attempt >= attempts:
                raise
            delay = _backoff_delay(attempt, _retry_after_seconds(exc))
            logger.warning(
                "فراخوانی %s ناموفق بود (تلاش %d/%d): %s — تلاش دوباره پس از %.2f ثانیه",
                operation,
                attempt,
                attempts,
                exc,
                delay,
            )
            sleep(delay)
            attempt += 1
