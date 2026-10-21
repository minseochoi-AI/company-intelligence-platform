"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping


def _fred(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    rows = data.get("observations", [])
    return {
        "series_id": "FEDFUNDS",
        "realtime_start": data.get("realtime_start"),
        "realtime_end": data.get("realtime_end"),
        "count": data.get("count"),
        "observations": [
            {
                "observation_date": row.get("date"),
                "available_at": row.get("realtime_start"),
                "revision_end": row.get("realtime_end"),
                "value": to_number(row.get("value")),
                "unit": "percent",
            }
            for row in rows
        ],
    }
