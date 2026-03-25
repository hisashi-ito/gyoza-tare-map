"""RSS feed fetcher: parses feed entries and fetches each article HTML."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser
import httpx
from charset_normalizer import from_bytes

from gyoza_tare_map.config import REQUEST_TIMEOUT_SEC
from gyoza_tare_map.crawl.cache import ResponseCache
from gyoza_tare_map.crawl.policy import RateLimiter, RobotsCache
from gyoza_tare_map.crawl.sources.base import CrawlSource, SeedEntry
from gyoza_tare_map.models import CrawledDocument


class RssSource(CrawlSource):
    """Parses an RSS/Atom feed URL and fetches each entry's linked article."""

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
        feed_url = seed.url
        cached_feed = await self._cache.get(feed_url)
        if cached_feed:
            feed_body = cached_feed["body"]
        else:
            await self._limiter.acquire(feed_url)
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT_SEC,
                follow_redirects=True,
                headers={"User-Agent": RobotsCache.USER_AGENT},
            ) as client:
                try:
                    resp = await client.get(feed_url)
                except Exception as exc:
                    print(f"[rss] Failed to fetch feed {feed_url}: {exc}")
                    return []
            feed_body = from_bytes(resp.content).best()
            feed_body = str(feed_body) if feed_body else resp.content.decode("utf-8", errors="replace")
            await self._cache.set(feed_url, resp.status_code, resp.headers.get("content-type", ""), feed_body)

        parsed = feedparser.parse(feed_body)
        docs: list[CrawledDocument] = []
        for entry in parsed.entries:
            link = entry.get("link", "")
            if not link:
                continue
            if not self._robots.is_allowed(link):
                print(f"[rss] Blocked by robots.txt: {link}")
                continue
            doc = await self._fetch_article(link, seed.prefectures)
            if doc:
                docs.append(doc)
        return docs

    async def _fetch_article(self, url: str, seed_prefectures: list[str] | None = None) -> CrawledDocument | None:
        cached = await self._cache.get(url)
        if cached:
            body, status_code, content_type, fetched_at = (
                cached["body"], cached["status_code"], cached["content_type"], cached["fetched_at"]
            )
        else:
            await self._limiter.acquire(url)
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT_SEC,
                follow_redirects=True,
                headers={"User-Agent": RobotsCache.USER_AGENT},
            ) as client:
                try:
                    resp = await client.get(url)
                except Exception as exc:
                    print(f"[rss] Failed to fetch article {url}: {exc}")
                    return None
            content_type = resp.headers.get("content-type", "")
            decoded = from_bytes(resp.content).best()
            body = str(decoded) if decoded else resp.content.decode("utf-8", errors="replace")
            status_code = resp.status_code
            fetched_at = datetime.now(tz=timezone.utc).isoformat()
            await self._cache.set(url, status_code, content_type, body)

        return CrawledDocument(
            url=url,
            fetched_at=fetched_at,
            source_type="rss",
            status_code=status_code,
            raw_html=body,
            domain=urlparse(url).netloc,
            content_type=content_type,
            seed_prefectures=seed_prefectures or [],
        )
