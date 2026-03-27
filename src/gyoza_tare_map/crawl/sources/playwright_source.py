"""Playwright-based crawl source for JavaScript-heavy pages.

Use ``type: playwright`` in seeds.yaml for sites that require JS rendering
(e.g. SPAs, lazy-loaded content). Falls back gracefully if Playwright is not
available or if the page errors.
"""
from __future__ import annotations

import asyncio
import datetime
from urllib.parse import urlparse
from typing import TYPE_CHECKING

from gyoza_tare_map.models import CrawledDocument

from .base import CrawlSource, SeedEntry

if TYPE_CHECKING:
    from gyoza_tare_map.crawl.policy import RateLimiter, RobotsCache


class PlaywrightSource(CrawlSource):
    """Fetch a single HTML page using Playwright (Chromium)."""

    def __init__(
        self,
        robots: RobotsCache,
        limiter: RateLimiter,
        timeout_ms: int = 30_000,
        wait_until: str = "domcontentloaded",
    ) -> None:
        self._robots = robots
        self._limiter = limiter
        self._timeout_ms = timeout_ms
        self._wait_until = wait_until

    async def fetch(self, seed: SeedEntry) -> list[CrawledDocument]:
        # robots.txt チェック
        if not self._robots.is_allowed(seed.url):
            print(f"[playwright] Blocked by robots.txt: {seed.url}")
            return []

        await self._limiter.acquire(seed.url)

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("[playwright] playwright not installed — skipping")
            return []

        html = ""
        status = 0
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                # ボット検出を緩和するための最低限のヘッダー
                await page.set_extra_http_headers({
                    "Accept-Language": "ja,en;q=0.9",
                })
                resp = await page.goto(
                    seed.url,
                    timeout=self._timeout_ms,
                    wait_until=self._wait_until,  # type: ignore[arg-type]
                )
                status = resp.status if resp else 0
                if status == 200:
                    # JS 実行完了を待つ（最大2秒）
                    await asyncio.sleep(2)
                    html = await page.content()
                await browser.close()
        except Exception as exc:
            print(f"[playwright] Error fetching {seed.url}: {exc}")
            return []

        return [
            CrawledDocument(
                url=seed.url,
                fetched_at=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                source_type="playwright",
                status_code=status,
                raw_html=html,
                domain=urlparse(seed.url).netloc,
                seed_prefectures=seed.prefectures,
            )
        ]
