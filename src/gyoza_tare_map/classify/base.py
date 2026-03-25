from __future__ import annotations

from abc import ABC, abstractmethod

from gyoza_tare_map.models import ClassifiedRecord, ExtractedSnippet


class Classifier(ABC):
    """Abstract base for all classifiers (rule-based, LLM, ensemble)."""

    @abstractmethod
    def classify(self, snippet: ExtractedSnippet) -> ClassifiedRecord:
        """Classify a snippet and return a ClassifiedRecord."""
        ...
