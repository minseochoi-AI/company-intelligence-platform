from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Normalizer = Callable[[bytes, str], dict[str, Any]]


@dataclass
class Probe:
    id: str
    provider: str
    category: str
    regions: list[str]
    method: str
    url: str
    params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    form_body: dict[str, Any] | None = None
    expected_format: str = "json"
    required_paths: list[str] = field(default_factory=list)
    secret_env: str | None = None
    normalizer: Normalizer | None = None
    capabilities: list[str] = field(default_factory=list)
    quota_note: str | None = None
    limitation: str | None = None


@dataclass
class HttpResult:
    status_code: int | None
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float
    attempts: int
    error: str | None = None


@dataclass(frozen=True)
class AtomicFieldContract:
    source_field: str
    internal_field: str
    meaning: str


@dataclass(frozen=True)
class SourcePolicy:
    operation_id: str
    provider: str
    regions: tuple[str, ...]
    access_mode: str
    data_role: str
    required_paths: tuple[str, ...]
    field_contracts: tuple[AtomicFieldContract, ...]
    activation_policy: str
    secret_env: str | None
    quota: str
    license: str
    last_verified: str
    semantic_contract: tuple[str, ...] = ()
    provider_disposition: str = "production"


@dataclass(frozen=True)
class ProviderHealth:
    operation_id: str
    status: str
    detail: str


@dataclass(frozen=True)
class AnalysisEligibility:
    correlation_ready: bool
    causal_ready: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class CompanyClassification:
    entity_id: str
    capabilities: dict[str, str]
    analysis_eligibility: AnalysisEligibility
    classification_reasons: tuple[str, ...]


@dataclass(frozen=True)
class AtomicFact:
    """One source fact without silently converting its measurement meaning."""

    entity_id: str | None
    operation_id: str
    fact_key: str
    value: Any
    unit: str | None
    currency: str | None
    period: str | None
    concept: str | None
    available_at: str | None
    source_url: str | None
    raw_record_id: str | None


@dataclass(frozen=True)
class ComparabilitySignature:
    country_code: str | None
    industry: str | None
    size_bucket: str | None
    currency: str | None
    period: str | None
    unit: str | None
    concept: str | None
    vintage: str | None
    coverage: str | None

    def key(self) -> tuple[str | None, ...]:
        return (self.country_code, self.industry, self.size_bucket, self.currency, self.period, self.unit, self.concept, self.vintage, self.coverage)


@dataclass(frozen=True)
class SourceDisposition:
    operation_id: str
    disposition: str
    reason: str


@dataclass(frozen=True)
class SearchProfile:
    countries: tuple[str, ...]
    job_keywords: tuple[str, ...]
    industries: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    employment_types: tuple[str, ...] = ()
    country_allocation: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class CandidateMatch:
    entity_id: str
    name: str
    country_code: str | None
    status: str
    score: int
    matched_capabilities: tuple[str, ...]
    exclusion_reason: str | None = None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementEvidence:
    text: str
    status: str
    evidence_scope: str
    source_url: str | None
    verification_status: str


@dataclass(frozen=True)
class RequirementVerification:
    availability: str
    requirements: tuple[RequirementEvidence, ...]
    reason: str | None = None
