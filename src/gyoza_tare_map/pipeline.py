"""Top-level pipeline: chains all 5 stages."""
from __future__ import annotations

import asyncio
from pathlib import Path

from gyoza_tare_map.config import (
    CLASSIFIED_JSONL,
    EXTRACTED_JSONL,
    OUTPUT_CSV,
    OUTPUT_MAP,
    OUTPUT_PARQUET,
    RAW_JSONL,
    SEEDS_FILE,
)


def run(
    seeds_file: Path = SEEDS_FILE,
    dry_run: bool = False,
    skip_crawl: bool = False,
    skip_map: bool = False,
) -> None:
    # Stage 1: Crawl
    if not skip_crawl:
        from gyoza_tare_map.crawl import runner as crawl_runner
        asyncio.run(
            crawl_runner.run(
                seeds_file=seeds_file,
                output_path=RAW_JSONL,
                dry_run=dry_run,
            )
        )
    else:
        print("[pipeline] Skipping crawl (--skip-crawl).")

    if not RAW_JSONL.exists():
        print(f"[pipeline] No raw data at {RAW_JSONL}. Aborting.")
        return

    # Stage 2: Extract
    from gyoza_tare_map.extract import record_builder
    record_builder.run(
        input_path=RAW_JSONL,
        output_path=EXTRACTED_JSONL,
        dry_run=dry_run,
    )

    if not EXTRACTED_JSONL.exists():
        print(f"[pipeline] No extracted data at {EXTRACTED_JSONL}. Aborting.")
        return

    # Stage 3: Classify
    from gyoza_tare_map.classify import rule_classifier
    records = rule_classifier.run(
        input_path=EXTRACTED_JSONL,
        output_path=CLASSIFIED_JSONL,
        dry_run=dry_run,
    )

    if not records:
        print("[pipeline] No classified records. Aborting.")
        return

    # Stage 4: Aggregate
    from gyoza_tare_map.aggregate.deduplicator import deduplicate
    from gyoza_tare_map.aggregate.scorer import score
    from gyoza_tare_map.aggregate.writer import write

    deduped = deduplicate(records)
    scores = score(deduped)
    df = write(
        scores,
        parquet_path=OUTPUT_PARQUET,
        csv_path=OUTPUT_CSV,
        dry_run=dry_run,
    )

    # Stage 5: Visualize
    from gyoza_tare_map.visualize.report import low_evidence_warning, print_report
    print_report(df)
    low_evidence_warning(df)

    if not skip_map:
        from gyoza_tare_map.visualize.choropleth import build_map
        try:
            build_map(df, output_path=OUTPUT_MAP, dry_run=dry_run)
        except FileNotFoundError as e:
            print(f"[pipeline] Map skipped: {e}")

    print("[pipeline] Done.")
