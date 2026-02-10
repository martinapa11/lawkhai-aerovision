"""
Configuration utilities for Lawkhai Aerovision Phase 1.

This module keeps all environment / path / model configuration
in one place so that:
- The AI tutor backend is easy to reason about.
- Safety parameters are explicit and reviewable.
- Nothing here encodes aircraft‑specific procedures.

All values are concept‑level and training‑oriented.
"""

from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class RagSettings:
    """
    Configuration for the RAG (Retrieval‑Augmented Generation) layer.

    These settings are intentionally generic:
    they control how training documents are indexed and queried,
    not any real‑world maintenance behavior.
    """

    data_dir: Path = BASE_DIR / "data"
    index_dir: Path = BASE_DIR / "indexes"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_chunk_size: int = 1000
    chunk_overlap: int = 100


@dataclass
class SafetySettings:
    """
    Configuration for the safety filter.

    This is where we define:
    - Keywords and patterns associated with procedural or task‑based queries.
    - Response style for redirects back to conceptual learning.
    """

    # A lightweight, conservative list; the filter logic can expand on this.
    blocked_verbs: tuple[str, ...] = (
        "remove",
        "install",
        "torque",
        "replace",
        "adjust",
        "troubleshoot",
        "repair",
        "fix",
        "service",
    )
    # Optional environment toggle for stricter blocking.
    strict_mode: bool = os.getenv("LAWKHAI_STRICT_MODE", "1") == "1"

@dataclass
class ComplianceSettings:
    """
    Configuration for safety/compliance logging.

    Logging is designed for *review and auditability* without collecting
    personal data. By default, blocked events are logged as minimal JSONL
    records with a salted one-way hash of the query text (no raw query).
    """

    enabled: bool = os.getenv("LAWKHAI_COMPLIANCE_LOG", "1") == "1"
    log_dir: Path = BASE_DIR / "logs"
    blocked_log_name: str = "blocked_queries.jsonl"
    # Salt is optional but recommended; it reduces the chance of brute-forcing
    # query hashes. Set via environment variable in your deployment.
    hash_salt: str = os.getenv("LAWKHAI_LOG_SALT", "")
    # Keep this False to avoid storing raw user text.
    store_query_preview: bool = os.getenv("LAWKHAI_STORE_QUERY_PREVIEW", "0") == "1"


@dataclass
class AppSettings:
    """
    Top‑level configuration object for the backend.
    """

    rag: RagSettings = RagSettings()
    safety: SafetySettings = SafetySettings()
    compliance: ComplianceSettings = ComplianceSettings()


def get_settings() -> AppSettings:
    """
    Return a singleton‑style settings object.

    In a more complex system we might cache this,
    but for this Phase 1 backend a simple function is sufficient.
    """

    return AppSettings()


__all__ = [
    "get_settings",
    "AppSettings",
    "RagSettings",
    "SafetySettings",
    "ComplianceSettings",
    "BASE_DIR",
]

