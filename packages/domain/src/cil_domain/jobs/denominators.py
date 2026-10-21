"""Canonical responsibility owner; migrated from src/company_intel/current_jobs.py."""

from __future__ import annotations
from typing import Any, Mapping


def _records(frame: Any) -> list[dict[str, Any]]:
    return frame.astype(object).where(frame.notna(), None).to_dict("records")


def summarize_coverage(sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "providers": sorted(
            {str(row.get("provider")) for row in sources if row.get("provider")}
        ),
        "source_count": len(sources),
        "limitations": [
            row.get("limitations") for row in sources if row.get("limitations")
        ],
    }
