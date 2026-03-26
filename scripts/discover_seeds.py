"""はてなブックマーク検索で seeds.yaml 候補URLを自動発見する。

Usage:
    python scripts/discover_seeds.py [--prefectures 東京都 大阪府 ...] [--min-bookmarks 3]

出力: seeds.yaml に追記可能な YAML スニペット（標準出力）
      既に seeds.yaml に登録済みのURLは除外される。
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gyoza_tare_map.config import PHASE1_PREFECTURES
from gyoza_tare_map.search.hatena_search import search_multi

# 都道府県ごとの検索クエリ（短縮形を使うと検索精度が上がる）
PREF_QUERY_MAP: dict[str, list[str]] = {
    "東京都":  ["東京 餃子 酢醤油", "東京 餃子 タレ 食べ方"],
    "大阪府":  ["大阪 餃子 タレ 食べ方", "大阪 餃子 たれ 店"],
    "神奈川県": ["横浜 餃子 タレ 食べ方", "神奈川 餃子 たれ 店"],
    "兵庫県":  ["神戸 餃子 味噌だれ", "神戸 餃子 たれ 食べ方"],
    "愛知県":  ["名古屋 餃子 味噌だれ", "愛知 餃子 たれ 食べ方"],
    "宮城県":  ["仙台 餃子 酢コショウ", "宮城 餃子 たれ 食べ方"],
    "福岡県":  ["福岡 餃子 タレ 食べ方", "博多 餃子 たれ 店"],
    "北海道":  ["札幌 餃子 たれ 食べ方", "北海道 餃子 タレ 店"],
    "京都府":  ["京都 餃子 たれ 食べ方", "京都 餃子 タレ 店"],
    "広島県":  ["広島 餃子 たれ 食べ方", "広島 餃子 タレ 店"],
    "栃木県":  ["宇都宮 餃子 たれ 食べ方", "宇都宮 餃子 タレ 店"],
}


def load_existing_urls(seeds_path: Path) -> set[str]:
    if not seeds_path.exists():
        return set()
    with open(seeds_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["url"] for s in (data.get("sources") or [])}


def build_queries(prefectures: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for pref in prefectures:
        if pref in PREF_QUERY_MAP:
            result[pref] = PREF_QUERY_MAP[pref]
        else:
            # フォールバック: 都道府県名の短縮形で汎用クエリ
            short = pref.rstrip("都道府県")
            result[pref] = [f"{short} 餃子 たれ"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prefectures", nargs="+", default=PHASE1_PREFECTURES,
        metavar="PREF",
        help="検索対象の都道府県（デフォルト: Phase 1 の4都府県）",
    )
    parser.add_argument("--min-bookmarks", type=int, default=3)
    parser.add_argument(
        "--seeds", type=Path,
        default=ROOT / "seeds.yaml",
    )
    args = parser.parse_args()

    existing_urls = load_existing_urls(args.seeds)
    pref_queries = build_queries(args.prefectures)

    # 全クエリをフラットに並べて一括検索
    all_queries: list[str] = []
    query_to_pref: dict[str, str] = {}
    for pref, queries in pref_queries.items():
        for q in queries:
            all_queries.append(q)
            query_to_pref[q] = pref

    print(f"[search] {len(all_queries)} クエリを検索中...", file=sys.stderr)
    results_map = search_multi(all_queries, min_bookmarks=args.min_bookmarks)

    # 都道府県ごとに候補をまとめる（重複除去）
    seen_urls: set[str] = set(existing_urls)
    candidates: dict[str, list[dict]] = {p: [] for p in args.prefectures}

    gyoza_kw = ["餃子", "ぎょうざ", "ギョーザ", "ギョウザ", "gyoza"]

    for query, results in results_map.items():
        pref = query_to_pref[query]
        for r in results:
            if r.url in seen_urls:
                continue
            # タイトルに餃子キーワードが含まれない記事は除外
            title_lower = r.title.lower()
            if not any(kw.lower() in title_lower for kw in gyoza_kw):
                continue
            seen_urls.add(r.url)
            candidates[pref].append({
                "url": r.url,
                "title": r.title,
                "bookmarks": r.bookmarks,
                "date": r.date,
                "query": query,
            })

    # 結果表示
    total = sum(len(v) for v in candidates.values())
    print(f"[search] 新規候補: {total} 件（既存 {len(existing_urls)} 件を除外済み）\n", file=sys.stderr)

    if total == 0:
        print("# 新規候補なし", file=sys.stderr)
        return

    # seeds.yaml に貼れる形式で出力
    print("# ---- 以下を seeds.yaml の sources: に追記してください ----\n")
    for pref, items in candidates.items():
        if not items:
            continue
        # ブックマーク数降順
        items.sort(key=lambda x: x["bookmarks"], reverse=True)
        print(f"  # {'=' * 60}")
        print(f"  # {pref}  （{len(items)} 件）")
        print(f"  # {'=' * 60}\n")
        for item in items:
            title_escaped = item["title"].replace("'", "\\'")
            print(f"  # [{item['bookmarks']}users] {item['title']}")
            print(f"  # query: {item['query']}")
            print(f"  - type: html")
            print(f"    url: {item['url']}")
            print(f"    prefectures: [\"{pref}\"]")
            print()


if __name__ == "__main__":
    main()
