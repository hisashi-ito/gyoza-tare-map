"""Prefecture detection from text using a keyword dictionary."""
from __future__ import annotations

import re

from gyoza_tare_map.config import ALL_PREFECTURES

# Alias map: short/alternative names → canonical full name
_ALIASES: dict[str, str] = {
    "北海道": "北海道",
    "青森": "青森県", "岩手": "岩手県", "宮城": "宮城県", "秋田": "秋田県",
    "山形": "山形県", "福島": "福島県",
    "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県",
    "埼玉": "埼玉県", "千葉": "千葉県",
    "東京": "東京都", "神奈川": "神奈川県",
    "新潟": "新潟県", "富山": "富山県", "石川": "石川県", "福井": "福井県",
    "山梨": "山梨県", "長野": "長野県",
    "岐阜": "岐阜県", "静岡": "静岡県", "愛知": "愛知県", "三重": "三重県",
    "滋賀": "滋賀県", "京都": "京都府", "大阪": "大阪府",
    "兵庫": "兵庫県", "奈良": "奈良県", "和歌山": "和歌山県",
    "鳥取": "鳥取県", "島根": "島根県", "岡山": "岡山県",
    "広島": "広島県", "山口": "山口県",
    "徳島": "徳島県", "香川": "香川県", "愛媛": "愛媛県", "高知": "高知県",
    "福岡": "福岡県", "佐賀": "佐賀県", "長崎": "長崎県",
    "熊本": "熊本県", "大分": "大分県", "宮崎": "宮崎県",
    "鹿児島": "鹿児島県", "沖縄": "沖縄県",
    # City-level hints for major cities → prefecture
    "札幌": "北海道",
    "仙台": "宮城県",
    "横浜": "神奈川県",
    "川崎": "神奈川県",
    "名古屋": "愛知県",
    "京都市": "京都府",
    "大阪市": "大阪府",
    "神戸": "兵庫県",
    "元町": "兵庫県",   # 神戸・元町
    "三宮": "兵庫県",
    "広島市": "広島県",
    "福岡市": "福岡県",
    "北九州": "福岡県",
    "那覇": "沖縄県",
    # Regional terms → representative prefecture
    "関西": "大阪府",
    "近畿": "大阪府",
    "関東": "東京都",
    "九州": "福岡県",
    "東北": "宮城県",
    "北陸": "石川県",
    "中国地方": "広島県",
    "四国": "高知県",
}

# Build regex: longest keys first to prefer full names over partial matches
_SORTED_KEYS = sorted(_ALIASES.keys(), key=len, reverse=True)
_PATTERN = re.compile("|".join(re.escape(k) for k in _SORTED_KEYS))


def detect_prefecture(text: str) -> str:
    """Return the first canonical prefecture name found in text, or ''."""
    m = _PATTERN.search(text)
    if m:
        return _ALIASES[m.group(0)]
    return ""


def detect_all_prefectures(text: str) -> list[str]:
    """Return all unique canonical prefecture names found in text."""
    found = {_ALIASES[m.group(0)] for m in _PATTERN.finditer(text)}
    # Preserve the order of ALL_PREFECTURES for consistency
    return [p for p in ALL_PREFECTURES if p in found]
