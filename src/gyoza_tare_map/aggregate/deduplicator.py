"""Remove duplicate records to prevent single high-volume sources from dominating."""
from __future__ import annotations

from gyoza_tare_map.models import ClassifiedRecord


def deduplicate(records: list[ClassifiedRecord]) -> list[ClassifiedRecord]:
    """Keep one record per (url, prefecture, label) triple.

    When duplicates exist, the record with the highest confidence is kept.
    """
    seen: dict[tuple[str, str, str], ClassifiedRecord] = {}
    for rec in records:
        key = (rec.url, rec.prefecture, rec.label)
        existing = seen.get(key)
        if existing is None or rec.confidence > existing.confidence:
            seen[key] = rec
    result = list(seen.values())
    removed = len(records) - len(result)
    if removed:
        print(f"[dedup] Removed {removed} duplicates, {len(result)} records remain.")
    return result
