"""Keyword dictionaries per condiment label.

These patterns are used by rule_classifier.py for Phase 1.
Each entry is a list of Japanese keyword strings. Pattern matching is
exact substring search on NFKC-normalized text.

Edit this file to tune Phase 1 accuracy before moving to LLM (Phase 2).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# prepared_tare: pre-made bottled sauce served at/from the restaurant
# ---------------------------------------------------------------------------
PREPARED_TARE: list[str] = [
    "タレ",
    "たれ",
    "付属のたれ",
    "付属タレ",
    "専用タレ",
    "秘伝のタレ",
    "秘伝たれ",
    "ラー油",
    "らー油",
    "辣油",
    "酢醤油タレ",
    "酢しょうゆタレ",
    "ついてくるたれ",
    "店のタレ",
    "お店のたれ",
    "オリジナルタレ",
    "特製タレ",
    "特製たれ",
    "ポン酢",
    "ぽん酢",
]

# ---------------------------------------------------------------------------
# self_mix_soy_vinegar: customer mixes soy sauce and vinegar at the table
# ---------------------------------------------------------------------------
SELF_MIX_SOY_VINEGAR: list[str] = [
    "自分で酢醤油",
    "自分でかける",
    "酢と醤油",
    "お酢と醤油",
    "酢醤油を作",
    "酢醤油で食べ",
    "酢じょうゆ",
    "酢しょうゆ",
    "卓上の酢",
    "卓上酢",
    "テーブルの酢",
    "割って食べ",
    "自分で割る",
    "酢をかけ",
    "醤油と酢",
]

# ---------------------------------------------------------------------------
# miso_dare: miso-based dipping sauce
# ---------------------------------------------------------------------------
MISO_DARE: list[str] = [
    "味噌だれ",
    "みそだれ",
    "味噌タレ",
    "みそタレ",
    "みそだれ",
    "味噌で食べ",
    "味噌をつけ",
    "名古屋の味噌",
    "赤味噌",
    "八丁味噌",
]

# ---------------------------------------------------------------------------
# su_kosho: vinegar + pepper (black/white pepper sprinkled with vinegar)
# ---------------------------------------------------------------------------
SU_KOSHO: list[str] = [
    "酢コショウ",
    "酢こしょう",
    "酢胡椒",
    "酢とコショウ",
    "酢と胡椒",
    "酢とこしょう",
    "コショウと酢",
    "胡椒と酢",
    "酢をかけてコショウ",
    "酢コショ",
]

# ---------------------------------------------------------------------------
# other_local_style: regional variants not covered by the above
# ---------------------------------------------------------------------------
OTHER_LOCAL_STYLE: list[str] = [
    "マヨネーズ",
    "マヨ",
    "ゆずこしょう",
    "柚子胡椒",
    "ゆず胡椒",
    "ごまだれ",
    "胡麻だれ",
    "ねぎ塩",
    "ネギ塩",
    "塩だれ",
    "しょうがじょうゆ",
    "生姜醤油",
    "ニンニク醤油",
    "にんにく醤油",
    "XO醤",
    "豆板醤",
    "トウバンジャン",
]

# Label → keyword list mapping (used by rule_classifier.py)
LABEL_KEYWORDS: dict[str, list[str]] = {
    "prepared_tare": PREPARED_TARE,
    "self_mix_soy_vinegar": SELF_MIX_SOY_VINEGAR,
    "miso_dare": MISO_DARE,
    "su_kosho": SU_KOSHO,
    "other_local_style": OTHER_LOCAL_STYLE,
}
