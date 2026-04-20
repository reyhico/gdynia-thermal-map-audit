"""Request rate limiter enforcing a minimum inter-request delay."""

from __future__ import annotations

import threading
import time


class RateLimiter:
    """Thread-safe rate limiter for HTTP requests.

    Parameters
    ----------
    min_delay_s:
        Minimum seconds to wait between calls to :meth:`wait`.
    """

    def __init__(self, min_delay_s: float = 1.0) -> None:
        self.min_delay_s = min_delay_s
        self._lock = threading.Lock()
        self._last_call: float = 0.0

    def wait(self) -> None:
        """Block until the minimum delay has elapsed since the last call."""
        with self._lock:
            elapsed = time.monotonic() - self._last_call
            remaining = self.min_delay_s - elapsed
            if remaining > 0:
                time.sleep(remaining)
            self._last_call = time.monotonic()

    @property
    def delay(self) -> float:
        """Current minimum delay in seconds."""
        return self.min_delay_s

    @delay.setter
    def delay(self, value: float) -> None:
        self.min_delay_s = max(0.0, value)
