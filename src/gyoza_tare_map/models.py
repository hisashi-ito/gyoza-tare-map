from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CrawledDocument:
    url: str
    fetched_at: str          # ISO-8601
    source_type: str         # "rss" | "html" | "api" | "playwright"
    status_code: int
    raw_html: str
    domain: str
    content_type: str = ""
    seed_prefectures: list[str] = field(default_factory=list)  # hint from seeds.yaml

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CrawledDocument:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> CrawledDocument:
        return cls.from_dict(json.loads(s))


@dataclass
class ExtractedSnippet:
    url: str
    fetched_at: str
    prefecture_hint: str     # detected prefecture name, or "" if unknown
    text: str                # cleaned text
    char_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ExtractedSnippet:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> ExtractedSnippet:
        return cls.from_dict(json.loads(s))


@dataclass
class ClassifiedRecord:
    url: str
    fetched_at: str
    prefecture: str          # canonical prefecture name
    label: str               # one of LABELS
    confidence: float        # 0.0–1.0
    classifier_version: str  # e.g. "rule_v1", "llm_qwen25_7b"
    snippet_text: str        # kept for audit
    ambiguous: bool = False  # True when top-2 label scores are within AMBIGUOUS_MARGIN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ClassifiedRecord:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> ClassifiedRecord:
        return cls.from_dict(json.loads(s))


@dataclass
class PrefectureScore:
    prefecture: str
    dominant_label: str
    label_scores: dict[str, float]   # {label: weighted_score}
    evidence_count: int
    confidence_mean: float
    low_evidence: bool = False       # True when evidence_count < LOW_EVIDENCE_THRESHOLD

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> PrefectureScore:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
