"""Canonical responsibility owner; migrated from src/company_intel/exporting.py."""

from __future__ import annotations
from cil_domain.provenance.manifests import sanitize_manifest_value
from datetime import UTC, date, datetime
from typing import Any
import hashlib
import json


def build_export_manifest(
    files: dict[str, bytes],
    *,
    generated_at: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "format_version": "1",
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "files": [
            {
                "name": name,
                "sha256": hashlib.sha256(value).hexdigest(),
                "bytes": len(value),
            }
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


def selection_run_ref(run_manifest: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(run_manifest, dict):
        return None
    return {
        "run_id": run_manifest.get("run_id"),
        "snapshot_id": (run_manifest.get("snapshot_ref") or {}).get("snapshot_id")
        if isinstance(run_manifest.get("snapshot_ref"), dict)
        else None,
        "manifest_sha256": hashlib.sha256(
            json.dumps(
                sanitize_manifest_value(run_manifest),
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest(),
    }


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
