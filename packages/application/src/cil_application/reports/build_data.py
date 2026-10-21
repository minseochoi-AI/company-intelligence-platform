"""Canonical responsibility owner; migrated from src/company_intel/exporting.py."""

from __future__ import annotations
from cil_contracts.reports import ExportBundle
from cil_domain.provenance.export import _run_manifest_table_rows
from cil_domain.provenance.export import build_export_manifest
from cil_domain.provenance.export import selection_run_ref
from cil_domain.provenance.manifests import sanitize_manifest_value
from cil_domain.provenance.redaction import sanitize_export_row
from cil_domain.provenance.redaction import validate_output_directory
from cil_application.ports import render_csv_bundle
from cil_application.ports import render_xlsx_workbook
from pathlib import Path
from typing import Any
import hashlib
import json


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
    denominators: list[dict[str, Any]] | None = None,
    trend_eligibility: list[dict[str, Any]] | None = None,
    run_manifest: dict[str, Any] | list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    include_xlsx: bool = True,
    allowed_root: Path | None = None,
) -> ExportBundle:
    destination = validate_output_directory(destination, allowed_root)
    safe_run_manifest = (
        sanitize_manifest_value(run_manifest) if run_manifest is not None else None
    )
    if safe_run_manifest is not None and (
        not isinstance(safe_run_manifest, (dict, list))
    ):
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
        "denominators": denominators or [],
        "trend_eligibility": trend_eligibility or [],
        "selection_run": [selection_run_ref(safe_run_manifest)]
        if isinstance(safe_run_manifest, dict)
        else [],
    }
    files = render_csv_bundle(tables)
    xlsx = render_xlsx_workbook(tables) if include_xlsx else None
    if xlsx is not None:
        files["company-intelligence.xlsx"] = xlsx
    if safe_run_manifest is not None:
        files["run_manifest.json"] = (
            json.dumps(safe_run_manifest, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        ).encode("utf-8")
    manifest_metadata = dict(metadata or {})
    if isinstance(safe_run_manifest, dict):
        manifest_metadata["run_id"] = safe_run_manifest.get("run_id")
    if safe_run_manifest is not None:
        manifest_metadata["run_manifest_sha256"] = hashlib.sha256(
            files["run_manifest.json"]
        ).hexdigest()
    manifest = build_export_manifest(files, metadata=manifest_metadata or None)
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    files["manifest.json"] = manifest_bytes
    for name, content in files.items():
        (destination / name).write_bytes(content)
    return ExportBundle(files, manifest)
