from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from gyoza_tare_map.models import CrawledDocument


@dataclass
class SeedEntry:
    url: str
    source_type: str                 # "html" | "rss" | "api" | "playwright"
    prefectures: list[str]           # hint prefectures; empty = auto-detect


class CrawlSource(ABC):
    """Base class for all crawl sources."""

    @abstractmethod
    async def fetch(self, seed: SeedEntry) -> list[CrawledDocument]:
        """Fetch one seed entry and return zero or more documents."""
        ...
