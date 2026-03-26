# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`gyoza-tare-map` is a Python data pipeline that estimates and visualizes regional differences in gyoza condiment culture across Japan using publicly available web data.

## Development Environment

All work is done inside Docker:

```bash
# Build and run the full pipeline
docker compose up app

# Run without crawling (use existing raw data)
docker compose run --rm app python scripts/run_pipeline.py --skip-crawl

# Individual stages
docker compose run --rm app python scripts/run_pipeline.py --skip-crawl --skip-map
docker compose run --rm app python scripts/fetch_geodata.py

# Dry run (no file writes)
docker compose run --rm app python scripts/run_pipeline.py --dry-run
```

Install (outside Docker, for editor tooling only):

```bash
pip install -e ".[dev]"
```

## Adding Crawl Targets

Edit `seeds.yaml` in the project root. Each entry needs `type`, `url`, and optional `prefectures`:

```yaml
sources:
  - type: rss
    url: https://example.com/feed
    prefectures: []          # empty = auto-detect from text
  - type: html
    url: https://example.com/article
    prefectures: ["大阪府"]
```

## Architecture

5-stage pipeline: **Crawl → Extract → Classify → Aggregate → Visualize**

```
src/gyoza_tare_map/
  config.py         # All paths, constants, prefecture list
  models.py         # Shared dataclasses (CrawledDocument → ExtractedSnippet → ClassifiedRecord → PrefectureScore)
  crawl/            # policy.py (robots+rate), cache.py (SQLite), sources/, runner.py
  extract/          # html_extractor.py (trafilatura), region_detector.py, record_builder.py
  classify/         # labels.py (keyword dicts), rule_classifier.py (Phase 1)
  aggregate/        # deduplicator.py, scorer.py, writer.py (pandas → Parquet/CSV)
  visualize/        # choropleth.py (folium map), report.py (pandas table)
  pipeline.py       # Chains all 5 stages
scripts/
  run_pipeline.py   # CLI: --dry-run, --skip-crawl, --skip-map, --seeds
  fetch_geodata.py  # One-time GeoJSON download
data/               # raw/ extracted/ classified/ geo/ cache.db  (gitignored)
outputs/            # evidence.parquet evidence.csv map.html     (gitignored)
```

Intermediate files are JSONL at each stage boundary. Every stage can be re-run independently by pointing `input_path` to the appropriate file.

### Core Data Model

Each stage adds fields:

```
CrawledDocument → ExtractedSnippet (+ prefecture_hint, text)
               → ClassifiedRecord  (+ label, confidence, ambiguous)
               → PrefectureScore   (+ dominant_label, label_scores, evidence_count)
```

Condiment labels: `prepared_tare`, `self_mix_soy_vinegar`, `miso_dare`, `su_kosho`, `other_local_style`, `unknown`

### Key Libraries

| Layer | Libraries |
|-------|-----------|
| Crawling | httpx, trafilatura, playwright, feedparser |
| Data | pandas, pyarrow |
| Geo | geopandas, folium |
| NLP/ML | transformers, sentence-transformers (Phase 2) |

## Development Phases

- **Phase 1:** Focus prefectures — Tokyo, Osaka, Kanagawa, Hyogo; rule-based classifier (`classify/rule_classifier.py`)
- **Phase 2:** Keyword dictionary expansion + negation handling in `classify/labels.py` and `rule_classifier.py`
  - Expand `labels.py` keyword lists with paraphrase variants
  - Add negation window detection: if a negation marker (「〜ではなく」「〜でなく」等) precedes a keyword within N characters, suppress that keyword hit
- **Phase 3:** Nationwide expansion, Playwright sources

## Crawl Policy

- robots.txt checked before every fetch (`crawl/policy.py`)
- 3-second minimum delay per domain
- HTTP responses cached in `data/cache.db` (7-day TTL)
- No CAPTCHA bypass
- Source priority: APIs > RSS > static HTML > Playwright

## Classifier Evaluation

Run against the labeled test set in `tests/classifier_testset.yaml`:

```bash
docker compose run --rm app python scripts/evaluate_classifier.py --verbose
```

When adding keywords or negation rules, run this to verify no regressions.
