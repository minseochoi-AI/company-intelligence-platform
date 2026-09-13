from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from .run_manifest import sanitize_manifest_value
from .security import sanitize_export_row, validate_output_directory

JOB_EXPORT_HEADERS = (
    "provider", "job_id", "company_id", "entity_id", "company_name", "company_type", "industry_raw",
    "business_unit", "institution_type_code", "institution_type_raw", "title", "title_raw",
    "occupation_label", "occupation_code", "occupation_system", "country_code", "location_raw", "city",
    "region", "workplace_type", "employment_type", "employment_type_raw", "posting_language",
    "salary_min", "salary_max", "salary_currency", "salary_period", "salary_period_raw", "salary_basis",
    "posted_at", "updated_at", "closing_at", "snapshot_at", "snapshot_date", "is_active", "source_url",
    "normalization_notes",
)

VERDICT_EXPORT_HEADERS = (
    "subject_type", "subject_id", "provider", "job_id", "company_id", "entity_id", "company_name",
    "field", "verdict", "reason", "expected_value", "observed_value", "left_value", "right_value",
    "source_url",
)

TABLE_HEADERS = {
    "companies": ("company_id", "legal_name", "country_code", "industry_code"),
    "capabilities": ("company_id", "operation_id", "capability", "status", "source_url", "available_at"),
    "jobs": JOB_EXPORT_HEADERS,
    "locations": (
        "provider", "job_id", "company_name", "location_raw", "country_code", "city", "region",
        "location_role", "source_field",
    ),
    "requirements": (
        "provider", "job_id", "company_name", "requirement_id", "requirement_kind", "normalized_key",
        "label", "necessity", "value", "proficiency", "text", "requirement_status", "evidence_scope",
        "source_url", "observed_at", "confidence",
    ),
    "sources": (
        "source_id", "provider", "operation_id", "snapshot_at", "record_count", "coverage",
        "limitations", "source_url",
    ),
    "exclusions": (
        "company_id", "provider", "job_id", "company_name", "field", "reason", "observed_value",
    ),
    "strict_matches": JOB_EXPORT_HEADERS + ("preference_hits",),
    "no_matches": VERDICT_EXPORT_HEADERS,
    "unverifiable": VERDICT_EXPORT_HEADERS,
    "unverifiable_candidates": VERDICT_EXPORT_HEADERS,
    "conflicts": VERDICT_EXPORT_HEADERS,
    "facets": (
        "semantic_field", "scope", "normalized_value", "display_label", "vocabulary_namespace",
        "provider", "raw_field", "record_count", "coverage_ratio", "filterability", "sortability",
        "comparability_requirements", "evidence_status",
    ),
    "run_manifest": (
        "run_id", "schema_version", "command", "generated_at", "profile_sha256", "facet_snapshot_sha256",
        "source_snapshot_sha256", "facet_count", "source_count", "verdict_counts", "output_manifest_sha256",
    ),
    "career_overlap": (
        "requirement_kind", "normalized_key", "label", "required_count", "preferred_count",
        "posting_count", "company_count", "country_count", "prevalence",
    ),
}


@dataclass(frozen=True)
class ExportBundle:
    files: dict[str, bytes]
    manifest: dict[str, Any]


def _safe_export_row(row: dict[str, Any]) -> dict[str, Any]:
    """Apply manifest redaction before spreadsheet formula sanitization."""
    safe_row = sanitize_manifest_value(row)
    if not isinstance(safe_row, dict):
        return {}
    return sanitize_export_row(safe_row)


def _csv_bytes(headers: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in sorted(
        (_safe_export_row(row) for row in rows),
        key=lambda item: tuple(str(item.get(key, "")) for key in headers),
    ):
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
        for row in sorted(
            (_safe_export_row(row) for row in tables.get(name, [])),
            key=lambda item: tuple(str(item.get(key, "")) for key in headers),
        ):
            sheet.append([item_or_empty(row.get(header)) for header in headers])
        sheet.freeze_panes = "A2"
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def build_export_manifest(
    files: dict[str, bytes], *, generated_at: str | None = None, metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
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
    if metadata:
        safe_metadata = sanitize_manifest_value(metadata)
        if isinstance(safe_metadata, dict):
            manifest["metadata"] = safe_metadata
    return manifest


def _run_manifest_table_rows(run_manifest: Any) -> list[dict[str, Any]]:
    """Project a full manifest to one spreadsheet-safe lineage summary row."""
    if isinstance(run_manifest, list):
        return [item for item in run_manifest if isinstance(item, dict)]
    if not isinstance(run_manifest, dict):
        return []
    lineage = run_manifest.get("lineage")
    if not isinstance(lineage, dict):
        lineage = {}
    facets = run_manifest.get("facets")
    sources = run_manifest.get("sources")
    return [
        {
            "run_id": run_manifest.get("run_id"),
            "schema_version": run_manifest.get("schema_version"),
            "command": run_manifest.get("command"),
            "generated_at": run_manifest.get("generated_at"),
            "profile_sha256": lineage.get("profile_sha256"),
            "facet_snapshot_sha256": lineage.get("facet_snapshot_sha256"),
            "source_snapshot_sha256": lineage.get("source_snapshot_sha256"),
            "facet_count": len(facets) if isinstance(facets, list) else 0,
            "source_count": len(sources) if isinstance(sources, list) else 0,
            "verdict_counts": run_manifest.get("verdict_counts", {}),
            "output_manifest_sha256": lineage.get("output_manifest_sha256"),
        }
    ]


def build_export_bundle(
    destination: Path,
    *,
    companies: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
    locations: list[dict[str, Any]] | None = None,
    career_overlap: list[dict[str, Any]] | None = None,
    strict_matches: list[dict[str, Any]] | None = None,
    no_matches: list[dict[str, Any]] | None = None,
    unverifiable: list[dict[str, Any]] | None = None,
    unverifiable_candidates: list[dict[str, Any]] | None = None,
    conflicts: list[dict[str, Any]] | None = None,
    facets: list[dict[str, Any]] | None = None,
    run_manifest: dict[str, Any] | list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    include_xlsx: bool = True,
    allowed_root: Path | None = None,
) -> ExportBundle:
    destination = validate_output_directory(destination, allowed_root)
    safe_run_manifest = sanitize_manifest_value(run_manifest) if run_manifest is not None else None
    if safe_run_manifest is not None and not isinstance(safe_run_manifest, (dict, list)):
        raise ValueError("run_manifest must be an object or a list of manifest rows")
    tables = {
        "companies": companies,
        "capabilities": capabilities,
        "jobs": jobs,
        "locations": locations or [],
        "requirements": requirements,
        "sources": sources,
        "exclusions": exclusions,
        "career_overlap": career_overlap or [],
        "strict_matches": strict_matches or [],
        "no_matches": no_matches or [],
        "unverifiable": unverifiable or [],
        "unverifiable_candidates": unverifiable_candidates or [],
        "conflicts": conflicts or [],
        "facets": facets or [],
        "run_manifest": _run_manifest_table_rows(safe_run_manifest),
    }
    files = render_csv_bundle(tables)
    xlsx = render_xlsx_workbook(tables) if include_xlsx else None
    if xlsx is not None:
        files["company-intelligence.xlsx"] = xlsx
    if safe_run_manifest is not None:
        files["run_manifest.json"] = (
            json.dumps(safe_run_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    manifest_metadata = dict(metadata or {})
    if isinstance(safe_run_manifest, dict):
        manifest_metadata["run_id"] = safe_run_manifest.get("run_id")
    if safe_run_manifest is not None:
        manifest_metadata["run_manifest_sha256"] = hashlib.sha256(files["run_manifest.json"]).hexdigest()
    manifest = build_export_manifest(files, metadata=manifest_metadata or None)
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    files["manifest.json"] = manifest_bytes
    for name, content in files.items():
        (destination / name).write_bytes(content)
    return ExportBundle(files, manifest)
