# gyoza-tare-map Specification v0.1

## 1. Purpose

This project aims to estimate and visualize regional differences in gyoza condiment culture across Japan using publicly available web data.

Labels:
- prepared_tare
- self_mix_soy_vinegar
- miso_dare
- other_local_style
- unknown

---

## 2. Scope

### Data Sources
- Blogs
- Gourmet sites
- Public datasets
- SNS (optional)

### Region Granularity
- Prefecture (initial)

### Outputs
- JSON / Parquet
- CSV
- Map visualization

---

## 3. Methodology

We combine weak evidence from:
- Articles (regional claims)
- Restaurant observations
- Social conversations

---

## 4. Data Sources Strategy

Priority:
1. APIs
2. RSS
3. Static HTML
4. Playwright (limited)

---

## 5. Non-functional Requirements

- Python 3.11+
- GPU: 16GB x2
- Respect robots.txt
- Rate limiting
- No CAPTCHA bypass

---

## 6. System Architecture

Pipeline:
1. Crawl
2. Extract
3. Classify
4. Aggregate
5. Visualize

---

## 7. Libraries

### Crawling
- httpx
- aiohttp
- trafilatura
- playwright

### Data
- pandas
- polars

### Geo
- geopandas
- folium

### NLP
- transformers
- sentence-transformers

---

## 8. Local LLM

Used for:
- Classification
- Evidence extraction

---

## 9. Data Model

### EvidenceRecord

```json
{
  "prefecture": "大阪府",
  "label": "prepared_tare",
  "confidence": 0.9
}
```

---

## 10. Scoring

Weighted aggregation per prefecture.

---

## 11. Crawl Policy

- Low frequency
- Domain-aware rate limit
- Cache responses

---

## 12. Public Data

- e-Stat
- National Land Numerical Info (GeoJSON)

---

## 13. Repo Structure

```
gyoza-tare-map/
  docs/
  data/
  src/
  scripts/
  outputs/
```

---

## 14. Phases

Phase 1:
- Tokyo, Osaka, Kanagawa, Hyogo

Phase 2:
- LLM integration

Phase 3:
- Nationwide

---

## 15. Initial Tasks

- schema.md
- labels.md
- crawl_policy.md

---

## 16. Strategy

Start simple:
- Rule-based
- Small dataset
- Then scale

---

