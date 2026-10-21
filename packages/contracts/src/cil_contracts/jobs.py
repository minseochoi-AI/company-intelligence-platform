"""Canonical responsibility owner; migrated from src/company_intel/classification.py, src/company_intel/current_jobs.py, src/company_intel/job_search.py."""

from __future__ import annotations
from typing import Protocol


class ClusterKey(Protocol):
    @property
    def key(self) -> str: ...


from dataclasses import asdict, dataclass
from dataclasses import dataclass, field
from typing import Any
from typing import Any, Mapping
from copy import deepcopy


@dataclass(frozen=True)
class CanonicalJobRecord:
    """Canonical cross-national job vacancy record with 5-level ClusterSignature."""

    job_id: str
    job_url: str
    employer_name: str
    org_id: str
    job_title: str
    occupation_code: str
    education_level: str
    contract_type: str
    salary_min: Any
    salary_max: Any
    currency: str
    location: str
    deadline: str
    description: str
    source_api: str
    cluster_signature: ClusterKey
    legal_form: str = ""
    entity_type: str = ""
    hours_or_headcount: str = ""
    raw_attributes: dict[str, Any] = field(default_factory=dict)
    normalized_attributes: dict[str, Any] = field(default_factory=dict)
    salary_period: str | None = None
    requirement_text: str | None = None
    preferred_text: str | None = None
    source_kind: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            **{
                key: deepcopy(value)
                for key, value in self.__dict__.items()
                if key != "cluster_signature"
            },
            "cluster_key": self.cluster_signature.key,
        }


@dataclass(frozen=True)
class SearchDenominators:
    provider_returned: int
    normalized: int
    active: int
    strict_match: int
    unverifiable: int
    no_match: int
    conflict: int
    active_as_of: str


@dataclass(frozen=True)
class CurrentJobResult:
    snapshot_id: str | None
    denominators: SearchDenominators
    tables: dict[str, list[dict[str, Any]]]
    coverage: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "denominators": asdict(self.denominators),
            "tables": self.tables,
            "coverage": self.coverage,
        }


@dataclass(frozen=True)
class JobSearchProfile:
    countries: tuple[str, ...]
    job_keywords: tuple[str, ...]
    occupations: tuple[str, ...] = ()
    isco_codes: tuple[str, ...] = ()
    ncs_codes: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    workplace_types: tuple[str, ...] = ()
    employment_types: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    posting_languages: tuple[str, ...] = ()
    business_units: tuple[str, ...] = ()
    industries: tuple[str, ...] = ()
    company_types: tuple[str, ...] = ()
    minimum_salary_floor: float | None = None
    maximum_salary_ceiling: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_basis: str | None = None
    required_requirement_terms: tuple[str, ...] = ()
    preferred_requirement_terms: tuple[str, ...] = ()
    required_languages: tuple[str, ...] = ()
    identity_link_statuses: tuple[str, ...] = ()
    public_contexts: tuple[str, ...] = ()
    public_institution_types: tuple[str, ...] = ()
    legal_forms: tuple[str, ...] = ()
    ownership_sectors: tuple[str, ...] = ()
    active_only: bool = True
    country_allocation: dict[str, int] = field(default_factory=dict)
    unknown_policy: str = "exclude"
    keyword_scope: str = "title_or_occupation"
