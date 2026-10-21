"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from typing import Any, Callable, Mapping


def mpm_detail_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Return only explicit detail fields supplied by a separately authorized MPM detail response.

    The registered list endpoint is intentionally not treated as a requirement source.
    """
    detail = record.get("detail") if isinstance(record.get("detail"), dict) else record
    explicit = detail.get("requirements")
    return {
        "posting_id": detail.get("idx") or detail.get("posting_id"),
        "requirements": explicit if isinstance(explicit, list) else [],
        "availability": "available"
        if isinstance(explicit, list)
        else "requirement_unavailable",
    }
