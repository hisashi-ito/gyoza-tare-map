"""Write aggregated scores to Parquet and CSV using pandas."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from gyoza_tare_map.config import LABELS, OUTPUT_CSV, OUTPUT_PARQUET
from gyoza_tare_map.models import PrefectureScore


def to_dataframe(scores: list[PrefectureScore]) -> pd.DataFrame:
    rows = []
    for s in scores:
        row: dict = {
            "prefecture": s.prefecture,
            "dominant_label": s.dominant_label,
            "evidence_count": s.evidence_count,
            "confidence_mean": s.confidence_mean,
            "low_evidence": s.low_evidence,
        }
        for label in LABELS:
            row[f"score_{label}"] = s.label_scores.get(label, 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def write(
    scores: list[PrefectureScore],
    parquet_path: Path = OUTPUT_PARQUET,
    csv_path: Path = OUTPUT_CSV,
    dry_run: bool = False,
) -> pd.DataFrame:
    df = to_dataframe(scores)
    if not dry_run:
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(parquet_path, index=False)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[writer] Wrote Parquet → {parquet_path}")
        print(f"[writer] Wrote CSV    → {csv_path}")
    return df
