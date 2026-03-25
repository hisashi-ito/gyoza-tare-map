"""robots.txt compliance and per-domain rate limiting."""
from __future__ import annotations

import asyncio
import time
import urllib.robotparser
from urllib.parse import urlparse

import httpx


class RobotsCache:
    """Fetches and caches robots.txt per domain. Blocks disallowed URLs."""

    USER_AGENT = "gyoza-tare-map-bot/0.1"

    def __init__(self) -> None:
        self._parsers: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _base_url(self, url: str) -> str:
        p = urlparse(url)
        return f"{p.scheme}://{p.netloc}"

    def fetch(self, url: str) -> None:
        """Synchronously fetch and cache robots.txt for the given URL's domain."""
        base = self._base_url(url)
        if base in self._parsers:
            return
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"{base}/robots.txt")
        try:
            parser.read()
        except Exception:
            # If robots.txt is unreachable, assume everything is allowed.
            pass
        self._parsers[base] = parser

    def is_allowed(self, url: str) -> bool:
        base = self._base_url(url)
        if base not in self._parsers:
            self.fetch(url)
        parser = self._parsers.get(base)
        if parser is None:
            return True
        return parser.can_fetch(self.USER_AGENT, url)


class RateLimiter:
    """Per-domain async rate limiter using token bucket (minimum delay)."""

    def __init__(self, delay_sec: float) -> None:
        self._delay = delay_sec
        self._last_request: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, domain: str) -> asyncio.Lock:
        if domain not in self._locks:
            self._locks[domain] = asyncio.Lock()
        return self._locks[domain]

    async def acquire(self, url: str) -> None:
        domain = urlparse(url).netloc
        lock = self._lock_for(domain)
        async with lock:
            last = self._last_request.get(domain, 0.0)
            wait = self._delay - (time.monotonic() - last)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request[domain] = time.monotonic()
