"""Canonical responsibility owner; migrated from src/company_intel/exporting.py."""

from __future__ import annotations
from cil_contracts.reports import TABLE_HEADERS
from cil_reporting.schema.values import _safe_export_row
from cil_reporting.schema.values import item_or_empty
from typing import Any
import csv
import io


def _csv_bytes(headers: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=headers, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    for row in sorted(
        (_safe_export_row(row) for row in rows),
        key=lambda item: tuple((str(item.get(key, "")) for key in headers)),
    ):
        writer.writerow({header: item_or_empty(row.get(header)) for header in headers})
    return stream.getvalue().encode("utf-8")


def render_csv_bundle(tables: dict[str, list[dict[str, Any]]]) -> dict[str, bytes]:
    return {
        f"{name}.csv": _csv_bytes(headers, tables.get(name, []))
        for name, headers in TABLE_HEADERS.items()
    }


def write_csv_tables(destination, tables):
    from pathlib import Path

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, table in tables.items():
        if not name.replace("_", "").isalnum():
            raise ValueError("invalid table name")
        path = destination / (name + ".csv")
        path.write_bytes(_csv_bytes(tuple(table["columns"]), table["rows"]))
        outputs.append(path)
    return outputs
