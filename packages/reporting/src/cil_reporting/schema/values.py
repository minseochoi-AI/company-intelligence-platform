"""Canonical responsibility owner; migrated from src/company_intel/exporting.py."""

from __future__ import annotations
from cil_domain.provenance.manifests import sanitize_manifest_value
from cil_domain.provenance.redaction import sanitize_export_row
from cil_domain.provenance.redaction import validate_output_directory
from datetime import UTC, date, datetime
from typing import Any
import json


def _safe_export_row(row: dict[str, Any]) -> dict[str, Any]:
    """Apply manifest redaction before spreadsheet formula sanitization."""
    safe_row = sanitize_manifest_value(row)
    if not isinstance(safe_row, dict):
        return {}
    return sanitize_export_row(safe_row)


def item_or_empty(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, default=_json_export_default
    )


def _json_export_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)
