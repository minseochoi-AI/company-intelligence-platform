"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_application.jobs.search import search_job_dataframes
from cil_contracts.jobs import JobSearchProfile
from cil_contracts.query import company_search_profile_from_mapping
from cil_integrations.providers.job_records import normalize_provider_payloads
from pydantic import BaseModel, Field
from typing import Any


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
    isco_codes: list[str] = Field(default_factory=list)
    ncs_codes: list[str] = Field(default_factory=list)
    active_only: bool = True
    country_allocation: dict[str, int] = Field(default_factory=dict)
    unknown_policy: str = "exclude"
    keyword_scope: str = "title_or_occupation"

    def to_domain(self) -> JobSearchProfile:
        values = self.model_dump(include=set(JobSearchProfile.__dataclass_fields__))
        for key in (
            "countries",
            "job_keywords",
            "occupations",
            "locations",
            "workplace_types",
            "employment_types",
            "languages",
            "posting_languages",
            "business_units",
            "industries",
            "company_types",
            "required_requirement_terms",
            "preferred_requirement_terms",
            "required_languages",
            "identity_link_statuses",
            "public_contexts",
            "public_institution_types",
            "legal_forms",
            "ownership_sectors",
            "isco_codes",
            "ncs_codes",
        ):
            values[key] = tuple(values.get(key, ()))
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
