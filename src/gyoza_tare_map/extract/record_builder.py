"""Converts CrawledDocument → list[ExtractedSnippet]."""
from __future__ import annotations

from pathlib import Path

from gyoza_tare_map.config import EXTRACTED_JSONL, RAW_JSONL
from gyoza_tare_map.extract.html_extractor import extract_text
from gyoza_tare_map.extract.region_detector import detect_prefecture
from gyoza_tare_map.models import CrawledDocument, ExtractedSnippet


def build_snippet(doc: CrawledDocument, prefecture_hint: str = "") -> ExtractedSnippet | None:
    """Extract clean text from a CrawledDocument and return an ExtractedSnippet.

    Returns None if no meaningful text could be extracted.
    """
    text = extract_text(doc.raw_html, url=doc.url)
    if not text:
        return None

    # Priority: caller hint > seed prefectures > auto-detect from text
    if prefecture_hint:
        prefecture = prefecture_hint
    elif doc.seed_prefectures:
        prefecture = doc.seed_prefectures[0]
    else:
        prefecture = detect_prefecture(doc.url + " " + text[:500])
    return ExtractedSnippet(
        url=doc.url,
        fetched_at=doc.fetched_at,
        prefecture_hint=prefecture,
        text=text,
        char_count=len(text),
    )


def run(
    input_path: Path = RAW_JSONL,
    output_path: Path = EXTRACTED_JSONL,
    dry_run: bool = False,
) -> list[ExtractedSnippet]:
    snippets: list[ExtractedSnippet] = []
    skipped = 0

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc = CrawledDocument.from_json(line)
            if doc.status_code != 200:
                skipped += 1
                continue
            snippet = build_snippet(doc)
            if snippet is None:
                skipped += 1
                continue
            snippets.append(snippet)

    print(f"[extract] {len(snippets)} snippets extracted, {skipped} skipped.")

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for s in snippets:
                f.write(s.to_json() + "\n")
        print(f"[extract] Wrote → {output_path}")

    return snippets
