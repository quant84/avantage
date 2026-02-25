"""Async token-bucket rate limiter with FIFO semaphore gate."""

from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """Async token-bucket rate limiter that prevents thundering-herd overshoot.

    Uses a FIFO semaphore gate so that at most one waiter sleeps at a time,
    preventing bursts of requests when multiple coroutines are waiting.

    Args:
        rate: Number of tokens (requests) allowed per *period*.
        period: Length of the token window in seconds.
    """

    def __init__(self, rate: int, period: float = 60.0) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if period <= 0:
            raise ValueError("period must be positive")

        self._rate = rate
        self._period = period
        self._tokens = float(rate)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self._gate = asyncio.Semaphore(1)

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._rate, self._tokens + elapsed * (self._rate / self._period))
        self._last_refill = now

    async def acquire(self) -> None:
        """Acquire a single token, waiting if necessary."""
        # Fast path: try to grab a token under the lock without sleeping.
        async with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return

        # Slow path: enter the FIFO gate so only one waiter sleeps at a time.
        async with self._gate:
            while True:
                async with self._lock:
                    self._refill()
                    if self._tokens >= 1.0:
                        self._tokens -= 1.0
                        return
                    # Calculate sleep duration until at least one token is available.
                    deficit = 1.0 - self._tokens
                    sleep_time = deficit / (self._rate / self._period)

                await asyncio.sleep(sleep_time)
