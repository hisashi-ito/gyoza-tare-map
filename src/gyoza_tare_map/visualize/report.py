"""Summary report: pivot table of label scores per prefecture."""
from __future__ import annotations

import pandas as pd

from gyoza_tare_map.config import LABELS


def print_report(df: pd.DataFrame) -> None:
    """Print a formatted summary table to stdout."""
    cols = ["prefecture", "dominant_label", "evidence_count", "confidence_mean"] + [
        f"score_{label}" for label in LABELS if label != "unknown"
    ]
    display = df[cols].copy()
    display.columns = (
        ["都道府県", "主要ラベル", "証拠数", "平均確信度"]
        + [label for label in LABELS if label != "unknown"]
    )
    display = display.sort_values("証拠数", ascending=False)
    pd.set_option("display.max_rows", 50)
    pd.set_option("display.width", 120)
    pd.set_option("display.float_format", "{:.3f}".format)
    print(display.to_string(index=False))


def low_evidence_warning(df: pd.DataFrame) -> None:
    low = df[df["low_evidence"]]
    if not low.empty:
        prefs = ", ".join(low["prefecture"].tolist())
        print(f"\n[警告] 証拠が少ない都道府県 (< 5件): {prefs}")
