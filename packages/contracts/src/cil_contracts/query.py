"""Canonical responsibility owner; migrated from src/company_intel/query_contract.py."""

from __future__ import annotations
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class FilterVerdict(StrEnum):
    MATCH = "match"
    NO_MATCH = "no_match"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"
    NOT_APPLICABLE = "not_applicable"


class UnknownPolicy(StrEnum):
    EXCLUDE = "exclude"
    REPORT = "report"
    INCLUDE = "include"


class FilterMode(StrEnum):
    """How values within one semantic field are combined."""

    ANY = "any"
    ALL = "all"


@dataclass(frozen=True)
class FieldFilter:
    """A field-level filter with an explicit combination and applicability rule."""

    field: str
    values: tuple[str, ...]
    mode: FilterMode = FilterMode.ANY
    applicable: bool = True
    unavailable_reason: str | None = None


@dataclass(frozen=True)
class SemanticValue:
    """A source-preserving value used by a company-search facet.

    ``namespace`` deliberately remains part of the value's identity.  For
    example, a GLEIF legal-form code and an ARES legal-form code may both be
    strings, but they are not interchangeable merely because their display
    labels look similar.
    """

    value: str
    namespace: str | None = None
    source_field: str | None = None

    @property
    def selector(self) -> str:
        """Return the unambiguous selector accepted by company search."""
        return f"{self.namespace}:{self.value}" if self.namespace else self.value


@dataclass(frozen=True)
class FieldVerdict:
    """One atomic filter decision with the values that produced it."""

    field: str
    verdict: FilterVerdict
    expected: tuple[str, ...] = ()
    mode: FilterMode = FilterMode.ANY
    observed: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class CompanySearchProfile:
    """Normalized company-search filters, without provider-field conflation.

    Values inside a single field use OR semantics; populated fields combine
    with AND semantics.  Native provider taxonomies remain separate through
    ``namespace:value`` selectors.  This profile is an adapter alongside the
    legacy :class:`company_intel.models.SearchProfile`, not a replacement for
    it, so existing API and CLI payloads remain valid.
    """

    countries: tuple[str, ...]
    job_keywords: tuple[str, ...] = ()
    industries: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    country_allocation: Mapping[str, int] | None = None
    ownership_sectors: tuple[str, ...] = ()
    legal_forms: tuple[str, ...] = ()
    business_activities: tuple[str, ...] = ()
    market_statuses: tuple[str, ...] = ()
    public_institution_types: tuple[str, ...] = ()
    entity_categories: tuple[str, ...] = ()
    source_operations: tuple[str, ...] = ()
    providers: tuple[str, ...] = ()
    require_resolved_identity: bool = True
    unknown_policy: UnknownPolicy = UnknownPolicy.REPORT
    field_filters: tuple[FieldFilter, ...] = ()
    unsupported_filters: tuple[FieldFilter, ...] = ()

    def semantic_filters(self) -> dict[str, tuple[str, ...]]:
        """Return only populated, provider-neutral semantic filter axes."""
        return {
            item.field: item.values
            for item in self.filters()
            if item.applicable and item.values
        }

    def filters(self) -> tuple[FieldFilter, ...]:
        """Return named filters plus explicit overrides in a stable order."""
        named = (
            FieldFilter("industry", self.industries),
            FieldFilter("ownership_sector", self.ownership_sectors),
            FieldFilter("legal_form", self.legal_forms),
            FieldFilter("business_activity", self.business_activities),
            FieldFilter("market_status", self.market_statuses),
            FieldFilter("public_institution_type", self.public_institution_types),
            FieldFilter("entity_category", self.entity_categories),
            FieldFilter("source_operation", self.source_operations),
            FieldFilter("provider", self.providers),
        )
        overrides = {item.field: item for item in self.field_filters}
        ordered = [
            overrides.pop(item.field, item)
            for item in named
            if item.values or item.field in overrides
        ]
        ordered.extend((overrides[field] for field in sorted(overrides)))
        ordered.extend(self.unsupported_filters)
        return tuple(ordered)

    @property
    def allocation(self) -> dict[str, int]:
        return dict(self.country_allocation or {})


_PROFILE_LIST_FIELDS = ("countries", "job_keywords", "required_capabilities")

COMPANY_SEMANTIC_FIELDS = frozenset(
    {
        "industry",
        "ownership_sector",
        "legal_form",
        "business_activity",
        "market_status",
        "public_institution_type",
        "entity_category",
        "source_operation",
        "provider",
    }
)

_JOB_ONLY_COMPANY_INPUTS = (
    "languages",
    "employment_types",
    "workplace_types",
    "locations",
    "salary_currency",
    "salary_period",
    "salary_basis",
)


def _string_tuple(value: object, *, field: str) -> tuple[str, ...]:
    """Coerce a JSON scalar/list to a deduplicated tuple without guessing."""
    if value is None:
        return ()
    if isinstance(value, str):
        values = (value,)
    elif isinstance(value, Iterable) and (
        not isinstance(value, (bytes, bytearray, Mapping))
    ):
        values = tuple(value)
    else:
        raise ValueError(f"{field} must be a string or list of strings")
    cleaned = tuple(
        dict.fromkeys(
            (item.strip() for item in values if isinstance(item, str) and item.strip())
        )
    )
    if any((not isinstance(item, str) for item in values)):
        raise ValueError(f"{field} must contain only strings")
    return cleaned


def _merge_filter_values(
    value: Mapping[str, Any], field: str, aliases: tuple[str, ...] = ()
) -> tuple[str, ...]:
    values: list[str] = []
    for name in (field, *aliases):
        values.extend(_string_tuple(value.get(name), field=name))
    taxonomy_filters = value.get("semantic_filters")
    if taxonomy_filters is not None:
        if not isinstance(taxonomy_filters, Mapping):
            raise ValueError(
                "semantic_filters must be an object keyed by semantic field"
            )
        for name in (field, *aliases):
            values.extend(
                _string_tuple(
                    taxonomy_filters.get(name), field=f"semantic_filters.{name}"
                )
            )
    return tuple(dict.fromkeys(values))


def _field_filter_from_mapping(item: Mapping[str, Any]) -> FieldFilter:
    field = item.get("field")
    if not isinstance(field, str) or not field.strip():
        raise ValueError("field_filters entries require a non-empty field")
    values = _string_tuple(item.get("values"), field=f"field_filters.{field}.values")
    if not values:
        raise ValueError("field_filters entries require at least one value")
    mode_value = item.get("mode", FilterMode.ANY)
    try:
        mode = (
            mode_value
            if isinstance(mode_value, FilterMode)
            else FilterMode(str(mode_value))
        )
    except ValueError as error:
        raise ValueError("field_filters mode must be 'any' or 'all'") from error
    applicable = item.get("applicable", True)
    if not isinstance(applicable, bool):
        raise ValueError("field_filters applicable must be a boolean")
    reason = item.get("unavailable_reason")
    if reason is not None and (not isinstance(reason, str)):
        raise ValueError("field_filters unavailable_reason must be a string")
    return FieldFilter(field.strip(), values, mode, applicable, reason)


def _parse_field_filters(value: Mapping[str, Any]) -> tuple[FieldFilter, ...]:
    raw = value.get("field_filters", ())
    if raw is None:
        return ()
    if isinstance(raw, Mapping):
        if "field" in raw:
            entries: Iterable[object] = (raw,)
        else:
            entries = (
                {"field": field, "values": values} for field, values in raw.items()
            )
    elif isinstance(raw, Iterable) and (not isinstance(raw, (str, bytes, bytearray))):
        entries = raw
    else:
        raise ValueError("field_filters must be an object or list of objects")
    filters: list[FieldFilter] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("field_filters entries must be objects")
        field_filter = _field_filter_from_mapping(entry)
        if field_filter.field not in COMPANY_SEMANTIC_FIELDS:
            raise ValueError(
                f"unsupported company semantic field: {field_filter.field}"
            )
        if field_filter.field in seen:
            raise ValueError(f"field_filters duplicates field: {field_filter.field}")
        seen.add(field_filter.field)
        filters.append(field_filter)
    return tuple(filters)


def _job_only_filters_from_mapping(value: Mapping[str, Any]) -> tuple[FieldFilter, ...]:
    filters = []
    for field in _JOB_ONLY_COMPANY_INPUTS:
        values = _string_tuple(value.get(field), field=field)
        if values:
            filters.append(
                FieldFilter(
                    field,
                    values,
                    applicable=False,
                    unavailable_reason=f"{field}_requires_job_search",
                )
            )
    return tuple(filters)


def company_search_profile_from_mapping(
    value: Mapping[str, Any],
) -> CompanySearchProfile:
    """Parse a JSON-ready profile into an explicit company-search contract.

    The aliases are input-only compatibility aids.  They do not turn one
    provider's legal-form, activity, or institution codes into another
    provider's vocabulary.
    """
    if not isinstance(value, Mapping):
        raise ValueError("company search profile must be an object")
    unknown_policy = value.get("unknown_policy", UnknownPolicy.REPORT)
    try:
        policy = (
            unknown_policy
            if isinstance(unknown_policy, UnknownPolicy)
            else UnknownPolicy(str(unknown_policy))
        )
    except ValueError as error:
        choices = ", ".join((item.value for item in UnknownPolicy))
        raise ValueError(f"unknown_policy must be one of: {choices}") from error
    allocation_raw = value.get("country_allocation", {})
    if not isinstance(allocation_raw, Mapping):
        raise ValueError("country_allocation must be an object")
    allocation: dict[str, int] = {}
    for country, limit in allocation_raw.items():
        if (
            not isinstance(country, str)
            or not country.strip()
            or isinstance(limit, bool)
            or (not isinstance(limit, int))
        ):
            raise ValueError(
                "country_allocation must map country strings to integer limits"
            )
        allocation[country.strip().upper()] = limit
    profile_values = {
        name: _string_tuple(value.get(name), field=name)
        for name in _PROFILE_LIST_FIELDS
    }
    profile_values["countries"] = tuple(
        (country.upper() for country in profile_values["countries"])
    )
    identity_value = value.get("require_resolved_identity", True)
    if not isinstance(identity_value, bool):
        raise ValueError("require_resolved_identity must be a boolean")
    return CompanySearchProfile(
        **profile_values,
        country_allocation=allocation,
        industries=_merge_filter_values(value, "industries", ("industry",)),
        ownership_sectors=_merge_filter_values(
            value, "ownership_sectors", ("ownership_sector",)
        ),
        legal_forms=_merge_filter_values(value, "legal_forms", ("legal_form",)),
        business_activities=_merge_filter_values(
            value, "business_activities", ("business_activity", "industry_codes")
        ),
        market_statuses=_merge_filter_values(
            value, "market_statuses", ("market_status",)
        ),
        public_institution_types=_merge_filter_values(
            value, "public_institution_types", ("public_institution_type",)
        ),
        entity_categories=_merge_filter_values(
            value, "entity_categories", ("entity_category",)
        ),
        source_operations=_merge_filter_values(
            value, "source_operations", ("source_operation",)
        ),
        providers=_merge_filter_values(value, "providers", ("provider",)),
        require_resolved_identity=identity_value,
        unknown_policy=policy,
        field_filters=_parse_field_filters(value),
        unsupported_filters=_job_only_filters_from_mapping(value),
    )


def company_search_profile_from_legacy(profile: object) -> CompanySearchProfile:
    """Adapt the original SearchProfile shape without importing its model.

    Keeping this duck-typed avoids a query-contract -> models dependency and
    lets callers migrate one endpoint at a time.
    """
    unsupported_filters = tuple(
        (
            FieldFilter(
                field,
                tuple(
                    (
                        str(value)
                        for value in getattr(profile, field, ())
                        if str(value).strip()
                    )
                ),
                applicable=False,
                unavailable_reason=f"{field}_requires_job_search",
            )
            for field in ("languages", "employment_types")
            if getattr(profile, field, ())
        )
    )
    return CompanySearchProfile(
        countries=tuple(
            (str(value).upper() for value in getattr(profile, "countries", ()))
        ),
        job_keywords=tuple(
            (str(value) for value in getattr(profile, "job_keywords", ()))
        ),
        industries=tuple((str(value) for value in getattr(profile, "industries", ()))),
        required_capabilities=tuple(
            (str(value) for value in getattr(profile, "required_capabilities", ()))
        ),
        country_allocation={
            str(country).upper(): limit
            for country, limit in dict(
                getattr(profile, "country_allocation", {}) or {}
            ).items()
        },
        unsupported_filters=unsupported_filters,
    )


@dataclass(frozen=True)
class AtomicSearchProfile:
    """A provider-neutral search request.

    ``required_languages`` means a language demanded from the applicant.  It
    is deliberately distinct from a posting's display language.
    """

    countries: tuple[str, ...]
    job_terms: tuple[str, ...]
    occupations: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    workplace_types: tuple[str, ...] = ()
    employment_types: tuple[str, ...] = ()
    required_languages: tuple[str, ...] = ()
    unknown_policy: UnknownPolicy = UnknownPolicy.EXCLUDE
    keyword_scope: str = "title_or_occupation"
    salary_currency: str | None = None
    salary_period: str | None = None
    salary_basis: str | None = None
    required_terms: tuple[str, ...] = ()
    preferred_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComparabilityPolicy:
    require_same_country: bool = True
    require_same_currency: bool = True
    require_same_period: bool = True
    require_same_unit: bool = True
    require_same_concept: bool = True


def combine_verdicts(verdicts: Iterable[FilterVerdict]) -> FilterVerdict:
    values = set(verdicts)
    if FilterVerdict.CONFLICT in values:
        return FilterVerdict.CONFLICT
    if FilterVerdict.NO_MATCH in values:
        return FilterVerdict.NO_MATCH
    if FilterVerdict.UNKNOWN in values:
        return FilterVerdict.UNKNOWN
    if values and values <= {FilterVerdict.MATCH, FilterVerdict.NOT_APPLICABLE}:
        return FilterVerdict.MATCH
    return FilterVerdict.NOT_APPLICABLE


def text_verdict(value: object, terms: tuple[str, ...]) -> FilterVerdict:
    if not terms:
        return FilterVerdict.NOT_APPLICABLE
    if value is None or not str(value).strip():
        return FilterVerdict.UNKNOWN
    lowered = str(value).casefold()
    return (
        FilterVerdict.MATCH
        if any((term.casefold() in lowered for term in terms))
        else FilterVerdict.NO_MATCH
    )


class QueryMode(StrEnum):
    CURRENT_JOB = "current_job"
    JOB_TREND = "job_trend"


@dataclass(frozen=True)
class CurrentJobQuery:
    profile: Mapping[str, Any]
    snapshot_id: str | None = None
    active_as_of: str | None = None


@dataclass(frozen=True)
class JobTrendQuery:
    profile: Mapping[str, Any]
    metric: str
    period_start: str | None = None
    period_end: str | None = None
    comparison_signature: tuple[str, ...] = ()


@dataclass(frozen=True)
class SelectionProfile:
    mode: QueryMode
    purpose: str
    selections: tuple[tuple[str, str], ...]
    snapshot_id: str | None = None


@dataclass(frozen=True)
class DenominatorContract:
    provider_returned: int
    normalized: int
    active: int
    strict_match: int
    unverifiable: int
    no_match: int
    conflict: int


@dataclass(frozen=True)
class CurrentResultContract:
    active_as_of: str
    denominators: DenominatorContract


@dataclass(frozen=True)
class TrendMetric:
    name: str
    unit: str = "postings"


@dataclass(frozen=True)
class TrendComparison:
    signature: tuple[str, ...]
    eligible: bool
    reason: str | None = None


def normalize_tree_selection(value: Mapping[str, Any]) -> SelectionProfile:
    selections = value.get("selections", {})
    if not isinstance(selections, Mapping):
        raise ValueError("tree selections must be an object")
    mode_value = value.get("mode") or (
        "job_trend" if value.get("purpose") == "job_trends" else "current_job"
    )
    try:
        mode = QueryMode(str(mode_value))
    except ValueError as error:
        raise ValueError("mode must be current_job or job_trend") from error
    return SelectionProfile(
        mode=mode,
        purpose=str(value.get("purpose") or mode.value),
        selections=tuple(
            sorted(
                (
                    (str(key), str(item))
                    for key, item in selections.items()
                    if item not in (None, "")
                )
            )
        ),
        snapshot_id=str(value["snapshot_id"]) if value.get("snapshot_id") else None,
    )


def validate_facet_selection(
    selection: SelectionProfile, available: Mapping[str, Iterable[str]]
) -> None:
    for field, value in selection.selections:
        candidates = {str(item) for item in available.get(field, ())}
        if candidates and value not in candidates:
            raise ValueError(f"invalid_selection:{field}")


def parse_query_profile(value: Mapping[str, Any]) -> CurrentJobQuery | JobTrendQuery:
    selection = normalize_tree_selection(value)
    profile = dict(value.get("profile") or {})
    if selection.mode == QueryMode.CURRENT_JOB:
        return CurrentJobQuery(
            profile, selection.snapshot_id, value.get("active_as_of")
        )
    metric = str(value.get("metric") or "active_postings")
    return JobTrendQuery(
        profile,
        metric,
        value.get("period_start"),
        value.get("period_end"),
        tuple(value.get("comparison_signature") or ()),
    )
