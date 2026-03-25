# Data Schema

## CrawledDocument (`data/raw/documents.jsonl`)

| Field        | Type   | Description                              |
|--------------|--------|------------------------------------------|
| url          | str    | Fetched URL                              |
| fetched_at   | str    | ISO-8601 timestamp (UTC)                 |
| source_type  | str    | `html` / `rss` / `api` / `playwright`   |
| status_code  | int    | HTTP status code                         |
| raw_html     | str    | Raw HTML / JSON body                     |
| domain       | str    | Hostname                                 |
| content_type | str    | HTTP Content-Type header                 |

## ExtractedSnippet (`data/extracted/snippets.jsonl`)

| Field            | Type   | Description                                        |
|------------------|--------|----------------------------------------------------|
| url              | str    | Source URL                                         |
| fetched_at       | str    | ISO-8601 timestamp                                 |
| prefecture_hint  | str    | Detected prefecture name, or `""` if unknown       |
| text             | str    | Clean body text (trafilatura output, NFKC-normalized) |
| char_count       | int    | Character count of `text`                          |

## ClassifiedRecord (`data/classified/records.jsonl`)

| Field              | Type   | Description                                     |
|--------------------|--------|-------------------------------------------------|
| url                | str    | Source URL                                      |
| fetched_at         | str    | ISO-8601 timestamp                              |
| prefecture         | str    | Canonical prefecture name (47-value vocab)      |
| label              | str    | One of the 5 condiment labels (see labels.md)   |
| confidence         | float  | 0.0–1.0                                         |
| classifier_version | str    | e.g. `rule_v1`, `llm_qwen25_7b`                 |
| snippet_text       | str    | First 500 chars of extracted text (for audit)   |
| ambiguous          | bool   | True when top-2 label scores differ by ≤ 0.1    |

## PrefectureScore (`outputs/evidence.parquet`, `outputs/evidence.csv`)

| Field             | Type   | Description                                          |
|-------------------|--------|------------------------------------------------------|
| prefecture        | str    | Canonical prefecture name                            |
| dominant_label    | str    | Label with highest weighted score                    |
| evidence_count    | int    | Total classified records for this prefecture         |
| confidence_mean   | float  | Mean confidence across all records                   |
| low_evidence      | bool   | True when evidence_count < 5                         |
| score_*           | float  | Normalized weight per label (one column per label)   |
