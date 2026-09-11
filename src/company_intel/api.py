from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analysis_service import build_company_timeline, evaluate_ai_event, evaluate_valuation_scenarios
from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    future_value_score,
    rank_companies,
)
from .config import Settings
from .exporting import build_export_bundle
from .job_search import JobSearchProfile, search_job_dataframes
from .models import SearchProfile
from .screening import ScreenerProfile, screen_companies
from .search import rank_candidates, validate_search_profile
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
    job_keywords: list[str]
    industries: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    employment_types: list[str] = Field(default_factory=list)
    country_allocation: dict[str, int] = Field(default_factory=dict)

    def to_domain(self) -> SearchProfile:
        return SearchProfile(
            countries=tuple(self.countries), job_keywords=tuple(self.job_keywords), industries=tuple(self.industries),
            required_capabilities=tuple(self.required_capabilities), languages=tuple(self.languages),
            employment_types=tuple(self.employment_types), country_allocation=self.country_allocation,
        )


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
    languages: list[str] = Field(default_factory=list)
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
    active_only: bool = True
    country_allocation: dict[str, int] = Field(default_factory=dict)
    unknown_policy: str = "exclude"
    keyword_scope: str = "title_or_occupation"

    def to_domain(self) -> JobSearchProfile:
        values = self.model_dump(exclude={"payloads"})
        for key in (
            "countries", "job_keywords", "occupations", "locations", "workplace_types",
            "employment_types", "languages", "industries", "company_types",
            "required_requirement_terms", "preferred_requirement_terms", "required_languages",
        ):
            values[key] = tuple(values[key])
        return JobSearchProfile(**values)


class ScreenerRequest(BaseModel):
    rows: list[dict[str, Any]]
    countries: list[str]
    industries: list[str]
    size_buckets: list[str]
    metrics: dict[str, float]
    directions: dict[str, bool] = Field(default_factory=dict)
    as_of: str | None = None
    minimum_peer_size: int = 2


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
        matches = rank_candidates(profile, Warehouse(settings).search_candidates(profile.countries))
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {"profile": request.model_dump(), "candidates": [item.__dict__ for item in matches]}


@app.post("/v1/job-search")
def job_search(request: JobSearchRequest) -> dict[str, Any]:
    try:
        return search_job_dataframes(request.payloads, request.to_domain()).as_records()
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@app.post("/v1/company-screener")
def company_screener(request: ScreenerRequest) -> dict[str, Any]:
    result = screen_companies(
        request.rows,
        ScreenerProfile(
            tuple(request.countries), tuple(request.industries), tuple(request.size_buckets),
            request.metrics, request.directions, request.as_of, request.minimum_peer_size,
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
    return evaluate_valuation_scenarios(
        revenue=request.revenue, net_debt=request.net_debt, shares=request.shares,
        evidence=request.evidence, years=request.years,
    )


@app.post("/v1/analysis/ai-event")
def ai_event_analysis(request: AiEventEvidenceRequest) -> dict[str, Any]:
    return evaluate_ai_event(**request.model_dump())


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
        bundle = build_export_bundle(output, include_xlsx=request.include_xlsx, allowed_root=settings.artifact_dir, **data)
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
