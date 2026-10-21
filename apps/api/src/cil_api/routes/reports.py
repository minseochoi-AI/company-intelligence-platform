"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_api.schemas import ExportRequest
from cil_application.reports.build_data import build_export_bundle
from cil_domain.provenance.manifests import build_run_manifest
from cil_domain.provenance.manifests import result_refs
from cil_integrations.runtime.settings import Settings
from cil_integrations.storage.duckdb.repository import Warehouse
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Any
from uuid import uuid4
import json


@app.post("/v1/exports")
def create_export(request: ExportRequest) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    run_id = f"export-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    output = settings.artifact_dir / "exports" / run_id
    try:
        data = Warehouse(settings).materialize_export_snapshot(
            request.entity_ids or None
        )
        run_manifest = build_run_manifest(
            "v1/exports",
            {"entity_ids": request.entity_ids},
            [],
            data.get("sources", []),
            {},
        )
        bundle = build_export_bundle(
            output,
            include_xlsx=request.include_xlsx,
            allowed_root=settings.artifact_dir,
            run_manifest=run_manifest,
            metadata={"api_run_id": run_id},
            **data,
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {
        "run_id": run_id,
        "status": "completed",
        "output_directory": str(output),
        "manifest": bundle.manifest,
    }


@app.get("/v1/exports/{run_id}")
def export_metadata(run_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    path = settings.artifact_dir / "exports" / run_id / "manifest.json"
    if not path.is_file():
        raise HTTPException(404, "export run not found")
    return {
        "run_id": run_id,
        "status": "completed",
        "manifest": json.loads(path.read_text(encoding="utf-8")),
    }
