"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping


def _alio_plus(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    if not isinstance(data, dict):
        return {"response_type": type(data).__name__, "records": preserve_payload(data)}
    return {
        "result_code": data.get("resultCode") or data.get("code") or data.get("status"),
        "result_message": data.get("resultMsg") or data.get("message"),
        "records": preserve_payload(data),
    }
