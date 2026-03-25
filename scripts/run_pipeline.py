#!/usr/bin/env python3
"""CLI entry point for the gyoza-tare-map pipeline.

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --dry-run
    python scripts/run_pipeline.py --skip-crawl
    python scripts/run_pipeline.py --skip-map
    python scripts/run_pipeline.py --seeds path/to/seeds.yaml
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gyoza_tare_map import pipeline
from gyoza_tare_map.config import SEEDS_FILE


def main() -> None:
    parser = argparse.ArgumentParser(description="gyoza-tare-map pipeline")
    parser.add_argument("--seeds", default=str(SEEDS_FILE), help="Path to seeds.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing output files")
    parser.add_argument("--skip-crawl", action="store_true", help="Skip crawl stage (use existing raw data)")
    parser.add_argument("--skip-map", action="store_true", help="Skip map generation")
    args = parser.parse_args()

    pipeline.run(
        seeds_file=Path(args.seeds),
        dry_run=args.dry_run,
        skip_crawl=args.skip_crawl,
        skip_map=args.skip_map,
    )


if __name__ == "__main__":
    main()
