from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analysis_service import build_company_timeline, evaluate_ai_event, evaluate_job_trends, evaluate_valuation_scenarios
from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    event_study_prerequisites,
    future_value_score,
    rank_companies,
    valuation_prerequisites,
)
from .config import Settings
from .exporting import build_export_bundle
from .facets import build_job_facets
from .job_search import JobSearchProfile, normalize_provider_payloads, search_job_dataframes
from .current_jobs import execute_current_job_search
from .query_contract import company_search_profile_from_mapping
from .run_manifest import build_run_manifest, result_refs
from .selection_provenance import bind_selection_run, verify_run_chain
from .screening import ScreenerProfile, screen_companies
from .search import explain_company_evaluation, rank_candidate_evaluations, rank_candidates, validate_search_profile
from .warehouse import Warehouse

app = FastAPI(title="Company Intelligence API", version="0.1.0")


class RankingRequest(BaseModel):
    rows: list[dict[str, Any]]
    weights: dict[str, float]
    directions: dict[str, bool] = Field(default_factory=dict)


class EventStudyRequest(BaseModel):
    asset_returns: list[float]
    benchmark_returns: list[float]
    event_index: int
    windows: list[int] = [1, 5, 20]


class DidRequest(BaseModel):
    treated_pre: list[float]
    treated_post: list[float]
    control_pre: list[float]
    control_post: list[float]


class DcfRequest(BaseModel):
    revenue: float
    net_debt: float
    shares: float
    years: int = 5


class FutureScoreRequest(BaseModel):
    components: dict[str, float | None]
    confidence: dict[str, float] = Field(default_factory=dict)


class SearchProfileRequest(BaseModel):
    countries: list[str]
    job_keywords: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    employment_types: list[str] = Field(default_factory=list)
    country_allocation: dict[str, int] = Field(default_factory=dict)
    ownership_sectors: list[str] = Field(default_factory=list)
    legal_forms: list[str] = Field(default_factory=list)
    business_activities: list[str] = Field(default_factory=list)
    market_statuses: list[str] = Field(default_factory=list)
    public_institution_types: list[str] = Field(default_factory=list)
    entity_categories: list[str] = Field(default_factory=list)
    source_operations: list[str] = Field(default_factory=list)
    providers: list[str] = Field(default_factory=list)
    semantic_filters: dict[str, list[str]] = Field(default_factory=dict)
    field_filters: list[dict[str, Any]] = Field(default_factory=list)
    require_resolved_identity: bool = True
    unknown_policy: str = "report"

    def to_domain(self):
        """Use the same namespaced semantic contract as ``company-search``."""

        return company_search_profile_from_mapping(self.model_dump())


class ExportRequest(BaseModel):
    entity_ids: list[str] = Field(default_factory=list)
    include_xlsx: bool = True


class JobSearchRequest(BaseModel):
    payloads: dict[str, Any]
    countries: list[str]
    job_keywords: list[str] = Field(default_factory=list)
    occupations: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    workplace_types: list[str] = Field(default_factory=list)
    employment_types: list[str] = Field(default_factory=list)
    # Legacy ``languages`` means a posting display language.  It is distinct
    # from ``required_languages``, which means a candidate requirement.
    languages: list[str] = Field(default_factory=list)
    posting_languages: list[str] = Field(default_factory=list)
    business_units: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    company_types: list[str] = Field(default_factory=list)
    minimum_salary_floor: float | None = None
    maximum_salary_ceiling: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_basis: str | None = None
    required_requirement_terms: list[str] = Field(default_factory=list)
    preferred_requirement_terms: list[str] = Field(default_factory=list)
    required_languages: list[str] = Field(default_factory=list)
    identity_link_statuses: list[str] = Field(default_factory=list)
    public_contexts: list[str] = Field(default_factory=list)
    public_institution_types: list[str] = Field(default_factory=list)
    legal_forms: list[str] = Field(default_factory=list)
    ownership_sectors: list[str] = Field(default_factory=list)
    active_only: bool = True
    country_allocation: dict[str, int] = Field(default_factory=dict)
    unknown_policy: str = "exclude"
    keyword_scope: str = "title_or_occupation"

    def to_domain(self) -> JobSearchProfile:
        values = self.model_dump(exclude={"payloads"})
        for key in (
            "countries", "job_keywords", "occupations", "locations", "workplace_types",
            "employment_types", "languages", "posting_languages", "business_units", "industries", "company_types",
            "required_requirement_terms", "preferred_requirement_terms", "required_languages",
            "identity_link_statuses", "public_contexts", "public_institution_types", "legal_forms", "ownership_sectors",
        ):
            values[key] = tuple(values[key])
        return JobSearchProfile(**values)


class CurrentJobRequest(JobSearchRequest):
    snapshot_id: str | None = None
    active_as_of: str | None = None


class JobTrendRequest(BaseModel):
    snapshots: list[dict[str, Any]]
    metric: str = "active_postings"
    has_control: bool = False


class SelectionRunRequest(BaseModel):
    selection: dict[str, Any]
    snapshot: dict[str, Any]
    results: dict[str, Any]


class SelectionRunResponse(BaseModel):
    run_id: str
    manifest: dict[str, Any]


class ScreenerRequest(BaseModel):
    rows: list[dict[str, Any]]
    countries: list[str]
    industries: list[str]
    size_buckets: list[str]
    metrics: dict[str, float]
    directions: dict[str, bool] = Field(default_factory=dict)
    as_of: str | None = None
    minimum_peer_size: int = 2
    comparability_group: str | None = None
    require_complete_signature: bool = True


class EvidenceTimelineRequest(BaseModel):
    entity_id: str
    as_of: str
    rows: list[dict[str, Any]]


class ValuationEvidenceRequest(BaseModel):
    revenue: float | None = None
    net_debt: float | None = None
    shares: float | None = None
    years: int = 5
    evidence: dict[str, str | None] = Field(default_factory=dict)


class AiEventEvidenceRequest(BaseModel):
    asset_returns: list[float]
    benchmark_returns: list[float]
    event_index: int
    event_evidence: dict[str, str | None]
    treated_pre: list[float] | None = None
    treated_post: list[float] | None = None
    control_pre: list[float] | None = None
    control_post: list[float] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/validation/latest")
def latest_validation() -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    path = settings.artifact_dir / "validation_results.json"
    if not path.exists():
        raise HTTPException(404, "Run company-intel validate first")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/rankings")
def rankings(request: RankingRequest) -> list[dict[str, Any]]:
    return rank_companies(request.rows, request.weights, request.directions)


@app.post("/analysis/event-study")
def calculate_event_study(request: EventStudyRequest) -> dict[str, Any]:
    return event_study(
        request.asset_returns, request.benchmark_returns, request.event_index, tuple(request.windows)
    )


@app.post("/analysis/did")
def calculate_did(request: DidRequest) -> dict[str, Any]:
    return difference_in_differences(
        request.treated_pre, request.treated_post, request.control_pre, request.control_post
    )


@app.post("/analysis/dcf")
def calculate_dcf(request: DcfRequest) -> dict[str, Any]:
    return dcf_scenarios(request.revenue, request.net_debt, request.shares, years=request.years)


@app.post("/analysis/future-score")
def calculate_future_score(request: FutureScoreRequest) -> dict[str, Any]:
    return future_value_score(request.components, request.confidence)


@app.get("/company/{entity_id}/timeline")
def company_timeline(entity_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    warehouse = Warehouse(settings)
    try:
        financials = warehouse.query(
            "SELECT * FROM financial_fact WHERE entity_id=? ORDER BY available_at, period_end", [entity_id]
        )
        workforce = warehouse.query(
            "SELECT * FROM workforce_fact WHERE entity_id=? ORDER BY available_at, period_end", [entity_id]
        )
        events = warehouse.query(
            "SELECT * FROM company_event WHERE entity_id=? ORDER BY available_at, event_date", [entity_id]
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {"entity_id": entity_id, "financials": financials, "workforce": workforce, "events": events}


@app.get("/v1/companies/{entity_id}/capabilities")
def company_capabilities(entity_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    warehouse = Warehouse(settings)
    try:
        capabilities = warehouse.query("SELECT operation_id,capability,status,source_url,available_at FROM company_source_capability WHERE entity_id=? ORDER BY operation_id,capability", [entity_id])
        fields = warehouse.query("SELECT operation_id,field_name,status,observation_date,available_at FROM field_availability WHERE entity_id=? ORDER BY operation_id,field_name", [entity_id])
        exclusions = warehouse.query("SELECT reasons_json,classified_at FROM classification_history WHERE entity_id=? ORDER BY classified_at DESC LIMIT 1", [entity_id])
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {"entity_id": entity_id, "capabilities": capabilities, "field_availability": fields, "analysis_exclusion": exclusions[0] if exclusions else None}


@app.post("/v1/company-search")
def company_search(request: SearchProfileRequest) -> dict[str, Any]:
    profile = validate_search_profile(request.to_domain())
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


@app.post("/v1/job-search")
def job_search(request: JobSearchRequest) -> dict[str, Any]:
    try:
        profile = request.to_domain()
        frames = search_job_dataframes(request.payloads, profile)
        all_jobs, _requirements, _sources = normalize_provider_payloads(request.payloads)
        facets = build_job_facets(all_jobs)
        sources = frames.sources.astype(object).where(frames.sources.notna(), None).to_dict("records")
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
            request.payloads, request.to_domain(), snapshot_id=request.snapshot_id, active_as_of=request.active_as_of,
        )
        payload = result.as_dict()
        payload["run_manifest"] = build_run_manifest(
            "v1/current-jobs", request.model_dump(exclude={"payloads"}), [], payload["tables"].get("sources", []),
            {key: value for key, value in payload["denominators"].items() if isinstance(value, int)},
            selection={"purpose": "current_jobs", "mode": "current_job", "snapshot_id": request.snapshot_id},
            snapshot_ref={"snapshot_id": request.snapshot_id, "collected_at": request.active_as_of, "status": "selected"},
            result_refs=result_refs(payload["tables"]),
        )
        return payload
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.post("/v1/job-trends")
def job_trends(request: JobTrendRequest) -> dict[str, Any]:
    result = evaluate_job_trends(request.snapshots)
    result["metric"] = request.metric
    result["event_boundary"] = {"status": "association-only" if result.get("status") == "eligible" else "unavailable", "has_control": request.has_control}
    return result


@app.post("/v1/selection-runs", response_model=SelectionRunResponse)
def selection_run(request: SelectionRunRequest) -> SelectionRunResponse:
    manifest = bind_selection_run(request.selection, request.snapshot, request.results)
    return SelectionRunResponse(run_id=manifest.run_id, manifest=manifest.as_dict())


@app.post("/v1/selection-runs/replay")
def replay_run(request: SelectionRunRequest) -> dict[str, Any]:
    manifest = bind_selection_run(request.selection, request.snapshot, request.results).as_dict()
    if not verify_run_chain(manifest):
        raise HTTPException(422, "selection_manifest_tampered")
    # The endpoint verifies the immutable request chain only.  A caller must
    # separately submit a saved snapshot to execute a search again.
    return {"status": "replay_ready", "run_id": manifest["run_id"], "snapshot_ref": manifest["snapshot_ref"]}


@app.post("/v1/company-screener")
def company_screener(request: ScreenerRequest) -> dict[str, Any]:
    result = screen_companies(
        request.rows,
        ScreenerProfile(
            tuple(request.countries), tuple(request.industries), tuple(request.size_buckets),
            request.metrics, request.directions, request.as_of, request.minimum_peer_size,
            request.comparability_group, request.require_complete_signature,
        ),
    )
    return {
        "rankings": result.rankings.astype(object).where(result.rankings.notna(), None).to_dict("records"),
        "exclusions": result.exclusions.astype(object).where(result.exclusions.notna(), None).to_dict("records"),
        "metadata": result.metadata,
    }


@app.post("/v1/company-timeline")
def evidence_timeline(request: EvidenceTimelineRequest) -> dict[str, Any]:
    result = build_company_timeline(request.rows, entity_id=request.entity_id, as_of=request.as_of)
    return {
        "timeline": result["timeline"].astype(object).where(result["timeline"].notna(), None).to_dict("records"),
        "exclusions": result["exclusions"].astype(object).where(result["exclusions"].notna(), None).to_dict("records"),
        "metadata": result["metadata"],
    }


@app.post("/v1/analysis/valuation-scenarios")
def valuation_scenarios(request: ValuationEvidenceRequest) -> dict[str, Any]:
    prerequisites = valuation_prerequisites(
        request.revenue, request.net_debt, request.shares, request.evidence
    )
    if prerequisites["status"] != "ready":
        return {"status": prerequisites["status"], "prerequisites": prerequisites}
    result = evaluate_valuation_scenarios(
        revenue=request.revenue, net_debt=request.net_debt, shares=request.shares,
        evidence=request.evidence, years=request.years,
    )
    return {**result, "prerequisites": prerequisites}


@app.post("/v1/analysis/ai-event")
def ai_event_analysis(request: AiEventEvidenceRequest) -> dict[str, Any]:
    value = request.model_dump()
    prerequisites = event_study_prerequisites(
        value["asset_returns"], value["benchmark_returns"], value["event_index"], value["event_evidence"],
        value.get("treated_pre"), value.get("treated_post"), value.get("control_pre"), value.get("control_post"),
    )
    if prerequisites["status"] != "association-only":
        return {"status": prerequisites["status"], "prerequisites": prerequisites}
    return {**evaluate_ai_event(**value), "prerequisites": prerequisites}


@app.get("/v1/jobs/{provider}/{job_id}/requirements")
def job_requirements(provider: str, job_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    try:
        rows = Warehouse(settings).query("SELECT text,requirement_status,evidence_scope,source_url,observed_at FROM job_requirement WHERE provider=? AND job_id=? ORDER BY requirement_id", [provider, job_id])
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {"provider": provider, "job_id": job_id, "availability": "available" if rows else "requirement_unavailable", "requirements": rows}


@app.post("/v1/exports")
def create_export(request: ExportRequest) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    run_id = f"export-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    output = settings.artifact_dir / "exports" / run_id
    try:
        data = Warehouse(settings).materialize_export_snapshot(request.entity_ids or None)
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
    return {"run_id": run_id, "status": "completed", "output_directory": str(output), "manifest": bundle.manifest}


@app.get("/v1/exports/{run_id}")
def export_metadata(run_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    path = settings.artifact_dir / "exports" / run_id / "manifest.json"
    if not path.is_file():
        raise HTTPException(404, "export run not found")
    return {"run_id": run_id, "status": "completed", "manifest": json.loads(path.read_text(encoding="utf-8"))}
