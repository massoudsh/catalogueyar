import time
from collections.abc import Callable
from typing import TypeVar

from openai import APIConnectionError, APITimeoutError, RateLimitError

T = TypeVar("T")
TRANSIENT_ERRORS = (APIConnectionError, APITimeoutError, RateLimitError, TimeoutError, ConnectionError)


def with_retry(operation: Callable[[], T], attempts: int = 3, base_delay: float = 0.2) -> T:
    last_error: BaseException | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except TRANSIENT_ERRORS as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            time.sleep(base_delay * (2**attempt))
    raise last_error  # type: ignore[misc]
