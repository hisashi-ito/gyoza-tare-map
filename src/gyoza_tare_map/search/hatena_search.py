"""はてなブックマーク検索RSSクライアント。

APIキー不要・無料。RSS エンドポイントを feedparser で解析する。
ページネーション対応（1ページ40件 × 最大5ページ = 200件/クエリ）。
"""
from __future__ import annotations

import time
import urllib.parse
from dataclasses import dataclass

import feedparser

BASE_URL = "https://b.hatena.ne.jp/q/{query}"
DEFAULT_PARAMS = {
    "sort": "popular",
    "users": "1",       # 幅広く取得するため閾値を下げる
    "target": "text",
    "safe": "on",
    "date_range": "5y",
    "mode": "rss",
}
PAGE_SIZE = 40          # はてなブックマーク RSS の1ページ件数
REQUEST_INTERVAL = 1.5  # seconds between requests


@dataclass
class SearchResult:
    url: str
    title: str
    bookmarks: int
    date: str   # ISO8601


def search(
    query: str,
    min_bookmarks: int = 1,
    max_pages: int = 5,
) -> list[SearchResult]:
    """はてなブックマーク本文検索でURLリストを返す（ページネーション対応）。

    Args:
        query: 検索クエリ（例: "東京 餃子 たれ"）
        min_bookmarks: この数以上のブックマークがある記事のみ返す
        max_pages: 最大取得ページ数（1ページ=40件、最大5ページ=200件）
    """
    encoded = urllib.parse.quote(query)
    base = BASE_URL.format(query=encoded)
    params = "&".join(f"{k}={v}" for k, v in DEFAULT_PARAMS.items())

    results: list[SearchResult] = []
    seen: set[str] = set()

    for page in range(1, max_pages + 1):
        offset = (page - 1) * PAGE_SIZE
        feed_url = f"{base}?{params}&of={offset}"
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            break   # これ以上ページがない

        for entry in feed.entries:
            if entry.link in seen:
                continue
            bk_count = int(getattr(entry, "hatena_bookmarkcount", 0) or 0)
            if bk_count < min_bookmarks:
                continue
            seen.add(entry.link)
            results.append(SearchResult(
                url=entry.link,
                title=entry.title,
                bookmarks=bk_count,
                date=entry.get("published", ""),
            ))

        if page < max_pages:
            time.sleep(REQUEST_INTERVAL)

    return results


def search_multi(
    queries: list[str],
    min_bookmarks: int = 1,
    max_pages: int = 5,
    interval: float = REQUEST_INTERVAL,
) -> dict[str, list[SearchResult]]:
    """複数クエリを順番に検索して返す。クエリ間にインターバルを挟む。"""
    results: dict[str, list[SearchResult]] = {}
    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(interval)
        results[q] = search(q, min_bookmarks=min_bookmarks, max_pages=max_pages)
    return results
