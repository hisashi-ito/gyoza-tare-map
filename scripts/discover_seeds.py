"""はてなブックマーク検索で seeds.yaml 候補URLを自動発見する。

Usage:
    # 標準出力に候補を表示（確認用）
    python scripts/discover_seeds.py

    # 全47都道府県を対象に検索
    python scripts/discover_seeds.py --all-prefectures

    # seeds.yaml に自動追記
    python scripts/discover_seeds.py --auto-append

    # 都道府県を絞って検索
    python scripts/discover_seeds.py --prefectures 福岡県 広島県 --auto-append
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gyoza_tare_map.config import ALL_PREFECTURES, PHASE1_PREFECTURES
from gyoza_tare_map.search.hatena_search import search_multi

# -----------------------------------------------------------------------
# 都道府県ごとの検索クエリ
# -----------------------------------------------------------------------
# 共通クエリ（全都道府県に適用）
_COMMON_QUERIES = ["餃子 たれ 食べ方", "餃子 タレ 専門店"]

# 都道府県固有クエリ（代表都市・地域名で絞り込む）
_PREF_SPECIFIC: dict[str, list[str]] = {
    "北海道":  ["札幌 餃子 たれ"],
    "宮城県":  ["仙台 餃子 酢コショウ", "仙台 餃子 たれ"],
    "栃木県":  ["宇都宮 餃子 たれ", "宇都宮 餃子 食べ方"],
    "東京都":  ["東京 餃子 酢醤油", "東京 餃子 タレ 食べ方"],
    "神奈川県": ["横浜 餃子 たれ", "横浜 餃子 食べ方"],
    "愛知県":  ["名古屋 餃子 味噌だれ", "名古屋 餃子 たれ"],
    "京都府":  ["京都 餃子 たれ 食べ方"],
    "大阪府":  ["大阪 餃子 タレ 食べ方", "大阪 餃子 たれ 店"],
    "兵庫県":  ["神戸 餃子 味噌だれ", "神戸 餃子 たれ 食べ方"],
    "広島県":  ["広島 餃子 たれ 食べ方"],
    "福岡県":  ["福岡 餃子 タレ 食べ方", "博多 餃子 たれ 店"],
    "宮崎県":  ["宮崎 餃子 たれ", "宮崎 餃子 食べ方"],
}

GYOZA_KEYWORDS = ["餃子", "ぎょうざ", "ギョーザ", "ギョウザ", "gyoza"]


def _build_queries(prefectures: list[str]) -> dict[str, list[str]]:
    """都道府県ごとの検索クエリリストを生成。"""
    result: dict[str, list[str]] = {}
    for pref in prefectures:
        short = pref.rstrip("都道府県")
        specific = _PREF_SPECIFIC.get(pref, [f"{short} 餃子 たれ"])
        result[pref] = specific + [f"{short} {q}" for q in _COMMON_QUERIES]
    return result


def _load_existing_urls(seeds_path: Path) -> set[str]:
    if not seeds_path.exists():
        return set()
    with open(seeds_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["url"] for s in (data.get("sources") or [])}


def _is_gyoza(title: str) -> bool:
    t = title.lower()
    return any(kw.lower() in t for kw in GYOZA_KEYWORDS)


def _collect_candidates(
    prefectures: list[str],
    existing_urls: set[str],
    min_bookmarks: int,
    max_pages: int,
) -> dict[str, list[dict]]:
    pref_queries = _build_queries(prefectures)

    all_queries: list[str] = []
    query_to_pref: dict[str, str] = {}
    for pref, queries in pref_queries.items():
        for q in queries:
            if q not in query_to_pref:   # 同一クエリの重複を避ける
                all_queries.append(q)
                query_to_pref[q] = pref

    print(
        f"[search] {len(prefectures)} 都道府県 / {len(all_queries)} クエリを検索中 "
        f"(最大 {max_pages} ページ/クエリ)...",
        file=sys.stderr,
    )

    results_map = search_multi(all_queries, min_bookmarks=min_bookmarks, max_pages=max_pages)

    seen_urls: set[str] = set(existing_urls)
    candidates: dict[str, list[dict]] = {p: [] for p in prefectures}

    for query, results in results_map.items():
        pref = query_to_pref[query]
        for r in results:
            if r.url in seen_urls:
                continue
            if not _is_gyoza(r.title):
                continue
            seen_urls.add(r.url)
            candidates[pref].append({
                "url": r.url,
                "title": r.title,
                "bookmarks": r.bookmarks,
                "date": r.date,
                "query": query,
            })

    for pref in candidates:
        candidates[pref].sort(key=lambda x: x["bookmarks"], reverse=True)

    return candidates


def _to_yaml_block(candidates: dict[str, list[dict]]) -> str:
    lines: list[str] = []
    for pref, items in candidates.items():
        if not items:
            continue
        lines.append(f"\n  # {'=' * 60}")
        lines.append(f"  # {pref}  ({len(items)} 件)")
        lines.append(f"  # {'=' * 60}\n")
        for item in items:
            title_short = textwrap.shorten(item["title"], width=60, placeholder="...")
            lines.append(f"  # [{item['bookmarks']}users] {title_short}")
            lines.append(f"  - type: html")
            lines.append(f"    url: {item['url']}")
            lines.append(f"    prefectures: [\"{pref}\"]")
            lines.append("")
    return "\n".join(lines)


def _append_to_seeds(seeds_path: Path, yaml_block: str) -> None:
    with open(seeds_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(yaml_block)
    print(f"[search] seeds.yaml に追記しました → {seeds_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--prefectures", nargs="+", default=None, metavar="PREF",
        help="検索対象の都道府県（デフォルト: Phase 1 の4都府県）",
    )
    group.add_argument(
        "--all-prefectures", action="store_true",
        help="全47都道府県を対象にする",
    )
    parser.add_argument("--min-bookmarks", type=int, default=1)
    parser.add_argument(
        "--max-pages", type=int, default=5,
        help="1クエリあたりの最大取得ページ数（1ページ=40件、デフォルト5）",
    )
    parser.add_argument(
        "--auto-append", action="store_true",
        help="発見したURLを seeds.yaml に自動追記する",
    )
    parser.add_argument(
        "--seeds", type=Path, default=ROOT / "seeds.yaml",
    )
    args = parser.parse_args()

    if args.all_prefectures:
        prefectures = ALL_PREFECTURES
    elif args.prefectures:
        prefectures = args.prefectures
    else:
        prefectures = PHASE1_PREFECTURES

    existing_urls = _load_existing_urls(args.seeds)
    candidates = _collect_candidates(
        prefectures, existing_urls,
        min_bookmarks=args.min_bookmarks,
        max_pages=args.max_pages,
    )

    total = sum(len(v) for v in candidates.values())
    print(
        f"[search] 新規候補: {total} 件（既存 {len(existing_urls)} 件を除外済み）",
        file=sys.stderr,
    )

    if total == 0:
        print("[search] 新規候補なし", file=sys.stderr)
        return

    yaml_block = _to_yaml_block(candidates)

    if args.auto_append:
        _append_to_seeds(args.seeds, yaml_block)
    else:
        print("# ---- 以下を seeds.yaml の sources: に追記してください ----\n")
        print(yaml_block)


if __name__ == "__main__":
    main()
