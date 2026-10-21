"""Canonical responsibility owner; migrated from src/company_intel/exporting.py."""

from __future__ import annotations
from cil_contracts.reports import TABLE_HEADERS
from cil_reporting.schema.values import _safe_export_row
from cil_reporting.schema.values import item_or_empty
from typing import Any
import io


def render_xlsx_workbook(tables: dict[str, list[dict[str, Any]]]) -> bytes | None:
    try:
        from openpyxl import Workbook
    except ImportError:
        return None
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name, headers in TABLE_HEADERS.items():
        sheet = workbook.create_sheet(name)
        sheet.append(list(headers))
        for row in sorted(
            (_safe_export_row(row) for row in tables.get(name, [])),
            key=lambda item: tuple((str(item.get(key, "")) for key in headers)),
        ):
            sheet.append([item_or_empty(row.get(header)) for header in headers])
        sheet.freeze_panes = "A2"
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()
