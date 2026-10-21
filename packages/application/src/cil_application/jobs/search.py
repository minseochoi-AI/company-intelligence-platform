"""Canonical responsibility owner; migrated from src/company_intel/job_search.py."""

from __future__ import annotations
from cil_contracts.jobs import JobSearchProfile
from cil_contracts.query import FilterVerdict
from cil_contracts.query import UnknownPolicy
from cil_contracts.query import text_verdict
from cil_domain.jobs.filters import _contains_verdict
from cil_domain.jobs.filters import _language_verdict
from cil_domain.jobs.filters import _membership_verdict
from cil_domain.jobs.filters import _reason_for
from cil_domain.jobs.filters import _requirement_matches
from cil_domain.jobs.filters import _requirement_verdict
from cil_domain.jobs.filters import _salary_signature_verdict
from cil_domain.jobs.filters import _validate_profile
from cil_domain.taxonomy.facts import resolve_title_to_isco
from cil_application.ports import normalize_greenhouse_jobs
from cil_application.ports import normalize_lever_jobs
from cil_application.ports import normalize_mpm_jobs
from cil_application.ports import normalize_mpsv_jobs
from cil_application.ports import normalize_provider_payloads
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import pandas as pd

JOB_COLUMNS = (
    "provider",
    "job_id",
    "entity_id",
    "company_name",
    "company_type",
    "industry_raw",
    "business_unit",
    "institution_type_code",
    "institution_type_raw",
    "identity_link_status",
    "public_context",
    "public_institution_type",
    "legal_form",
    "ownership_sector",
    "title_raw",
    "occupation_label",
    "occupation_code",
    "occupation_system",
    "occupation_pivot",
    "ncs_code",
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
    "is_active",
    "source_url",
    "normalization_notes",
)

REQUIREMENT_COLUMNS = (
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
    "evidence_scope",
    "source_url",
    "confidence",
)

EXCLUSION_COLUMNS = (
    "provider",
    "job_id",
    "company_name",
    "field",
    "reason",
    "observed_value",
)

SOURCE_COLUMNS = (
    "provider",
    "snapshot_at",
    "record_count",
    "source_url",
    "coverage",
    "limitations",
)

OVERLAP_COLUMNS = (
    "requirement_kind",
    "normalized_key",
    "label",
    "required_count",
    "preferred_count",
    "posting_count",
    "company_count",
    "country_count",
    "prevalence",
)

LOCATION_COLUMNS = (
    "provider",
    "job_id",
    "company_name",
    "location_raw",
    "country_code",
    "city",
    "region",
    "location_role",
    "source_field",
)

VERDICT_COLUMNS = (
    "provider",
    "job_id",
    "company_name",
    "field",
    "verdict",
    "reason",
    "observed_value",
)


@dataclass(frozen=True)
class JobDataFrames:
    companies: pd.DataFrame
    jobs: pd.DataFrame
    requirements: pd.DataFrame
    career_overlap: pd.DataFrame
    exclusions: pd.DataFrame
    sources: pd.DataFrame
    strict_matches: pd.DataFrame
    unverifiable_candidates: pd.DataFrame
    no_matches: pd.DataFrame
    conflicts: pd.DataFrame
    locations: pd.DataFrame
    metadata: dict[str, Any]

    def as_records(self) -> dict[str, Any]:
        tables = {
            "companies": self.companies,
            "jobs": self.jobs,
            "requirements": self.requirements,
            "career_overlap": self.career_overlap,
            "exclusions": self.exclusions,
            "sources": self.sources,
            "strict_matches": self.strict_matches,
            "unverifiable_candidates": self.unverifiable_candidates,
            "no_matches": self.no_matches,
            "conflicts": self.conflicts,
            "locations": self.locations,
        }
        return {
            "tables": {
                name: {
                    "columns": list(frame.columns),
                    "rows": frame.astype(object)
                    .where(frame.notna(), None)
                    .to_dict("records"),
                }
                for name, frame in tables.items()
            },
            "metadata": self.metadata,
        }

    def write_csv(self, destination: Path) -> list[Path]:
        from cil_application.ports import write_csv_tables

        return write_csv_tables(destination, self.as_records()["tables"])


SKILLS = {
    "python",
    "sql",
    "kotlin",
    "swift",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "aws",
    "azure",
    "gcp",
    "excel",
    "tableau",
    "power bi",
    "docker",
    "kubernetes",
    "linux",
    "machine learning",
    "data engineering",
    "project management",
    "salesforce",
    "sap",
}

LANGUAGES = {
    "english",
    "korean",
    "czech",
    "german",
    "french",
    "spanish",
    "japanese",
    "mandarin",
}

NORMALIZERS = {
    "greenhouse": normalize_greenhouse_jobs,
    "lever": normalize_lever_jobs,
    "mpm": normalize_mpm_jobs,
    "mpm_public_employment": normalize_mpm_jobs,
    "mpsv": normalize_mpsv_jobs,
    "mpsv_cz": normalize_mpsv_jobs,
}


def search_job_dataframes(
    payloads: dict[str, Any], profile: JobSearchProfile
) -> JobDataFrames:
    _validate_profile(profile)
    jobs, requirements, sources = normalize_provider_payloads(payloads)
    requirements_by_job: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in requirements:
        requirements_by_job.setdefault(
            (str(row["provider"]), str(row["job_id"])), []
        ).append(row)
    included: list[dict[str, Any]] = []
    unverifiable_candidates: list[dict[str, Any]] = []
    no_match_candidates: list[dict[str, Any]] = []
    conflict_candidates: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for row in jobs:
        verdicts: list[tuple[str, FilterVerdict, Any]] = []

        def evaluate(field: str, verdict: FilterVerdict, observed: Any) -> None:
            if verdict != FilterVerdict.NOT_APPLICABLE:
                verdicts.append((field, verdict, observed))

        evaluate(
            "country",
            _membership_verdict(row.get("country_code"), profile.countries),
            row.get("country_code"),
        )
        inferred_isco = resolve_title_to_isco(" ".join(profile.job_keywords))
        keyword_text = " ".join(
            (str(row.get("_title_text") or ""), str(row.get("occupation_label") or ""))
        )
        if inferred_isco and row.get("occupation_pivot") == inferred_isco:
            keyword_text = " ".join((keyword_text, *profile.job_keywords))
        if profile.keyword_scope == "title_or_description":
            keyword_text = " ".join(
                (keyword_text, str(row.get("_description_text") or ""))
            )
        evaluate(
            "job_keywords",
            text_verdict(keyword_text, profile.job_keywords),
            keyword_text or None,
        )
        occupation_text = " ".join(
            (
                str(row.get(key) or "")
                for key in (
                    "occupation_label",
                    "occupation_code",
                    "occupation_pivot",
                    "ncs_code",
                )
            )
        )
        evaluate(
            "occupations",
            _contains_verdict(occupation_text, profile.occupations),
            occupation_text or None,
        )
        if profile.isco_codes:
            pivot_val = row.get("occupation_pivot") or ""
            evaluate(
                "isco_codes",
                _membership_verdict(pivot_val, profile.isco_codes),
                pivot_val or None,
            )
        if profile.ncs_codes:
            ncs_val = row.get("ncs_code") or ""
            evaluate(
                "ncs_codes",
                _contains_verdict(ncs_val, profile.ncs_codes),
                ncs_val or None,
            )
        evaluate(
            "locations",
            _contains_verdict(
                row.get("_location_text") or row.get("location_raw"), profile.locations
            ),
            row.get("_location_text") or row.get("location_raw"),
        )
        evaluate(
            "workplace_types",
            _membership_verdict(row.get("workplace_type"), profile.workplace_types),
            row.get("workplace_type"),
        )
        evaluate(
            "employment_types",
            _membership_verdict(row.get("employment_type"), profile.employment_types),
            row.get("employment_type"),
        )
        posting_languages = profile.posting_languages or profile.languages
        evaluate(
            "posting_languages",
            _language_verdict(row.get("posting_language"), posting_languages),
            row.get("posting_language"),
        )
        evaluate(
            "industries",
            _contains_verdict(row.get("industry_raw"), profile.industries),
            row.get("industry_raw"),
        )
        evaluate(
            "company_types",
            _membership_verdict(row.get("company_type"), profile.company_types),
            row.get("company_type"),
        )
        evaluate(
            "identity_link_status",
            _membership_verdict(
                row.get("identity_link_status"), profile.identity_link_statuses
            ),
            row.get("identity_link_status"),
        )
        evaluate(
            "public_context",
            _membership_verdict(row.get("public_context"), profile.public_contexts),
            row.get("public_context"),
        )
        evaluate(
            "public_institution_type",
            _membership_verdict(
                row.get("public_institution_type"), profile.public_institution_types
            ),
            row.get("public_institution_type"),
        )
        evaluate(
            "legal_form",
            _membership_verdict(row.get("legal_form"), profile.legal_forms),
            row.get("legal_form"),
        )
        evaluate(
            "ownership_sector",
            _membership_verdict(row.get("ownership_sector"), profile.ownership_sectors),
            row.get("ownership_sector"),
        )
        evaluate(
            "business_units",
            _contains_verdict(
                row.get("_department_text") or row.get("business_unit"),
                profile.business_units,
            ),
            row.get("business_unit"),
        )
        if profile.active_only:
            active_value = row.get("is_active")
            evaluate(
                "is_active",
                FilterVerdict.MATCH
                if active_value is True
                else FilterVerdict.UNKNOWN
                if active_value is None
                else FilterVerdict.NO_MATCH,
                active_value,
            )
        signature = _salary_signature_verdict(row, profile)
        if signature != FilterVerdict.NOT_APPLICABLE:
            signature_observed = f"{row.get('salary_currency')}/{row.get('salary_period')}/{row.get('salary_basis')}"
            evaluate("salary_comparability", signature, signature_observed)
            if (
                signature == FilterVerdict.MATCH
                and profile.minimum_salary_floor is not None
            ):
                minimum = row.get("salary_min")
                evaluate(
                    "salary_min",
                    FilterVerdict.UNKNOWN
                    if minimum is None
                    else FilterVerdict.MATCH
                    if float(minimum) >= profile.minimum_salary_floor
                    else FilterVerdict.NO_MATCH,
                    minimum,
                )
            if (
                signature == FilterVerdict.MATCH
                and profile.maximum_salary_ceiling is not None
            ):
                maximum = row.get("salary_max")
                evaluate(
                    "salary_max",
                    FilterVerdict.UNKNOWN
                    if maximum is None
                    else FilterVerdict.MATCH
                    if float(maximum) <= profile.maximum_salary_ceiling
                    else FilterVerdict.NO_MATCH,
                    maximum,
                )
        job_requirements = requirements_by_job.get(
            (str(row["provider"]), str(row["job_id"])), []
        )
        for term in profile.required_requirement_terms:
            evaluate(
                "required_requirements",
                _requirement_verdict(job_requirements, term, required_only=True),
                term,
            )
        for language in profile.required_languages:
            language_rows = [
                item
                for item in job_requirements
                if item.get("requirement_kind") == "language"
            ]
            evaluate(
                "required_languages",
                _requirement_verdict(language_rows, language, required_only=True),
                language,
            )
        for field, verdict, observed in verdicts:
            if verdict in {FilterVerdict.MATCH, FilterVerdict.NOT_APPLICABLE}:
                continue
            reason = _reason_for(field, verdict)
            exclusions.append(
                {
                    "provider": row["provider"],
                    "job_id": row["job_id"],
                    "company_name": row.get("company_name"),
                    "field": field,
                    "reason": reason,
                    "observed_value": observed,
                }
            )
        no_match = [entry for entry in verdicts if entry[1] == FilterVerdict.NO_MATCH]
        unknown = [entry for entry in verdicts if entry[1] == FilterVerdict.UNKNOWN]
        conflicts = [entry for entry in verdicts if entry[1] == FilterVerdict.CONFLICT]
        verdict_rows = [
            {
                "provider": row["provider"],
                "job_id": row["job_id"],
                "company_name": row.get("company_name"),
                "field": field,
                "verdict": verdict.value,
                "reason": _reason_for(field, verdict),
                "observed_value": observed,
            }
            for field, verdict, observed in verdicts
            if verdict not in {FilterVerdict.MATCH, FilterVerdict.NOT_APPLICABLE}
        ]
        candidate = {**row, "_verdict_rows": verdict_rows}
        if conflicts:
            conflict_candidates.append(candidate)
            continue
        if no_match:
            no_match_candidates.append(candidate)
            continue
        if unknown:
            unverifiable_candidates.append(candidate)
            if profile.unknown_policy != UnknownPolicy.INCLUDE.value:
                continue
        preference_hits = sum(
            (
                _requirement_matches(job_requirements, term, required_only=False)
                for term in profile.preferred_requirement_terms
            )
        )
        candidate = {**candidate, "preference_hits": preference_hits}
        included.append(candidate)
    included.sort(
        key=lambda row: (
            -int(row.get("preference_hits", 0)),
            str(row.get("country_code")),
            str(row.get("company_name")),
            str(row.get("job_id")),
        )
    )
    if profile.country_allocation:
        selected: list[dict[str, Any]] = []
        country_counts: dict[str, int] = {}
        for row in included:
            country = str(row.get("country_code") or "")
            limit = profile.country_allocation.get(country)
            if limit is not None and country_counts.get(country, 0) >= limit:
                exclusion = {
                    "provider": row["provider"],
                    "job_id": row["job_id"],
                    "company_name": row.get("company_name"),
                    "field": "country_allocation",
                    "reason": "country_allocation_reached",
                    "observed_value": country,
                }
                exclusions.append(exclusion)
                no_match_candidates.append(
                    {
                        **row,
                        "_verdict_rows": [
                            *row.get("_verdict_rows", []),
                            {
                                "provider": row["provider"],
                                "job_id": row["job_id"],
                                "company_name": row.get("company_name"),
                                "field": "country_allocation",
                                "verdict": FilterVerdict.NO_MATCH.value,
                                "reason": "country_allocation_reached",
                                "observed_value": country,
                            },
                        ],
                    }
                )
                continue
            country_counts[country] = country_counts.get(country, 0) + 1
            selected.append(row)
        included = selected
    matched_keys = {(str(row["provider"]), str(row["job_id"])) for row in included}
    matched_requirements = [
        row
        for row in requirements
        if (str(row["provider"]), str(row["job_id"])) in matched_keys
    ]
    job_output = [
        {key: row.get(key) for key in JOB_COLUMNS}
        | {"preference_hits": row.get("preference_hits", 0)}
        for row in included
    ]

    def verdict_output(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [item for row in rows for item in row.get("_verdict_rows", [])]

    strict_output = [
        {key: row.get(key) for key in JOB_COLUMNS}
        | {"preference_hits": row.get("preference_hits", 0)}
        for row in included
        if not row.get("_verdict_rows")
    ]
    unverifiable_output = verdict_output(unverifiable_candidates)
    no_match_output = verdict_output(no_match_candidates)
    conflict_output = verdict_output(conflict_candidates)
    location_output = [
        {
            "provider": row["provider"],
            "job_id": row["job_id"],
            "company_name": row.get("company_name"),
            "location_raw": location,
            "country_code": row.get("country_code"),
            "city": row.get("city"),
            "region": row.get("region"),
            "location_role": "primary" if index == 0 else "additional",
            "source_field": "location/offices/allLocations",
        }
        for row in included
        for index, location in enumerate(
            row.get("_location_candidates") or [row.get("location_raw")]
        )
        if location
    ]
    company_groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in included:
        key = (
            str(row.get("entity_id") or ""),
            str(row.get("company_name") or ""),
            str(row.get("country_code") or ""),
        )
        current = company_groups.setdefault(
            key,
            {
                "entity_id": row.get("entity_id"),
                "company_name": row.get("company_name"),
                "country_code": row.get("country_code"),
                "company_type": row.get("company_type"),
                "industry_raw": row.get("industry_raw"),
                "matched_job_count": 0,
            },
        )
        current["matched_job_count"] += 1
    overlap_groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for requirement in matched_requirements:
        if requirement.get("necessity") not in {"required", "preferred"}:
            continue
        key = (
            str(requirement["requirement_kind"]),
            str(requirement["normalized_key"]),
            str(requirement["label"]),
        )
        group = overlap_groups.setdefault(
            key,
            {
                "requirement_kind": key[0],
                "normalized_key": key[1],
                "label": key[2],
                "required_count": 0,
                "preferred_count": 0,
                "jobs": set(),
                "companies": set(),
                "countries": set(),
            },
        )
        if requirement["necessity"] == "required":
            group["required_count"] += 1
        elif requirement["necessity"] == "preferred":
            group["preferred_count"] += 1
        group["jobs"].add((requirement["provider"], requirement["job_id"]))
        group["companies"].add(requirement.get("company_name"))
        job = next(
            (
                item
                for item in included
                if item["provider"] == requirement["provider"]
                and item["job_id"] == requirement["job_id"]
            ),
            None,
        )
        if job and job.get("country_code"):
            group["countries"].add(job["country_code"])
    overlap = []
    denominator = len(included) or 1
    for group in overlap_groups.values():
        overlap.append(
            {
                key: group[key]
                for key in (
                    "requirement_kind",
                    "normalized_key",
                    "label",
                    "required_count",
                    "preferred_count",
                )
            }
            | {
                "posting_count": len(group["jobs"]),
                "company_count": len(group["companies"]),
                "country_count": len(group["countries"]),
                "prevalence": len(group["jobs"]) / denominator,
            }
        )
    overlap.sort(
        key=lambda row: (
            -row["posting_count"],
            row["requirement_kind"],
            row["normalized_key"],
        )
    )
    shortages = {
        country: max(
            profile.country_allocation.get(country, 0)
            - sum((row.get("country_code") == country for row in included)),
            0,
        )
        for country in profile.countries
    }
    limitations = [
        "A job posting is evidence of advertised demand, not a completed hire.",
        "Unknown fields are reported separately and do not satisfy a hard filter unless unknown_policy=include is explicit.",
        "Salary is compared only when currency, pay period, and requested salary basis match; no FX or annualization is inferred.",
        "Greenhouse and Lever are company-board scoped, not global job search APIs.",
        "MPM list results cannot satisfy location, salary, employment-type, or requirement filters.",
    ]
    return JobDataFrames(
        companies=pd.DataFrame(
            list(company_groups.values()),
            columns=(
                "entity_id",
                "company_name",
                "country_code",
                "company_type",
                "industry_raw",
                "matched_job_count",
            ),
        ),
        jobs=pd.DataFrame(job_output, columns=(*JOB_COLUMNS, "preference_hits")),
        requirements=pd.DataFrame(matched_requirements, columns=REQUIREMENT_COLUMNS),
        career_overlap=pd.DataFrame(overlap, columns=OVERLAP_COLUMNS),
        exclusions=pd.DataFrame(exclusions, columns=EXCLUSION_COLUMNS),
        sources=pd.DataFrame(sources, columns=SOURCE_COLUMNS),
        strict_matches=pd.DataFrame(
            strict_output, columns=(*JOB_COLUMNS, "preference_hits")
        ),
        unverifiable_candidates=pd.DataFrame(
            unverifiable_output, columns=VERDICT_COLUMNS
        ),
        no_matches=pd.DataFrame(no_match_output, columns=VERDICT_COLUMNS),
        conflicts=pd.DataFrame(conflict_output, columns=VERDICT_COLUMNS),
        locations=pd.DataFrame(location_output, columns=LOCATION_COLUMNS),
        metadata={
            "matched_jobs": len(included),
            "strict_matches": len(strict_output),
            "unverifiable_candidates": len(unverifiable_candidates),
            "no_matches": len(no_match_candidates),
            "conflicts": len(conflict_candidates),
            "total_jobs": len(jobs),
            "country_shortages": shortages,
            "legacy_languages_alias_used": bool(
                profile.languages and (not profile.posting_languages)
            ),
            "limitations": limitations,
        },
    )


def build_denominators(
    payloads: dict[str, Any], frames: JobDataFrames
) -> dict[str, int]:
    jobs, _requirements, sources = normalize_provider_payloads(payloads)
    return {
        "provider_returned": sum(
            (int(item.get("record_count") or 0) for item in sources)
        ),
        "normalized": len(jobs),
        "active": sum((1 for row in jobs if row.get("is_active") is True)),
        "strict_match": len(frames.strict_matches),
        "unverifiable": len(frames.unverifiable_candidates),
        "no_match": len(frames.no_matches),
        "conflict": len(frames.conflicts),
    }
