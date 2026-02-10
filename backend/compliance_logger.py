"""
Compliance logging for Lawkhai Aerovision (training-only aviation AI).

Purpose
-------
Support aviation safety culture and academic auditability by logging when
the system blocks or redirects unsafe requests (procedural, task-based,
or diagnostic intent).

Privacy stance (critical)
-------------------------
This logger is designed to avoid storing personal data:
- It does NOT store raw user queries by default.
- It stores only minimal metadata and a salted, one-way hash fingerprint.
- Optional query preview logging is disabled by default and should remain
  off unless a formal privacy review approves it.

Log format
----------
JSON Lines (JSONL), one event per line, suitable for review and analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import threading
from typing import Optional

from .config import get_settings


@dataclass(frozen=True)
class BlockedQueryEvent:
    """
    A minimal, privacy-preserving record for a blocked query.

    Fields intentionally exclude direct user identifiers and raw text.
    """

    timestamp_utc: str
    category: str
    reasons: list[str]
    system_focus: Optional[str]
    query_fingerprint: str
    query_length: int
    # Optional and disabled by default:
    query_preview: Optional[str] = None


class ComplianceLogger:
    """
    Writes privacy-preserving compliance events to a JSONL file.

    The logger is resilient:
    - Logging failures should not crash the tutor.
    - File writes are guarded by a lock for basic thread safety.
    """

    def __init__(self, log_dir: Optional[Path] = None, log_name: Optional[str] = None) -> None:
        settings = get_settings().compliance
        self.enabled: bool = settings.enabled
        self.store_query_preview: bool = settings.store_query_preview
        self.hash_salt: str = settings.hash_salt

        self.log_dir: Path = log_dir or settings.log_dir
        self.log_name: str = log_name or settings.blocked_log_name
        self._lock = threading.Lock()

    def log_blocked_query(
        self,
        query: str,
        category: str,
        reasons: list[str],
        system_focus: Optional[str] = None,
    ) -> None:
        """
        Log a blocked query without storing raw user text.
        """

        if not self.enabled:
            return

        event = BlockedQueryEvent(
            timestamp_utc=_utc_now_iso(),
            category=category,
            reasons=reasons,
            system_focus=system_focus,
            query_fingerprint=_fingerprint_query(query=query, salt=self.hash_salt),
            query_length=len(query),
            query_preview=_safe_preview(query) if self.store_query_preview else None,
        )

        try:
            self._write_jsonl(event)
        except Exception:
            # Never allow logging failures to interrupt the safety redirect.
            return

    def _write_jsonl(self, event: BlockedQueryEvent) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / self.log_name

        line = json.dumps(asdict(event), ensure_ascii=False)
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(query: str) -> str:
    # Normalize whitespace and casing for stable fingerprinting.
    return " ".join(query.strip().lower().split())


def _fingerprint_query(query: str, salt: str) -> str:
    """
    Create a salted SHA-256 fingerprint of the normalized query.

    This supports deduplication and trend review without storing raw text.
    """

    normalized = _normalize_query(query)
    material = (salt + "|" + normalized).encode("utf-8", errors="ignore")
    return sha256(material).hexdigest()


def _safe_preview(query: str, max_len: int = 80) -> str:
    """
    Optional redacted preview (disabled by default).

    This intentionally avoids sophisticated PII detection; it simply truncates
    and normalizes whitespace. Keep store_query_preview disabled unless a
    privacy review explicitly approves storing any user text.
    """

    preview = " ".join(query.strip().split())
    if len(preview) <= max_len:
        return preview
    return preview[: max_len - 3] + "..."


__all__ = ["ComplianceLogger", "BlockedQueryEvent"]

