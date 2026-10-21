"""Canonical responsibility owner; migrated from src/company_intel/classification.py, src/company_intel/exporting.py."""

from __future__ import annotations
from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DynamicColumnSpec:
    """Specification of an Excel column in a dynamically compiled report."""

    index: int
    header: str
    field_key: str
    column_letter: str
    alignment: str = "left"
    is_hyperlink: bool = False
    is_freshness: bool = False
    formula_template: str = ""


JOB_EXPORT_HEADERS = (
    "provider",
    "job_id",
    "company_id",
    "entity_id",
    "company_name",
    "company_type",
    "industry_raw",
    "business_unit",
    "institution_type_code",
    "institution_type_raw",
    "title",
    "title_raw",
    "occupation_label",
    "occupation_code",
    "occupation_system",
    "country_code",
    "location_raw",
    "city",
    "region",
    "workplace_type",
    "employment_type",
    "employment_type_raw",
    "posting_language",
    "salary_min",
    "salary_max",
    "salary_currency",
    "salary_period",
    "salary_period_raw",
    "salary_basis",
    "posted_at",
    "updated_at",
    "closing_at",
    "snapshot_at",
    "snapshot_date",
    "is_active",
    "source_url",
    "normalization_notes",
)

VERDICT_EXPORT_HEADERS = (
    "subject_type",
    "subject_id",
    "provider",
    "job_id",
    "company_id",
    "entity_id",
    "company_name",
    "field",
    "verdict",
    "reason",
    "expected_value",
    "observed_value",
    "left_value",
    "right_value",
    "source_url",
)

TABLE_HEADERS = {
    "companies": ("company_id", "legal_name", "country_code", "industry_code"),
    "capabilities": (
        "company_id",
        "operation_id",
        "capability",
        "status",
        "source_url",
        "available_at",
    ),
    "jobs": JOB_EXPORT_HEADERS,
    "locations": (
        "provider",
        "job_id",
        "company_name",
        "location_raw",
        "country_code",
        "city",
        "region",
        "location_role",
        "source_field",
    ),
    "requirements": (
        "provider",
        "job_id",
        "company_name",
        "requirement_id",
        "requirement_kind",
        "normalized_key",
        "label",
        "necessity",
        "value",
        "proficiency",
        "text",
        "requirement_status",
        "evidence_scope",
        "source_url",
        "observed_at",
        "confidence",
    ),
    "sources": (
        "source_id",
        "provider",
        "operation_id",
        "snapshot_at",
        "record_count",
        "coverage",
        "limitations",
        "source_url",
    ),
    "exclusions": (
        "company_id",
        "provider",
        "job_id",
        "company_name",
        "field",
        "reason",
        "observed_value",
    ),
    "strict_matches": JOB_EXPORT_HEADERS + ("preference_hits",),
    "no_matches": VERDICT_EXPORT_HEADERS,
    "unverifiable": VERDICT_EXPORT_HEADERS,
    "unverifiable_candidates": VERDICT_EXPORT_HEADERS,
    "conflicts": VERDICT_EXPORT_HEADERS,
    "facets": (
        "semantic_field",
        "scope",
        "normalized_value",
        "display_label",
        "vocabulary_namespace",
        "provider",
        "raw_field",
        "record_count",
        "coverage_ratio",
        "filterability",
        "sortability",
        "comparability_requirements",
        "evidence_status",
    ),
    "run_manifest": (
        "run_id",
        "schema_version",
        "command",
        "generated_at",
        "profile_sha256",
        "facet_snapshot_sha256",
        "source_snapshot_sha256",
        "facet_count",
        "source_count",
        "verdict_counts",
        "output_manifest_sha256",
    ),
    "denominators": (
        "provider_returned",
        "normalized",
        "active",
        "strict_match",
        "unverifiable",
        "no_match",
        "conflict",
        "active_as_of",
    ),
    "trend_eligibility": ("eligible", "reason", "snapshot_count", "series_signature"),
    "selection_run": ("run_id", "snapshot_id", "manifest_sha256"),
    "career_overlap": (
        "requirement_kind",
        "normalized_key",
        "label",
        "required_count",
        "preferred_count",
        "posting_count",
        "company_count",
        "country_count",
        "prevalence",
    ),
}


@dataclass(frozen=True)
class ExportBundle:
    files: dict[str, bytes]
    manifest: dict[str, Any]
