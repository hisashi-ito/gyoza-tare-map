"""SQLite-backed HTTP response cache (synchronous sqlite3)."""
from __future__ import annotations

import hashlib
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

from gyoza_tare_map.config import CACHE_DB, CACHE_TTL_DAYS


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS cache (
    url_hash    TEXT PRIMARY KEY,
    url         TEXT NOT NULL,
    fetched_at  TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    content_type TEXT NOT NULL DEFAULT '',
    body        TEXT NOT NULL
)
"""

_lock = threading.Lock()


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute(CREATE_TABLE)
    conn.commit()
    return conn


class ResponseCache:
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = str(db_path or CACHE_DB)
        self._conn = _get_conn(self._db_path)

    async def get(self, url: str) -> dict | None:
        """Return cached response dict or None if missing/expired."""
        with _lock:
            cur = self._conn.execute(
                "SELECT fetched_at, status_code, content_type, body FROM cache WHERE url_hash = ?",
                (_url_hash(url),),
            )
            row = cur.fetchone()

        if row is None:
            return None

        fetched_at_str, status_code, content_type, body = row
        fetched_at = datetime.fromisoformat(fetched_at_str)
        if datetime.now(tz=timezone.utc) - fetched_at > timedelta(days=CACHE_TTL_DAYS):
            return None

        return {
            "url": url,
            "fetched_at": fetched_at_str,
            "status_code": status_code,
            "content_type": content_type,
            "body": body,
        }

    async def set(self, url: str, status_code: int, content_type: str, body: str) -> None:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        with _lock:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO cache
                    (url_hash, url, fetched_at, status_code, content_type, body)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (_url_hash(url), url, fetched_at, status_code, content_type, body),
            )
            self._conn.commit()
