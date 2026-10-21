"""Canonical responsibility owner; migrated from src/company_intel/live_snapshots.py."""

from __future__ import annotations
from datetime import UTC, datetime
from typing import Any, Callable, Mapping
import hashlib
import json


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def snapshot_freshness(
    collected_at: str | None, *, now: str | None = None, max_age_seconds: int = 86400
) -> dict[str, Any]:
    """Return an explicit freshness verdict without silently refreshing data."""
    if not collected_at:
        return {"status": "missing", "fresh": False, "age_seconds": None}
    try:
        collected = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
        current = datetime.fromisoformat(
            (now or datetime.now(UTC).isoformat()).replace("Z", "+00:00")
        )
    except ValueError:
        return {"status": "invalid_timestamp", "fresh": False, "age_seconds": None}
    age = max(0.0, (current - collected).total_seconds())
    return {
        "status": "fresh" if age <= max_age_seconds else "stale",
        "fresh": age <= max_age_seconds,
        "age_seconds": age,
    }
