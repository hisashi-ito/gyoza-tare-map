"""はてなブックマーク検索RSSクライアント。

APIキー不要・無料。RSS エンドポイントを feedparser で解析する。
"""
from __future__ import annotations

import time
import urllib.parse
from dataclasses import dataclass

import feedparser

BASE_URL = "https://b.hatena.ne.jp/q/{query}"
DEFAULT_PARAMS = {
    "sort": "popular",
    "users": "3",       # ブックマーク数の最低閾値
    "target": "text",   # 本文検索
    "safe": "on",
    "date_range": "5y",
    "mode": "rss",
}
REQUEST_INTERVAL = 1.5  # seconds between requests (robots.txt: Crawl-delay 未指定)


@dataclass
class SearchResult:
    url: str
    title: str
    bookmarks: int
    date: str   # ISO8601


def search(
    query: str,
    min_bookmarks: int = 3,
    max_results: int = 40,
) -> list[SearchResult]:
    """はてなブックマーク本文検索でURLリストを返す。

    Args:
        query: 検索クエリ（例: "東京 餃子 たれ"）
        min_bookmarks: この数以上のブックマークがある記事のみ返す
        max_results: 最大返却件数（RSSは1ページ最大40件）
    """
    encoded = urllib.parse.quote(query)
    url = BASE_URL.format(query=encoded)
    params = "&".join(f"{k}={v}" for k, v in DEFAULT_PARAMS.items())
    feed_url = f"{url}?{params}"

    feed = feedparser.parse(feed_url)

    results: list[SearchResult] = []
    for entry in feed.entries[:max_results]:
        bk_count = int(getattr(entry, "hatena_bookmarkcount", 0) or 0)
        if bk_count < min_bookmarks:
            continue
        results.append(SearchResult(
            url=entry.link,
            title=entry.title,
            bookmarks=bk_count,
            date=entry.get("published", ""),
        ))

    return results


def search_multi(
    queries: list[str],
    min_bookmarks: int = 3,
    max_results_per_query: int = 40,
    interval: float = REQUEST_INTERVAL,
) -> dict[str, list[SearchResult]]:
    """複数クエリを順番に検索して返す。クエリ間にインターバルを挟む。"""
    results: dict[str, list[SearchResult]] = {}
    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(interval)
        results[q] = search(q, min_bookmarks=min_bookmarks, max_results=max_results_per_query)
    return results
