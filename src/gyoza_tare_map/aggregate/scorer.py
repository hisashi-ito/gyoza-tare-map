"""Weighted aggregation of ClassifiedRecord → PrefectureScore per prefecture."""
from __future__ import annotations

from gyoza_tare_map.config import LABELS
from gyoza_tare_map.models import ClassifiedRecord, PrefectureScore

LOW_EVIDENCE_THRESHOLD = 5


def score(records: list[ClassifiedRecord]) -> list[PrefectureScore]:
    """Aggregate records by prefecture using confidence-weighted voting."""
    # Group by prefecture
    by_pref: dict[str, list[ClassifiedRecord]] = {}
    for rec in records:
        if not rec.prefecture:
            continue
        by_pref.setdefault(rec.prefecture, []).append(rec)

    scores: list[PrefectureScore] = []
    for prefecture, recs in by_pref.items():
        # Sum confidence weights per label (exclude "unknown" from scoring)
        label_weights: dict[str, float] = {label: 0.0 for label in LABELS if label != "unknown"}
        for rec in recs:
            if rec.label in label_weights:
                label_weights[rec.label] += rec.confidence

        total_weight = sum(label_weights.values())

        if total_weight == 0:
            label_scores = {label: 0.0 for label in label_weights}
            dominant_label = "unknown"
        else:
            label_scores = {label: w / total_weight for label, w in label_weights.items()}
            dominant_label = max(label_scores, key=lambda l: label_scores[l])

        # Include "unknown" in label_scores for completeness
        label_scores["unknown"] = sum(1 for r in recs if r.label == "unknown") / len(recs)

        confidence_mean = sum(r.confidence for r in recs) / len(recs)

        scores.append(
            PrefectureScore(
                prefecture=prefecture,
                dominant_label=dominant_label,
                label_scores=label_scores,
                evidence_count=len(recs),
                confidence_mean=round(confidence_mean, 4),
                low_evidence=len(recs) < LOW_EVIDENCE_THRESHOLD,
            )
        )

    scores.sort(key=lambda s: s.prefecture)
    print(f"[scorer] Scored {len(scores)} prefectures.")
    return scores
