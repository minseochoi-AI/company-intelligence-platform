"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping


def _alpha(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    series_key = next((key for key in data if "Time Series" in key), None)
    series = data.get(series_key, {}) if series_key else {}
    prices = [
        {
            "symbol": data.get("Meta Data", {}).get("2. Symbol", "IBM"),
            "price_date": day,
            "open": to_number(values.get("1. open")),
            "high": to_number(values.get("2. high")),
            "low": to_number(values.get("3. low")),
            "close": to_number(values.get("4. close")),
            "volume": to_number(values.get("5. volume")),
            "adjustment": "raw",
        }
        for day, values in series.items()
    ]
    return {
        "meta": preserve_payload(data.get("Meta Data", {})),
        "row_count": len(prices),
        "prices": prices,
        "provider_note": data.get("Note")
        or data.get("Information")
        or data.get("Error Message"),
    }
