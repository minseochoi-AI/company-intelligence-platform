"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_api.schemas import ScreenerRequest
from cil_api.schemas import SearchProfileRequest
from cil_domain.companies.screening import ScreenerProfile
from cil_domain.companies.screening import screen_companies
from cil_domain.companies.search import explain_company_evaluation
from cil_domain.companies.search import rank_candidate_evaluations
from cil_domain.companies.search import rank_candidates
from cil_domain.companies.search import validate_search_profile
from cil_integrations.runtime.settings import Settings
from cil_integrations.storage.duckdb.repository import Warehouse
from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Any


@app.get("/company/{entity_id}/timeline")
def company_timeline(entity_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    warehouse = Warehouse(settings)
    try:
        financials = warehouse.query(
            "SELECT * FROM financial_fact WHERE entity_id=? ORDER BY available_at, period_end",
            [entity_id],
        )
        workforce = warehouse.query(
            "SELECT * FROM workforce_fact WHERE entity_id=? ORDER BY available_at, period_end",
            [entity_id],
        )
        events = warehouse.query(
            "SELECT * FROM company_event WHERE entity_id=? ORDER BY available_at, event_date",
            [entity_id],
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {
        "entity_id": entity_id,
        "financials": financials,
        "workforce": workforce,
        "events": events,
    }


@app.get("/v1/companies/{entity_id}/capabilities")
def company_capabilities(entity_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    warehouse = Warehouse(settings)
    try:
        capabilities = warehouse.query(
            "SELECT operation_id,capability,status,source_url,available_at FROM company_source_capability WHERE entity_id=? ORDER BY operation_id,capability",
            [entity_id],
        )
        fields = warehouse.query(
            "SELECT operation_id,field_name,status,observation_date,available_at FROM field_availability WHERE entity_id=? ORDER BY operation_id,field_name",
            [entity_id],
        )
        exclusions = warehouse.query(
            "SELECT reasons_json,classified_at FROM classification_history WHERE entity_id=? ORDER BY classified_at DESC LIMIT 1",
            [entity_id],
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {
        "entity_id": entity_id,
        "capabilities": capabilities,
        "field_availability": fields,
        "analysis_exclusion": exclusions[0] if exclusions else None,
    }


@app.post("/v1/company-search")
def company_search(request: SearchProfileRequest) -> dict[str, Any]:
    try:
        profile = validate_search_profile(request.to_domain())
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    settings = Settings.from_env(Path.cwd())
    try:
        candidates = Warehouse(settings).search_candidates(profile.countries)
        evaluations = rank_candidate_evaluations(profile, candidates)
        matches = rank_candidates(profile, candidates)
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    verdict_counts: dict[str, int] = {}
    for evaluation in evaluations:
        verdict_counts[evaluation.status] = verdict_counts.get(evaluation.status, 0) + 1
    return {
        "profile": request.model_dump(),
        "candidates": [item.__dict__ for item in matches],
        "evaluations": [explain_company_evaluation(item) for item in evaluations],
        "verdict_counts": dict(sorted(verdict_counts.items())),
    }


@app.post("/v1/company-screener")
def company_screener(request: ScreenerRequest) -> dict[str, Any]:
    result = screen_companies(
        request.rows,
        ScreenerProfile(
            tuple(request.countries),
            tuple(request.industries),
            tuple(request.size_buckets),
            request.metrics,
            request.directions,
            request.as_of,
            request.minimum_peer_size,
            request.comparability_group,
            request.require_complete_signature,
        ),
    )
    return {
        "rankings": result.rankings.astype(object)
        .where(result.rankings.notna(), None)
        .to_dict("records"),
        "exclusions": result.exclusions.astype(object)
        .where(result.exclusions.notna(), None)
        .to_dict("records"),
        "metadata": result.metadata,
    }
