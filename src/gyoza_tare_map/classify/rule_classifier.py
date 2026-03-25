"""Phase 1: keyword-count rule-based classifier."""
from __future__ import annotations

import unicodedata
from pathlib import Path

from gyoza_tare_map.classify.base import Classifier
from gyoza_tare_map.classify.labels import LABEL_KEYWORDS
from gyoza_tare_map.config import (
    AMBIGUOUS_MARGIN,
    CLASSIFIED_JSONL,
    EXTRACTED_JSONL,
    MAX_RULE_CONFIDENCE,
    MIN_CONFIDENCE,
)
from gyoza_tare_map.models import ClassifiedRecord, ExtractedSnippet

VERSION = "rule_v1"


class RuleClassifier(Classifier):
    def classify(self, snippet: ExtractedSnippet) -> ClassifiedRecord:
        text = unicodedata.normalize("NFKC", snippet.text)

        # Count keyword hits per label
        scores: dict[str, int] = {label: 0 for label in LABEL_KEYWORDS}
        for label, keywords in LABEL_KEYWORDS.items():
            for kw in keywords:
                scores[label] += text.count(kw)

        total_hits = sum(scores.values())

        if total_hits == 0:
            return ClassifiedRecord(
                url=snippet.url,
                fetched_at=snippet.fetched_at,
                prefecture=snippet.prefecture_hint,
                label="unknown",
                confidence=0.0,
                classifier_version=VERSION,
                snippet_text=snippet.text[:500],
                ambiguous=False,
            )

        # Normalize to [0, 1]
        norm: dict[str, float] = {label: count / total_hits for label, count in scores.items()}
        sorted_labels = sorted(norm, key=lambda l: norm[l], reverse=True)
        top_label = sorted_labels[0]
        top_score = norm[top_label]
        second_score = norm[sorted_labels[1]] if len(sorted_labels) > 1 else 0.0

        confidence = min(top_score, MAX_RULE_CONFIDENCE)
        ambiguous = (top_score - second_score) <= AMBIGUOUS_MARGIN

        if confidence < MIN_CONFIDENCE:
            top_label = "unknown"

        return ClassifiedRecord(
            url=snippet.url,
            fetched_at=snippet.fetched_at,
            prefecture=snippet.prefecture_hint,
            label=top_label,
            confidence=confidence,
            classifier_version=VERSION,
            snippet_text=snippet.text[:500],
            ambiguous=ambiguous,
        )


def run(
    input_path: Path = EXTRACTED_JSONL,
    output_path: Path = CLASSIFIED_JSONL,
    dry_run: bool = False,
) -> list[ClassifiedRecord]:
    classifier = RuleClassifier()
    records: list[ClassifiedRecord] = []
    skipped = 0

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            snippet = ExtractedSnippet.from_json(line)
            if not snippet.prefecture_hint:
                skipped += 1
                continue
            record = classifier.classify(snippet)
            records.append(record)

    print(f"[classify] {len(records)} records classified, {skipped} skipped (no prefecture).")

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r.to_json() + "\n")
        print(f"[classify] Wrote → {output_path}")

    return records
