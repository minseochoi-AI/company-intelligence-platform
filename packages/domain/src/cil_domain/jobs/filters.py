"""Canonical responsibility owner; migrated from src/company_intel/job_search.py."""

from __future__ import annotations
from cil_contracts.jobs import JobSearchProfile
from cil_contracts.query import FilterVerdict
from cil_contracts.query import UnknownPolicy
from cil_contracts.query import text_verdict
from dataclasses import dataclass, field
from typing import Any
import re


def _active_at(closing_at: Any, snapshot_at: str, *, listed_as_live: bool) -> bool:
    if not closing_at:
        return listed_as_live
    closing = re.sub("[^0-9]", "", str(closing_at))[:8]
    snapshot = re.sub("[^0-9]", "", snapshot_at)[:8]
    return bool(len(closing) == 8 and len(snapshot) == 8 and (closing >= snapshot))


def _contains(value: Any, terms: tuple[str, ...]) -> bool:
    lowered = str(value or "").casefold()
    return any((term.casefold() in lowered for term in terms))


def _membership_verdict(value: Any, expected: tuple[str, ...]) -> FilterVerdict:
    """Evaluate an enum field without converting missing data to a rejection."""
    if not expected:
        return FilterVerdict.NOT_APPLICABLE
    if value is None or not str(value).strip() or str(value).casefold() == "unknown":
        return FilterVerdict.UNKNOWN
    return FilterVerdict.MATCH if str(value) in expected else FilterVerdict.NO_MATCH


def _contains_verdict(value: Any, terms: tuple[str, ...]) -> FilterVerdict:
    if not terms:
        return FilterVerdict.NOT_APPLICABLE
    if value is None or not str(value).strip():
        return FilterVerdict.UNKNOWN
    return FilterVerdict.MATCH if _contains(value, terms) else FilterVerdict.NO_MATCH


def _language_verdict(value: Any, terms: tuple[str, ...]) -> FilterVerdict:
    if not terms:
        return FilterVerdict.NOT_APPLICABLE
    if value is None or not str(value).strip():
        return FilterVerdict.UNKNOWN
    aliases = {
        "en": "english",
        "ko": "korean",
        "cs": "czech",
        "de": "german",
        "fr": "french",
        "es": "spanish",
        "ja": "japanese",
        "zh": "mandarin",
    }
    observed = str(value).casefold().strip()
    expanded = " ".join((observed, aliases.get(observed, "")))
    return FilterVerdict.MATCH if _contains(expanded, terms) else FilterVerdict.NO_MATCH


def _salary_signature_verdict(
    row: dict[str, Any], profile: JobSearchProfile
) -> FilterVerdict:
    """Return whether a structured range has the requested comparison signature."""
    if profile.minimum_salary_floor is None and profile.maximum_salary_ceiling is None:
        return FilterVerdict.NOT_APPLICABLE
    required = (profile.salary_currency, profile.salary_period)
    observed = (row.get("salary_currency"), row.get("salary_period"))
    if any(
        (value is None or not str(value).strip() for value in (*required, *observed))
    ):
        return FilterVerdict.UNKNOWN
    if observed != required:
        return FilterVerdict.UNKNOWN
    if (
        profile.salary_basis is not None
        and row.get("salary_basis") != profile.salary_basis
    ):
        return FilterVerdict.UNKNOWN
    return FilterVerdict.MATCH


def _reason_for(field: str, verdict: FilterVerdict) -> str:
    return {
        FilterVerdict.NO_MATCH: f"{field}_not_matched",
        FilterVerdict.UNKNOWN: f"{field}_unverifiable",
        FilterVerdict.CONFLICT: f"{field}_conflict",
    }.get(verdict, f"{field}_not_applicable")


def _requirement_matches(
    rows: list[dict[str, Any]], term: str, *, required_only: bool
) -> bool:
    for row in rows:
        if required_only and row.get("necessity") != "required":
            continue
        if not required_only and row.get("necessity") not in {"required", "preferred"}:
            continue
        haystack = " ".join(
            (str(row.get(key) or "") for key in ("normalized_key", "label", "value"))
        )
        if term.casefold() in haystack.casefold():
            return True
    return False


def _requirement_verdict(
    rows: list[dict[str, Any]], term: str, *, required_only: bool
) -> FilterVerdict:
    if not rows:
        return FilterVerdict.UNKNOWN
    return (
        FilterVerdict.MATCH
        if _requirement_matches(rows, term, required_only=required_only)
        else FilterVerdict.NO_MATCH
    )


def _record_verdict(
    reasons: list[tuple[str, str, Any]],
    field: str,
    verdict: FilterVerdict,
    observed: Any,
) -> None:
    if verdict == FilterVerdict.NO_MATCH:
        reasons.append((field, f"{field}_not_matched", observed))
    elif verdict == FilterVerdict.UNKNOWN:
        reasons.append((field, f"{field}_unverifiable", observed))
    elif verdict == FilterVerdict.CONFLICT:
        reasons.append((field, f"{field}_conflict", observed))


def _validate_profile(profile: JobSearchProfile) -> None:
    if not profile.countries:
        raise ValueError("countries must contain at least one ISO code")
    if (
        not profile.job_keywords
        and (not profile.occupations)
        and (not profile.isco_codes)
        and (not profile.ncs_codes)
    ):
        raise ValueError("job_keywords or occupations must contain an explicit term")
    unknown = set(profile.country_allocation) - set(profile.countries)
    if unknown:
        raise ValueError("country_allocation contains out-of-scope countries")
    if (
        profile.minimum_salary_floor is not None
        or profile.maximum_salary_ceiling is not None
    ) and (not profile.salary_currency or not profile.salary_period):
        raise ValueError(
            "salary_currency and salary_period are required with a salary floor or ceiling"
        )
    if profile.unknown_policy not in {item.value for item in UnknownPolicy}:
        raise ValueError("unknown_policy must be exclude, report, or include")
    if profile.keyword_scope not in {"title_or_occupation", "title_or_description"}:
        raise ValueError(
            "keyword_scope must be title_or_occupation or title_or_description"
        )


def active_as_of(row: dict[str, Any], cutoff: str) -> bool | None:
    """Evaluate a posting's active state at a supplied snapshot cutoff."""
    closing = row.get("closing_at")
    if closing in (None, ""):
        return row.get("is_active") if isinstance(row.get("is_active"), bool) else None
    return _active_at(closing, cutoff, listed_as_live=bool(row.get("is_active")))
