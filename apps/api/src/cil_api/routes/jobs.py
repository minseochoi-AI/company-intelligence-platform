"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_api.schemas import CurrentJobRequest
from cil_api.schemas import JobSearchRequest
from cil_api.schemas import JobTrendRequest
from cil_application.analysis.service import build_company_timeline
from cil_application.analysis.service import evaluate_ai_event
from cil_application.analysis.service import evaluate_job_trends
from cil_application.analysis.service import evaluate_valuation_scenarios
from cil_application.jobs.current import execute_current_job_search
from cil_application.jobs.search import search_job_dataframes
from cil_contracts.jobs import JobSearchProfile
from cil_domain.provenance.manifests import build_run_manifest
from cil_domain.provenance.manifests import result_refs
from cil_domain.queries.facets import build_job_facets
from cil_integrations.providers.job_records import normalize_provider_payloads
from cil_integrations.runtime.settings import Settings
from cil_integrations.storage.duckdb.repository import Warehouse
from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Any


@app.post("/v1/job-search")
def job_search(request: JobSearchRequest) -> dict[str, Any]:
    try:
        profile = request.to_domain()
        frames = search_job_dataframes(request.payloads, profile)
        all_jobs, _requirements, _sources = normalize_provider_payloads(
            request.payloads
        )
        facets = build_job_facets(all_jobs)
        sources = (
            frames.sources.astype(object)
            .where(frames.sources.notna(), None)
            .to_dict("records")
        )
        verdict_counts = {
            "matched": len(frames.jobs),
            "strict_matches": len(frames.strict_matches),
            "unverifiable": len(frames.unverifiable_candidates),
            "no_match": len(frames.no_matches),
            "conflict": len(frames.conflicts),
        }
        return {
            **frames.as_records(),
            "facets": facets,
            "run_manifest": build_run_manifest(
                "v1/job-search",
                request.model_dump(exclude={"payloads"}),
                facets,
                sources,
                verdict_counts,
            ),
        }
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.post("/v1/current-jobs")
def current_jobs(request: CurrentJobRequest) -> dict[str, Any]:
    try:
        result = execute_current_job_search(
            request.payloads,
            request.to_domain(),
            snapshot_id=request.snapshot_id,
            active_as_of=request.active_as_of,
        )
        payload = result.as_dict()
        payload["run_manifest"] = build_run_manifest(
            "v1/current-jobs",
            request.model_dump(exclude={"payloads"}),
            [],
            payload["tables"].get("sources", []),
            {
                key: value
                for key, value in payload["denominators"].items()
                if isinstance(value, int)
            },
            selection={
                "purpose": "current_jobs",
                "mode": "current_job",
                "snapshot_id": request.snapshot_id,
            },
            snapshot_ref={
                "snapshot_id": request.snapshot_id,
                "collected_at": request.active_as_of,
                "status": "selected",
            },
            result_refs=result_refs(payload["tables"]),
        )
        return payload
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.post("/v1/job-trends")
def job_trends(request: JobTrendRequest) -> dict[str, Any]:
    result = evaluate_job_trends(request.snapshots)
    result["metric"] = request.metric
    result["event_boundary"] = {
        "status": "association-only"
        if result.get("status") == "eligible"
        else "unavailable",
        "has_control": request.has_control,
    }
    return result


@app.get("/v1/jobs/{provider}/{job_id}/requirements")
def job_requirements(provider: str, job_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    try:
        rows = Warehouse(settings).query(
            "SELECT text,requirement_status,evidence_scope,source_url,observed_at FROM job_requirement WHERE provider=? AND job_id=? ORDER BY requirement_id",
            [provider, job_id],
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {
        "provider": provider,
        "job_id": job_id,
        "availability": "available" if rows else "requirement_unavailable",
        "requirements": rows,
    }
