"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_api.schemas import SelectionRunRequest
from cil_api.schemas import SelectionRunResponse
from cil_domain.provenance.selection import bind_selection_run
from cil_domain.provenance.selection import verify_run_chain
from fastapi import FastAPI, HTTPException
from typing import Any


@app.post("/v1/selection-runs", response_model=SelectionRunResponse)
def selection_run(request: SelectionRunRequest) -> SelectionRunResponse:
    manifest = bind_selection_run(request.selection, request.snapshot, request.results)
    return SelectionRunResponse(run_id=manifest.run_id, manifest=manifest.as_dict())


@app.post("/v1/selection-runs/replay")
def replay_run(request: SelectionRunRequest) -> dict[str, Any]:
    manifest = bind_selection_run(
        request.selection, request.snapshot, request.results
    ).as_dict()
    if not verify_run_chain(manifest):
        raise HTTPException(422, "selection_manifest_tampered")
    return {
        "status": "replay_ready",
        "run_id": manifest["run_id"],
        "snapshot_ref": manifest["snapshot_ref"],
    }
