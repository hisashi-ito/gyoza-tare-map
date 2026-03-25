"""HTML → clean text extraction via trafilatura."""
from __future__ import annotations

import unicodedata

import trafilatura


def extract_text(html: str, url: str = "") -> str:
    """Return clean text from HTML. Returns empty string if extraction fails."""
    text = trafilatura.extract(
        html,
        url=url or None,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
        favor_precision=False,
    )
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # Verify that the text contains Japanese characters (CJK block)
    has_japanese = any("\u3000" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef" for c in text)
    if not has_japanese:
        return ""
    return text.strip()
