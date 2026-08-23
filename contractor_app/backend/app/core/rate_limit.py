"""Simple in-memory sliding-window rate limiter (demo-grade)."""

from __future__ import annotations

from collections import defaultdict
from time import monotonic


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = max(1, limit)
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = monotonic()
        cutoff = now - self.window_seconds
        hits = [t for t in self._hits[key] if t > cutoff]
        if len(hits) >= self.limit:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True


_limiters: dict[str, SlidingWindowLimiter] = {}


def get_limiter(name: str, limit: int, window_seconds: int = 60) -> SlidingWindowLimiter:
    limiter = _limiters.get(name)
    if limiter is None or limiter.limit != limit or limiter.window_seconds != window_seconds:
        limiter = SlidingWindowLimiter(limit, window_seconds)
        _limiters[name] = limiter
    return limiter
