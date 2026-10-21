"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping


def _ecos(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    root = data.get("StatisticSearch", {})
    rows = root.get("row", [])
    return {
        "result": root.get("RESULT") or data.get("RESULT"),
        "list_total_count": root.get("list_total_count"),
        "observations": [
            {
                "series_code": row.get("STAT_CODE"),
                "series_name": row.get("STAT_NAME"),
                "item_code": row.get("ITEM_CODE1"),
                "item_name": row.get("ITEM_NAME1"),
                "frequency": row.get("CYCLE"),
                "observation_date": row.get("TIME"),
                "value": to_number(row.get("DATA_VALUE")),
                "unit": row.get("UNIT_NAME"),
            }
            for row in rows
        ],
    }
