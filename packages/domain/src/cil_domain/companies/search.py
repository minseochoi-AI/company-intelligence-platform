"""Canonical responsibility owner; migrated from src/company_intel/search.py."""

from __future__ import annotations
from cil_contracts.facts import CandidateMatch
from cil_contracts.facts import SearchProfile
from cil_contracts.query import COMPANY_SEMANTIC_FIELDS
from cil_contracts.query import CompanySearchProfile
from cil_contracts.query import FieldFilter
from cil_contracts.query import FieldVerdict
from cil_contracts.query import FilterMode
from cil_contracts.query import FilterVerdict
from cil_contracts.query import SemanticValue
from cil_contracts.query import UnknownPolicy
from cil_contracts.query import combine_verdicts
from cil_contracts.query import company_search_profile_from_legacy
from cil_contracts.query import text_verdict
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, replace
from typing import Any

_SEMANTIC_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "industry": ("industry", "industries", "industry_code"),
    "ownership_sector": ("ownership_sector", "ownership"),
    "legal_form": (
        "legal_form",
        "legal_forms",
        "legal_form_code",
        "legalForm",
        "pravniForma",
    ),
    "business_activity": (
        "business_activity",
        "business_activities",
        "industry_code",
        "industry_codes",
        "sic",
        "cz_nace",
        "czNace",
        "nace",
    ),
    "market_status": ("market_status", "listing_status", "market_listing_status"),
    "public_institution_type": (
        "public_institution_type",
        "institution_type",
        "apba_type",
        "apba_type_name",
        "apbaTypeNa",
        "type01",
    ),
    "entity_category": ("entity_category", "legal_entity_category", "category"),
    "source_operation": ("operation_id", "source_operation", "source_operations"),
    "provider": ("provider",),
}

_KNOWN_CAPABILITY_STATUSES = {
    "available",
    "unavailable",
    "unsupported",
    "disabled",
    "conflict",
}


@dataclass(frozen=True)
class CompanyCandidateEvaluation:
    """A full, source-explainable decision for one candidate company."""

    entity_id: str
    name: str
    country_code: str | None
    verdict: FilterVerdict
    score: int
    matched_capabilities: tuple[str, ...]
    field_verdicts: tuple[FieldVerdict, ...]
    reason: str | None = None
    evidence: tuple[str, ...] = ()
    included: bool = False

    @property
    def status(self) -> str:
        return {
            FilterVerdict.MATCH: "matched",
            FilterVerdict.UNKNOWN: "unknown",
            FilterVerdict.CONFLICT: "conflict",
            FilterVerdict.NO_MATCH: "excluded",
            FilterVerdict.NOT_APPLICABLE: "excluded",
        }[self.verdict]


def _company_profile(
    profile: SearchProfile | CompanySearchProfile,
) -> CompanySearchProfile:
    return (
        profile
        if isinstance(profile, CompanySearchProfile)
        else company_search_profile_from_legacy(profile)
    )


def validate_company_search_profile(
    profile: CompanySearchProfile,
) -> CompanySearchProfile:
    """Validate explicit company filters before any candidate is ranked."""
    countries = tuple(
        (
            country.strip().upper()
            for country in profile.countries
            if country and country.strip()
        )
    )
    if not countries:
        raise ValueError("countries must contain at least one ISO country code")
    if countries != profile.countries:
        raise ValueError("countries must be normalized uppercase ISO country codes")
    if not (
        profile.job_keywords
        or profile.required_capabilities
        or profile.semantic_filters()
    ):
        raise ValueError(
            "provide job_keywords, required_capabilities, or a semantic company filter"
        )
    invalid_filters = [
        item.field
        for item in profile.filters()
        if item.applicable and item.field not in COMPANY_SEMANTIC_FIELDS
    ]
    if invalid_filters:
        raise ValueError(
            f"unsupported company semantic field: {', '.join(sorted(invalid_filters))}"
        )
    unknown = set(profile.allocation) - set(profile.countries)
    if unknown:
        raise ValueError("country_allocation contains countries outside countries")
    if any((value < 0 for value in profile.allocation.values())):
        raise ValueError("country_allocation values cannot be negative")
    return profile


def validate_search_profile(
    profile: SearchProfile | CompanySearchProfile,
) -> SearchProfile | CompanySearchProfile:
    """Validate old and new profile shapes while retaining the caller's type."""
    validate_company_search_profile(_company_profile(profile))
    return profile


def build_company_universe(
    profile: SearchProfile | CompanySearchProfile, candidates: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    contract = _company_profile(profile)
    validate_company_search_profile(contract)
    countries = set(contract.countries)
    return [
        row
        for row in candidates
        if str(row.get("country_code") or row.get("country") or "").upper() in countries
    ]


def _as_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_identity_conflict(row: Mapping[str, Any]) -> bool:
    value = row.get("identity_conflict")
    if isinstance(value, str):
        return value.casefold() in {"true", "yes", "1", "conflict", "ambiguous"}
    if value is True:
        return True
    status = _as_text(row.get("identity_status"))
    return status is not None and status.casefold() in {
        "conflict",
        "ambiguous",
        "merged",
    }


def _identity_field_verdict(
    row: Mapping[str, Any], profile: CompanySearchProfile
) -> FieldVerdict:
    status = _as_text(row.get("identity_status")) or "unresolved"
    if _is_identity_conflict(row):
        return FieldVerdict(
            "identity",
            FilterVerdict.CONFLICT,
            observed=(status,),
            reason="identity_conflict",
        )
    if not profile.require_resolved_identity:
        return FieldVerdict(
            "identity", FilterVerdict.NOT_APPLICABLE, observed=(status,)
        )
    if status.casefold() == "resolved":
        return FieldVerdict("identity", FilterVerdict.MATCH, observed=(status,))
    return FieldVerdict(
        "identity",
        FilterVerdict.UNKNOWN,
        observed=(status,),
        reason="identity_unresolved",
    )


def _capability_field_verdict(
    row: Mapping[str, Any], required: tuple[str, ...]
) -> FieldVerdict:
    if not required:
        return FieldVerdict("capability", FilterVerdict.NOT_APPLICABLE)
    capabilities = row.get("capabilities")
    if not isinstance(capabilities, Mapping):
        return FieldVerdict(
            "capability",
            FilterVerdict.UNKNOWN,
            expected=required,
            reason="capability_unavailable",
        )
    values: list[FilterVerdict] = []
    observed: list[str] = []
    for capability in required:
        raw_status = capabilities.get(capability)
        status = _as_text(raw_status)
        if status is None:
            values.append(FilterVerdict.UNKNOWN)
            continue
        normalized = status.casefold()
        observed.append(f"{capability}={status}")
        if normalized == "available":
            values.append(FilterVerdict.MATCH)
        elif normalized == "conflict":
            values.append(FilterVerdict.CONFLICT)
        elif normalized in _KNOWN_CAPABILITY_STATUSES:
            values.append(FilterVerdict.NO_MATCH)
        else:
            values.append(FilterVerdict.UNKNOWN)
    verdict = combine_verdicts(values)
    reason = None if verdict == FilterVerdict.MATCH else f"capability_{verdict.value}"
    return FieldVerdict(
        "capability",
        verdict,
        expected=required,
        observed=tuple(observed),
        reason=reason,
    )


def _keyword_field_verdict(
    row: Mapping[str, Any], keywords: tuple[str, ...]
) -> FieldVerdict:
    if not keywords:
        return FieldVerdict("job_keyword", FilterVerdict.NOT_APPLICABLE)
    values = [
        _as_text(row.get(field))
        for field in (
            "name",
            "legal_name",
            "title",
            "occupation_label",
            "industry",
            "industry_code",
        )
    ]
    title = " ".join((value for value in values if value))
    verdict = text_verdict(title, keywords)
    reason = None if verdict == FilterVerdict.MATCH else f"job_keyword_{verdict.value}"
    return FieldVerdict(
        "job_keyword",
        verdict,
        expected=keywords,
        observed=(title,) if title else (),
        reason=reason,
    )


def _semantic_values_from_value(
    value: object, *, source_field: str, inherited_namespace: str | None = None
) -> list[SemanticValue]:
    if isinstance(value, SemanticValue):
        return [value]
    if isinstance(value, str):
        text = value.strip()
        return [SemanticValue(text, inherited_namespace, source_field)] if text else []
    if isinstance(value, Mapping):
        namespace = (
            _as_text(
                value.get("namespace")
                or value.get("vocabulary_namespace")
                or value.get("taxonomy_namespace")
            )
            or inherited_namespace
        )
        output: list[SemanticValue] = []
        for key in ("normalized_value", "value", "code", "id", "label", "name"):
            candidate = value.get(key)
            if isinstance(candidate, (str, int, float)) and (
                not isinstance(candidate, bool)
            ):
                text = str(candidate).strip()
                if text:
                    output.append(SemanticValue(text, namespace, source_field))
        if output:
            return output
        for key in ("values", "items", "records"):
            if key in value:
                return _semantic_values_from_value(
                    value[key], source_field=source_field, inherited_namespace=namespace
                )
        return []
    if isinstance(value, Iterable) and (not isinstance(value, (bytes, bytearray))):
        output: list[SemanticValue] = []
        for item in value:
            output.extend(
                _semantic_values_from_value(
                    item,
                    source_field=source_field,
                    inherited_namespace=inherited_namespace,
                )
            )
        return output
    if isinstance(value, (int, float)) and (not isinstance(value, bool)):
        return [SemanticValue(str(value), inherited_namespace, source_field)]
    return []


def _semantic_values(row: Mapping[str, Any], field: str) -> tuple[SemanticValue, ...]:
    aliases = _SEMANTIC_FIELD_ALIASES[field]
    values: list[SemanticValue] = []
    for container_name in ("semantic_fields", "taxonomy"):
        container = row.get(container_name)
        if isinstance(container, Mapping):
            for alias in aliases:
                if alias in container:
                    values.extend(
                        _semantic_values_from_value(
                            container[alias], source_field=alias
                        )
                    )
    for alias in aliases:
        if alias in row:
            values.extend(_semantic_values_from_value(row[alias], source_field=alias))
    seen: set[tuple[str | None, str]] = set()
    result: list[SemanticValue] = []
    for value in values:
        key = (
            value.namespace.casefold() if value.namespace else None,
            value.value.casefold(),
        )
        if key not in seen:
            seen.add(key)
            result.append(value)
    return tuple(result)


def _selector_matches(
    observed_value: SemanticValue, selector: str
) -> tuple[bool, bool]:
    """Return ``(exact, namespace_required)`` without splitting provider namespaces.

    Namespaces may themselves contain colons, such as
    ``ARES:pravniForma``.  Matching therefore uses the observed namespace as
    the exact prefix instead of splitting a selector at its first colon.
    """
    expected = selector.strip()
    if observed_value.namespace:
        prefix = f"{observed_value.namespace}:"
        if expected.casefold().startswith(prefix.casefold()):
            return (
                observed_value.value.casefold() == expected[len(prefix) :].casefold(),
                False,
            )
        if (
            ":" not in expected
            and observed_value.value.casefold() == expected.casefold()
        ):
            return (False, True)
        return (False, False)
    return (observed_value.value.casefold() == expected.casefold(), False)


def _semantic_field_verdict(
    field_filter: FieldFilter, observed_values: tuple[SemanticValue, ...]
) -> FieldVerdict:
    field = field_filter.field
    expected = field_filter.values
    if not expected:
        return FieldVerdict(field, FilterVerdict.NOT_APPLICABLE, mode=field_filter.mode)
    observed = tuple((value.selector for value in observed_values))
    if not observed_values:
        return FieldVerdict(
            field,
            FilterVerdict.UNKNOWN,
            expected=expected,
            mode=field_filter.mode,
            observed=observed,
            reason=f"{field}_unavailable",
        )
    matched: list[bool] = []
    ambiguous: list[bool] = []
    for selector in expected:
        selector_matched = False
        selector_ambiguous = False
        for observed_value in observed_values:
            exact, namespace_required = _selector_matches(observed_value, selector)
            selector_matched = selector_matched or exact
            selector_ambiguous = selector_ambiguous or namespace_required
        matched.append(selector_matched)
        ambiguous.append(selector_ambiguous)
    is_match = any(matched) if field_filter.mode == FilterMode.ANY else all(matched)
    if is_match:
        return FieldVerdict(
            field,
            FilterVerdict.MATCH,
            expected=expected,
            mode=field_filter.mode,
            observed=observed,
        )
    if any(ambiguous):
        return FieldVerdict(
            field,
            FilterVerdict.CONFLICT,
            expected=expected,
            mode=field_filter.mode,
            observed=observed,
            reason=f"{field}_namespace_required",
        )
    return FieldVerdict(
        field,
        FilterVerdict.NO_MATCH,
        expected=expected,
        mode=field_filter.mode,
        observed=observed,
        reason=f"{field}_not_matched",
    )


def _evaluation_reason(
    field_verdicts: tuple[FieldVerdict, ...], verdict: FilterVerdict
) -> str | None:
    for field_verdict in field_verdicts:
        if (
            field_verdict.field == "identity"
            and field_verdict.verdict in {FilterVerdict.UNKNOWN, FilterVerdict.CONFLICT}
            and field_verdict.reason
        ):
            return field_verdict.reason
    for field_verdict in field_verdicts:
        if field_verdict.verdict == verdict and field_verdict.reason:
            return field_verdict.reason
    return None


def _included(verdict: FilterVerdict, policy: UnknownPolicy) -> bool:
    return verdict == FilterVerdict.MATCH or (
        verdict == FilterVerdict.UNKNOWN and policy == UnknownPolicy.INCLUDE
    )


def evaluate_company_candidate(
    profile: SearchProfile | CompanySearchProfile, row: Mapping[str, Any]
) -> CompanyCandidateEvaluation:
    """Evaluate every populated filter; absence stays UNKNOWN rather than false."""
    contract = _company_profile(profile)
    validate_company_search_profile(contract)
    field_verdicts: list[FieldVerdict] = [
        _identity_field_verdict(row, contract),
        _capability_field_verdict(row, contract.required_capabilities),
        _keyword_field_verdict(row, contract.job_keywords),
    ]
    for field_filter in contract.filters():
        if not field_filter.applicable:
            field_verdicts.append(
                FieldVerdict(
                    field_filter.field,
                    FilterVerdict.NOT_APPLICABLE,
                    expected=field_filter.values,
                    mode=field_filter.mode,
                    reason=field_filter.unavailable_reason or "filter_not_applicable",
                )
            )
            continue
        field_verdicts.append(
            _semantic_field_verdict(
                field_filter, _semantic_values(row, field_filter.field)
            )
        )
    verdicts = tuple(field_verdicts)
    verdict = combine_verdicts((item.verdict for item in verdicts))
    title = " ".join(
        (
            value
            for value in (
                _as_text(row.get("name")),
                _as_text(row.get("title")),
                _as_text(row.get("occupation_label")),
                _as_text(row.get("industry")),
                _as_text(row.get("industry_code")),
            )
            if value
        )
    )
    keyword_hits = sum(
        (keyword.casefold() in title.casefold() for keyword in contract.job_keywords)
    )
    capabilities = (
        row.get("capabilities") if isinstance(row.get("capabilities"), Mapping) else {}
    )
    matched_capabilities = tuple(
        sorted(
            (
                capability
                for capability in contract.required_capabilities
                if capabilities.get(capability) == "available"
            )
        )
    )
    score = (
        len(matched_capabilities) * 100
        + keyword_hits * 10
        + int(bool(row.get("evidence_urls")))
    )
    evidence_urls = row.get("evidence_urls", ())
    evidence = (
        tuple(sorted((str(url) for url in evidence_urls if url)))
        if isinstance(evidence_urls, Iterable)
        and (not isinstance(evidence_urls, (str, bytes, bytearray)))
        else ()
    )
    country = _as_text(row.get("country_code") or row.get("country"))
    return CompanyCandidateEvaluation(
        entity_id=str(row.get("entity_id", "")),
        name=str(row.get("name") or row.get("legal_name") or ""),
        country_code=country.upper() if country else None,
        verdict=verdict,
        score=score,
        matched_capabilities=matched_capabilities,
        field_verdicts=verdicts,
        reason=_evaluation_reason(verdicts, verdict),
        evidence=evidence,
        included=_included(verdict, contract.unknown_policy),
    )


def _sort_evaluations(
    evaluations: Iterable[CompanyCandidateEvaluation],
) -> list[CompanyCandidateEvaluation]:
    priority = {
        FilterVerdict.MATCH: 0,
        FilterVerdict.UNKNOWN: 1,
        FilterVerdict.CONFLICT: 2,
        FilterVerdict.NO_MATCH: 3,
        FilterVerdict.NOT_APPLICABLE: 4,
    }
    return sorted(
        evaluations,
        key=lambda item: (
            priority[item.verdict],
            -item.score if item.verdict == FilterVerdict.MATCH else 0,
            item.entity_id,
        ),
    )


def _apply_country_allocation(
    evaluations: list[CompanyCandidateEvaluation], profile: CompanySearchProfile
) -> list[CompanyCandidateEvaluation]:
    if not profile.allocation:
        return evaluations
    allocated: dict[str, int] = {country: 0 for country in profile.allocation}
    output: list[CompanyCandidateEvaluation] = []
    for evaluation in evaluations:
        country = evaluation.country_code
        limit = profile.allocation.get(country or "")
        if evaluation.verdict != FilterVerdict.MATCH or limit is None:
            output.append(evaluation)
            continue
        if allocated[country or ""] < limit:
            allocated[country or ""] += 1
            output.append(evaluation)
            continue
        allocation_verdict = FieldVerdict(
            "country_allocation",
            FilterVerdict.NO_MATCH,
            expected=(str(limit),),
            observed=(country or "",),
            reason="country_allocation_reached",
        )
        output.append(
            replace(
                evaluation,
                verdict=FilterVerdict.NO_MATCH,
                field_verdicts=(*evaluation.field_verdicts, allocation_verdict),
                reason="country_allocation_reached",
                included=False,
            )
        )
    return output


def apply_country_allocation(
    evaluations: list[CompanyCandidateEvaluation], profile: CompanySearchProfile
) -> list[CompanyCandidateEvaluation]:
    """Apply a per-country cap only after strict candidate ranking is known."""
    return _apply_country_allocation(evaluations, profile)


def rank_candidate_evaluations(
    profile: SearchProfile | CompanySearchProfile, candidates: Iterable[dict[str, Any]]
) -> list[CompanyCandidateEvaluation]:
    """Return strict, unverifiable, conflict, and excluded candidates separately."""
    contract = _company_profile(profile)
    rows = build_company_universe(contract, candidates)
    evaluations = _sort_evaluations(
        (evaluate_company_candidate(contract, row) for row in rows)
    )
    return _sort_evaluations(apply_country_allocation(evaluations, contract))


def _legacy_match(evaluation: CompanyCandidateEvaluation) -> CandidateMatch:
    return CandidateMatch(
        evaluation.entity_id,
        evaluation.name,
        evaluation.country_code,
        evaluation.status,
        evaluation.score,
        evaluation.matched_capabilities,
        evaluation.reason,
        evaluation.evidence,
    )


def rank_candidates(
    profile: SearchProfile | CompanySearchProfile, candidates: Iterable[dict[str, Any]]
) -> list[CandidateMatch]:
    """Return the legacy CandidateMatch view over the richer five-state result."""
    return [
        _legacy_match(evaluation)
        for evaluation in rank_candidate_evaluations(profile, candidates)
    ]


def explain_company_evaluation(
    evaluation: CompanyCandidateEvaluation,
) -> dict[str, Any]:
    """Render atomic, user-visible reasons without exposing raw provider payloads."""
    return {
        "entity_id": evaluation.entity_id,
        "name": evaluation.name,
        "country_code": evaluation.country_code,
        "status": evaluation.status,
        "verdict": evaluation.verdict.value,
        "score": evaluation.score,
        "included": evaluation.included,
        "matched_capabilities": list(evaluation.matched_capabilities),
        "reason": evaluation.reason,
        "field_verdicts": [
            {
                **asdict(field_verdict),
                "verdict": field_verdict.verdict.value,
                "expected": list(field_verdict.expected),
                "observed": list(field_verdict.observed),
            }
            for field_verdict in evaluation.field_verdicts
        ],
        "evidence": list(evaluation.evidence),
    }


def explain_candidate(match: CandidateMatch) -> dict[str, Any]:
    """Keep the original public explanation shape for existing callers."""
    return {
        "entity_id": match.entity_id,
        "status": match.status,
        "score": match.score,
        "matched_capabilities": list(match.matched_capabilities),
        "exclusion_reason": match.exclusion_reason,
        "evidence": list(match.evidence),
    }


def candidate_verdict(match: CandidateMatch) -> FilterVerdict:
    if match.status == "matched":
        return FilterVerdict.MATCH
    if match.status == "unknown":
        return FilterVerdict.UNKNOWN
    if match.status == "conflict":
        return FilterVerdict.CONFLICT
    return FilterVerdict.NO_MATCH


def identity_link_status(row: Mapping[str, Any]) -> str:
    value = str(
        row.get("identity_link_status") or row.get("identity_status") or "unresolved"
    )
    return (
        value
        if value in {"linked", "candidate", "unresolved", "conflict"}
        else "unresolved"
    )


def public_sector_filter(
    row: Mapping[str, Any], requested: tuple[str, ...] = ()
) -> FieldVerdict:
    """Use legal/ownership filters only where an entity link is verified."""
    if not requested:
        return FieldVerdict("public_sector", FilterVerdict.NOT_APPLICABLE)
    status = identity_link_status(row)
    if status == "conflict":
        return FieldVerdict(
            "public_sector",
            FilterVerdict.CONFLICT,
            expected=requested,
            reason="identity_conflict",
        )
    if status != "linked":
        return FieldVerdict(
            "public_sector",
            FilterVerdict.UNKNOWN,
            expected=requested,
            reason="identity_unresolved",
        )
    values = tuple(
        (
            str(item)
            for item in (
                row.get("ownership_sector"),
                row.get("public_institution_type"),
                row.get("legal_form"),
            )
            if item
        )
    )
    return _semantic_field_verdict(
        FieldFilter("ownership_sector", requested),
        tuple((SemanticValue(item) for item in values)),
    )
