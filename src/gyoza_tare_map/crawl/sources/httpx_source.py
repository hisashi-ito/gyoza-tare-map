"""Static HTML / API fetcher using async httpx."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from charset_normalizer import from_bytes

from gyoza_tare_map.config import REQUEST_TIMEOUT_SEC
from gyoza_tare_map.crawl.cache import ResponseCache
from gyoza_tare_map.crawl.policy import RateLimiter, RobotsCache
from gyoza_tare_map.crawl.sources.base import CrawlSource, SeedEntry
from gyoza_tare_map.models import CrawledDocument


class HttpxSource(CrawlSource):
    def __init__(
        self,
        robots: RobotsCache,
        limiter: RateLimiter,
        cache: ResponseCache,
    ) -> None:
        self._robots = robots
        self._limiter = limiter
        self._cache = cache

    async def fetch(self, seed: SeedEntry) -> list[CrawledDocument]:
        url = seed.url
        if not self._robots.is_allowed(url):
            print(f"[httpx] Blocked by robots.txt: {url}")
            return []

        cached = await self._cache.get(url)
        if cached:
            return [self._make_doc(url, cached["body"], cached["status_code"], cached["content_type"], cached["fetched_at"], seed.source_type, seed.prefectures)]

        await self._limiter.acquire(url)
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SEC,
            follow_redirects=True,
            headers={"User-Agent": RobotsCache.USER_AGENT},
        ) as client:
            try:
                resp = await client.get(url)
            except Exception as exc:
                print(f"[httpx] Failed {url}: {exc}")
                return []

        content_type = resp.headers.get("content-type", "")
        body = self._decode(resp.content, content_type)
        await self._cache.set(url, resp.status_code, content_type, body)
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        return [self._make_doc(url, body, resp.status_code, content_type, fetched_at, seed.source_type, seed.prefectures)]

    def _decode(self, content: bytes, content_type: str) -> str:
        result = from_bytes(content).best()
        if result:
            return str(result)
        return content.decode("utf-8", errors="replace")

    def _make_doc(
        self,
        url: str,
        body: str,
        status_code: int,
        content_type: str,
        fetched_at: str,
        source_type: str,
        seed_prefectures: list[str] | None = None,
    ) -> CrawledDocument:
        return CrawledDocument(
            url=url,
            fetched_at=fetched_at,
            source_type=source_type,
            status_code=status_code,
            raw_html=body,
            domain=urlparse(url).netloc,
            content_type=content_type,
            seed_prefectures=seed_prefectures or [],
        )
