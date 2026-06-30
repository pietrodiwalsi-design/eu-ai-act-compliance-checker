"""
In-memory sliding-window rate limiter (NFR-04).

Limits requests per API key (extracted from JWT sub claim).
Default: 10 requests per 60 seconds on /assess.
"""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List

from fastapi import HTTPException, status


class RateLimiter:
    """Sliding-window rate limiter keyed by caller identity."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        """Raise 429 if key has exceeded the rate limit."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            timestamps = self._requests[key]
            # Prune expired entries
            self._requests[key] = [t for t in timestamps if t > cutoff]
            timestamps = self._requests[key]

            if len(timestamps) >= self.max_requests:
                retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s.",
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)

    def reset(self, key: str | None = None) -> None:
        """Clear rate limit state. If key is None, clear all."""
        with self._lock:
            if key is None:
                self._requests.clear()
            else:
                self._requests.pop(key, None)


# Singleton instance — configured from settings at import time
assess_rate_limiter = RateLimiter()
