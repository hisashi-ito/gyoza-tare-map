"""Evaluate the rule-based classifier against a labeled test set.

Usage:
    python scripts/evaluate_classifier.py [--testset PATH]

Output: per-label precision / recall / F1, plus macro averages.
"""
from __future__ import annotations

import argparse
import datetime
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
DEFAULT_TESTSET = ROOT / "tests" / "classifier_testset.yaml"

# Make sure the package is importable
import sys
sys.path.insert(0, str(ROOT / "src"))

from gyoza_tare_map.classify.rule_classifier import RuleClassifier
from gyoza_tare_map.config import LABELS
from gyoza_tare_map.models import ExtractedSnippet


def load_cases(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["cases"]


def make_snippet(text: str) -> ExtractedSnippet:
    return ExtractedSnippet(
        url="test://local",
        fetched_at=datetime.datetime.now(tz=datetime.timezone.utc),
        prefecture_hint="東京都",
        text=text,
        char_count=len(text),
    )


def compute_metrics(
    y_true: list[str], y_pred: list[str], labels: list[str]
) -> dict[str, dict[str, float]]:
    """Return per-label precision, recall, F1, support."""
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)

    for gold, pred in zip(y_true, y_pred):
        if gold == pred:
            tp[gold] += 1
        else:
            fp[pred] += 1
            fn[gold] += 1

    support: dict[str, int] = defaultdict(int)
    for g in y_true:
        support[g] += 1

    metrics: dict[str, dict[str, float]] = {}
    for label in labels:
        p = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) > 0 else 0.0
        r = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        metrics[label] = {"precision": p, "recall": r, "f1": f1, "support": support[label]}

    return metrics


def print_report(metrics: dict[str, dict[str, float]], y_true: list[str], y_pred: list[str]) -> None:
    header = f"{'label':<25} {'precision':>9} {'recall':>9} {'f1':>9} {'support':>8}"
    print(header)
    print("-" * len(header))

    active_labels = [l for l in metrics if metrics[l]["support"] > 0]
    for label in active_labels:
        m = metrics[label]
        print(
            f"{label:<25} {m['precision']:>9.3f} {m['recall']:>9.3f}"
            f" {m['f1']:>9.3f} {m['support']:>8.0f}"
        )

    print("-" * len(header))

    # Macro average (over labels with support > 0)
    macro_p = sum(metrics[l]["precision"] for l in active_labels) / len(active_labels)
    macro_r = sum(metrics[l]["recall"] for l in active_labels) / len(active_labels)
    macro_f1 = sum(metrics[l]["f1"] for l in active_labels) / len(active_labels)
    n = len(y_true)
    print(f"{'macro avg':<25} {macro_p:>9.3f} {macro_r:>9.3f} {macro_f1:>9.3f} {n:>8}")

    # Accuracy
    correct = sum(1 for g, p in zip(y_true, y_pred) if g == p)
    print(f"\nAccuracy: {correct}/{n} = {correct/n:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--testset", type=Path, default=DEFAULT_TESTSET)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-case results")
    args = parser.parse_args()

    cases = load_cases(args.testset)
    classifier = RuleClassifier()

    y_true: list[str] = []
    y_pred: list[str] = []

    if args.verbose:
        print(f"\n{'#':<4} {'gold':<25} {'pred':<25} {'conf':>6}  text[:60]")
        print("-" * 100)

    for i, case in enumerate(cases):
        gold = case["label"]
        text = case["text"].strip()
        snippet = make_snippet(text)
        record = classifier.classify(snippet)

        y_true.append(gold)
        y_pred.append(record.label)

        if args.verbose:
            match = "OK" if gold == record.label else "NG"
            print(
                f"{i+1:<4} {gold:<25} {record.label:<25} {record.confidence:>6.3f}"
                f"  {match}  {text[:60].replace(chr(10), ' ')!r}"
            )

    print(f"\n=== Classifier Evaluation ({args.testset.name}) ===\n")
    metrics = compute_metrics(y_true, y_pred, LABELS)
    print_report(metrics, y_true, y_pred)


if __name__ == "__main__":
    main()
