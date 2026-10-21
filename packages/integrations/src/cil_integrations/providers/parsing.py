"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyless.py."""

from __future__ import annotations
from cil_domain.providers.parsing import get_path
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from typing import Any, Iterable, Iterator, Mapping


def _select(mapping: dict[str, str]):
    from cil_domain.providers.parsing import MISSING

    def safe_normalize(body: bytes, _: str) -> dict[str, Any]:
        data = json_payload(body)
        output: dict[str, Any] = {}
        for label, path in mapping.items():
            value = get_path(data, path)
            output[label] = None if value is MISSING else preserve_payload(value)
        return output

    return safe_normalize
