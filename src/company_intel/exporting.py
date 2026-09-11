from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from .security import sanitize_export_row, validate_output_directory

TABLE_HEADERS = {
    "companies": ("company_id", "legal_name", "country_code", "industry_code"),
    "capabilities": ("company_id", "operation_id", "capability", "status", "source_url", "available_at"),
    "jobs": ("provider", "job_id", "company_id", "title", "country_code", "posted_at", "snapshot_date", "is_active"),
    "requirements": ("provider", "job_id", "requirement_id", "text", "requirement_status", "evidence_scope", "source_url", "observed_at"),
    "sources": ("source_id", "source_url"),
    "exclusions": ("company_id", "reason"),
    "unverifiable": ("subject_type", "subject_id", "field", "reason", "observed_value", "source_url"),
    "conflicts": ("subject_type", "subject_id", "field", "reason", "left_value", "right_value", "source_url"),
    "career_overlap": (
        "requirement_kind", "normalized_key", "label", "required_count", "preferred_count",
        "posting_count", "company_count", "country_count", "prevalence",
    ),
}


@dataclass(frozen=True)
class ExportBundle:
    files: dict[str, bytes]
    manifest: dict[str, Any]


def _csv_bytes(headers: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in sorted((sanitize_export_row(row) for row in rows), key=lambda item: tuple(str(item.get(key, "")) for key in headers)):
        writer.writerow({header: item_or_empty(row.get(header)) for header in headers})
    return stream.getvalue().encode("utf-8")


def item_or_empty(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    # DuckDB returns DATE/TIMESTAMP objects for the evidence tables.  CSV and
    # XLSX are portable text contracts, so preserve their exact ISO meaning
    # instead of failing the whole export or applying a locale-dependent cast.
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=_json_export_default)


def _json_export_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def render_csv_bundle(tables: dict[str, list[dict[str, Any]]]) -> dict[str, bytes]:
    return {f"{name}.csv": _csv_bytes(headers, tables.get(name, [])) for name, headers in TABLE_HEADERS.items()}


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
        for row in sorted((sanitize_export_row(row) for row in tables.get(name, [])), key=lambda item: tuple(str(item.get(key, "")) for key in headers)):
            sheet.append([item_or_empty(row.get(header)) for header in headers])
        sheet.freeze_panes = "A2"
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def build_export_manifest(files: dict[str, bytes], *, generated_at: str | None = None) -> dict[str, Any]:
    return {
        "format_version": "1",
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "files": [
            {"name": name, "sha256": hashlib.sha256(value).hexdigest(), "bytes": len(value)}
            for name, value in sorted(files.items())
        ],
        "limitations": [
            "Rows without verified requirement evidence remain in exclusions or availability fields.",
            "CSV is the canonical contract; XLSX, if present, renders the same tables.",
        ],
        "lineage": "Each row must retain provider, source URL or explicit exclusion/verification reason.",
    }


def build_export_bundle(destination: Path, *, companies: list[dict[str, Any]], capabilities: list[dict[str, Any]], jobs: list[dict[str, Any]], requirements: list[dict[str, Any]], sources: list[dict[str, Any]], exclusions: list[dict[str, Any]], career_overlap: list[dict[str, Any]] | None = None, unverifiable: list[dict[str, Any]] | None = None, conflicts: list[dict[str, Any]] | None = None, include_xlsx: bool = True, allowed_root: Path | None = None) -> ExportBundle:
    destination = validate_output_directory(destination, allowed_root)
    tables = {"companies": companies, "capabilities": capabilities, "jobs": jobs, "requirements": requirements, "sources": sources, "exclusions": exclusions, "career_overlap": career_overlap or [], "unverifiable": unverifiable or [], "conflicts": conflicts or []}
    files = render_csv_bundle(tables)
    xlsx = render_xlsx_workbook(tables) if include_xlsx else None
    if xlsx is not None:
        files["company-intelligence.xlsx"] = xlsx
    manifest = build_export_manifest(files)
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    files["manifest.json"] = manifest_bytes
    for name, content in files.items():
        (destination / name).write_bytes(content)
    return ExportBundle(files, manifest)
