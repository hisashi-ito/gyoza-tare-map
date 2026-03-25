"""Crawl runner: loads seeds.yaml, dispatches to appropriate source, writes JSONL."""
from __future__ import annotations

import asyncio
from pathlib import Path

import yaml

from gyoza_tare_map.config import (
    DEFAULT_CRAWL_DELAY_SEC,
    MAX_CONCURRENT_DOMAINS,
    RAW_JSONL,
    SEEDS_FILE,
)
from gyoza_tare_map.crawl.cache import ResponseCache
from gyoza_tare_map.crawl.policy import RateLimiter, RobotsCache
from gyoza_tare_map.crawl.sources.base import SeedEntry
from gyoza_tare_map.crawl.sources.httpx_source import HttpxSource
from gyoza_tare_map.crawl.sources.rss_source import RssSource
from gyoza_tare_map.models import CrawledDocument


def load_seeds(seeds_file: Path = SEEDS_FILE) -> list[SeedEntry]:
    if not seeds_file.exists():
        raise FileNotFoundError(f"seeds.yaml not found: {seeds_file}\nCreate it with a 'sources' list.")
    with open(seeds_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    entries = []
    for item in data.get("sources", []):
        entries.append(
            SeedEntry(
                url=item["url"],
                source_type=item.get("type", "html"),
                prefectures=item.get("prefectures", []),
            )
        )
    return entries


def _write_jsonl(docs: list[CrawledDocument], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for doc in docs:
            f.write(doc.to_json() + "\n")


async def run(
    seeds_file: Path = SEEDS_FILE,
    output_path: Path = RAW_JSONL,
    dry_run: bool = False,
) -> list[CrawledDocument]:
    seeds = load_seeds(seeds_file)
    robots = RobotsCache()
    limiter = RateLimiter(delay_sec=DEFAULT_CRAWL_DELAY_SEC)
    cache = ResponseCache()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOMAINS)

    html_source = HttpxSource(robots, limiter, cache)
    rss_source = RssSource(robots, limiter, cache)

    async def process(seed: SeedEntry) -> list[CrawledDocument]:
        async with semaphore:
            if seed.source_type == "rss":
                return await rss_source.fetch(seed)
            else:
                return await html_source.fetch(seed)

    tasks = [process(s) for s in seeds]
    results = await asyncio.gather(*tasks)

    all_docs: list[CrawledDocument] = []
    for docs in results:
        all_docs.extend(docs)

    print(f"[runner] Fetched {len(all_docs)} documents from {len(seeds)} seeds.")

    if not dry_run:
        _write_jsonl(all_docs, output_path)
        print(f"[runner] Wrote {len(all_docs)} documents → {output_path}")

    return all_docs
