"""Unit tests for the rate limiter (NFR-04)."""
import pytest
from fastapi import HTTPException

from app.core.rate_limiter import RateLimiter


def test_allows_under_limit():
    rl = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        rl.check("user1")  # should not raise


def test_blocks_over_limit():
    rl = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        rl.check("user1")
    with pytest.raises(HTTPException) as exc_info:
        rl.check("user1")
    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers


def test_separate_keys():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    rl.check("user1")
    rl.check("user1")
    # user1 is at limit
    with pytest.raises(HTTPException):
        rl.check("user1")
    # user2 should still be fine
    rl.check("user2")


def test_reset_clears_key():
    rl = RateLimiter(max_requests=1, window_seconds=60)
    rl.check("user1")
    with pytest.raises(HTTPException):
        rl.check("user1")
    rl.reset("user1")
    rl.check("user1")  # should work again


def test_reset_all():
    rl = RateLimiter(max_requests=1, window_seconds=60)
    rl.check("a")
    rl.check("b")
    rl.reset()
    rl.check("a")  # should work
    rl.check("b")  # should work
