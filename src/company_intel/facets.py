"""Snapshot-scoped facet contracts for the interactive and scriptable CLI.

Facet counts describe the supplied saved records only.  They are never market
coverage estimates, and a disabled option is intentionally retained when it
helps explain why a requested filter cannot be evaluated.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .models import FacetAvailability, TaxonomyFact
from .taxonomy import taxonomy_facts_from_record


@dataclass(frozen=True)
class FacetDefinition:
    semantic_field: str
    scope: str
    display_label: str
    vocabulary_namespace: str
    raw_fields: tuple[str, ...]
    filterability: str
    sortability: str
    comparability_requirements: tuple[str, ...] = ()
    unavailable_reason: str | None = None


@dataclass(frozen=True)
class FacetOption:
    """A value users may inspect or select from a saved-snapshot facet list."""

    semantic_field: str
    scope: str
    normalized_value: str
    display_label: str
    vocabulary_namespace: str
    provider: tuple[str, ...]
    raw_field: tuple[str, ...]
    record_count: int
    coverage_ratio: float
    filterability: str
    sortability: str
    comparability_requirements: tuple[str, ...]
    evidence_status: str
    disabled_reason: str | None = None

    @property
    def selectable(self) -> bool:
        return self.filterability == "filterable" and self.disabled_reason is None

    def as_dict(self) -> dict[str, Any]:
        """Return a stable JSON-ready representation for CLI and API callers."""

        providers = list(self.provider)
        raw_fields = list(self.raw_field)
        return {
            "semantic_field": self.semantic_field,
            "scope": self.scope,
            "normalized_value": self.normalized_value,
            "display_label": self.display_label,
            "vocabulary_namespace": self.vocabulary_namespace,
            "provider": providers,
            "providers": providers,
            "raw_field": raw_fields,
            "raw_fields": raw_fields,
            "record_count": self.record_count,
            "coverage_ratio": self.coverage_ratio,
            "filterability": self.filterability.replace("_", "-"),
            "sortability": self.sortability,
            "comparability_requirements": list(self.comparability_requirements),
            "evidence_status": self.evidence_status,
            "disabled_reason": self.disabled_reason,
            "selectable": self.selectable,
        }


_JOB_DEFINITIONS: tuple[FacetDefinition, ...] = (
    FacetDefinition("country_code", "job", "Country", "ISO-3166-1", ("country_code",), "filterable", "not_sortable"),
    FacetDefinition("occupation_label", "job", "Job title / occupation", "provider:title", ("occupation_label", "title_raw"), "filterable", "not_sortable"),
    FacetDefinition("location", "job", "Location", "provider:location", ("location_raw", "city", "region"), "filterable", "not_sortable"),
    FacetDefinition("workplace_type", "job", "Workplace type", "company-intel:workplace", ("workplace_type",), "filterable", "not_sortable"),
    FacetDefinition("employment_type", "job", "Employment type", "company-intel:employment", ("employment_type",), "filterable", "not_sortable"),
    FacetDefinition("employment_commitment_raw", "job", "Provider commitment text", "provider:commitment", ("employment_type_raw",), "display_only", "not_sortable", unavailable_reason="Raw provider commitment is not safely equivalent to a normalized employment type."),
    FacetDefinition("posting_language", "job", "Posting language", "BCP-47-or-provider-text", ("posting_language",), "filterable", "not_sortable"),
    FacetDefinition("business_unit", "job", "Posting business unit", "ATS:posting-unit", ("business_unit", "_department_text"), "filterable", "not_sortable", unavailable_reason="A posting department is only a job-level business-unit filter; it is not a company industry or legal classification."),
    FacetDefinition("industry", "job", "Posting industry", "provider:industry", ("industry_raw",), "display_only", "not_sortable", unavailable_reason="ATS industry text is not a verified company industry classification."),
    FacetDefinition("company_type", "job", "Company type", "provider:company_type", ("company_type",), "forbidden", "not_sortable", unavailable_reason="A job-board company_type does not establish legal form, ownership, or public status. Use taxonomy facts instead."),
    FacetDefinition("salary_signature", "job", "Structured salary signature", "currency/period/basis", ("salary_min", "salary_max", "salary_currency", "salary_period", "salary_basis"), "filterable", "sortable", ("currency", "period", "basis"), "Only structured salary values with currency, period, and basis can be compared or sorted."),
)

_TAXONOMY_DEFINITIONS: dict[str, FacetDefinition] = {
    "ownership_sector": FacetDefinition("ownership_sector", "taxonomy", "Ownership / public sector", "provider-native:ownership", ("provider_scope",), "filterable", "not_sortable"),
    "public_institution_type": FacetDefinition("public_institution_type", "taxonomy", "Public institution type", "provider-native:public-institution", ("apbaTypeNa",), "filterable", "not_sortable"),
    "legal_form": FacetDefinition("legal_form", "taxonomy", "Legal form", "provider-native:legal-form", ("pravniForma", "legalForm.id"), "filterable", "not_sortable"),
    "industry": FacetDefinition("industry", "taxonomy", "Industry classification", "provider-native:industry", ("czNace", "sic"), "filterable", "not_sortable"),
    "market_status": FacetDefinition("market_status", "taxonomy", "Market status", "provider-native:market-status", ("marketStatus",), "filterable", "not_sortable"),
    "posting_organization_unit": FacetDefinition("posting_organization_unit", "taxonomy", "Posting organization unit", "provider-native:posting-unit", ("departments", "categories.team", "institution_name"), "display_only", "not_sortable", unavailable_reason="A posting unit or institution name is not an identity-resolved company."),
}


def facet_definitions(scope: str | None = None) -> tuple[FacetDefinition, ...]:
    """Return static field contracts used to render an interactive selector."""

    definitions = (*_JOB_DEFINITIONS, *_TAXONOMY_DEFINITIONS.values())
    return tuple(item for item in definitions if scope is None or item.scope == scope)


def _records(rows: Iterable[Any] | Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    to_dict = getattr(rows, "to_dict", None)
    if callable(to_dict):
        try:
            converted = to_dict("records")
        except (TypeError, ValueError):
            converted = None
        if isinstance(converted, list):
            return [item for item in converted if isinstance(item, dict)]
    if isinstance(rows, dict):
        nested = rows.get("rows")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
        return [rows]
    return [item for item in rows if isinstance(item, dict)]


def _present(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, str) and value.casefold() in {"unknown", "unavailable", "n/a"}:
        return False
    return True


def _text_value(record: dict[str, Any], definition: FacetDefinition) -> str | None:
    values = [record.get(field) for field in definition.raw_fields if _present(record.get(field))]
    if not values:
        return None
    return " | ".join(str(value).strip() for value in values)


def _evidence_status(*, count: int, total: int, disabled: bool) -> str:
    if disabled:
        return "unavailable"
    if not count:
        return "unavailable"
    return "observed" if count == total else "partial_snapshot_coverage"


def _job_options(records: list[dict[str, Any]], definition: FacetDefinition) -> list[FacetOption]:
    total = len(records)
    by_value: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if definition.semantic_field == "salary_signature":
        for record in records:
            min_value = record.get("salary_min")
            max_value = record.get("salary_max")
            currency = record.get("salary_currency")
            period = record.get("salary_period")
            basis = record.get("salary_basis")
            if not (_present(min_value) or _present(max_value)) or not all(_present(value) for value in (currency, period, basis)):
                continue
            signature = f"{currency}/{period}/{basis}"
            by_value[signature].append(record)
    else:
        for record in records:
            value = _text_value(record, definition)
            if value is not None:
                by_value[value].append(record)

    all_providers = tuple(sorted({str(record.get("provider", "unknown")) for record in records}))
    if not by_value:
        reason = definition.unavailable_reason or "No usable value exists in the supplied saved snapshot."
        return [
            FacetOption(
                semantic_field=definition.semantic_field,
                scope=definition.scope,
                normalized_value="__unavailable__",
                display_label=f"{definition.display_label}: unavailable",
                vocabulary_namespace=definition.vocabulary_namespace,
                provider=all_providers,
                raw_field=definition.raw_fields,
                record_count=0,
                coverage_ratio=0.0,
                filterability="display_only" if definition.filterability == "filterable" else definition.filterability,
                sortability="not_sortable",
                comparability_requirements=definition.comparability_requirements,
                evidence_status="unavailable",
                disabled_reason=reason,
            )
        ]

    options: list[FacetOption] = []
    for value, matching_records in sorted(by_value.items(), key=lambda item: (-len(item[1]), item[0].casefold())):
        providers = tuple(sorted({str(record.get("provider", "unknown")) for record in matching_records}))
        disabled = definition.filterability != "filterable"
        options.append(
            FacetOption(
                semantic_field=definition.semantic_field,
                scope=definition.scope,
                normalized_value=value,
                display_label=value,
                vocabulary_namespace=definition.vocabulary_namespace,
                provider=providers,
                raw_field=definition.raw_fields,
                record_count=len(matching_records),
                coverage_ratio=(len(matching_records) / total) if total else 0.0,
                filterability=definition.filterability,
                sortability=definition.sortability,
                comparability_requirements=definition.comparability_requirements,
                evidence_status=_evidence_status(count=len(matching_records), total=total, disabled=disabled),
                disabled_reason=definition.unavailable_reason if disabled else None,
            )
        )
    return options


def build_job_facets(jobs: Iterable[Any] | Any) -> list[dict[str, Any]]:
    """Build JSON-ready job facet options from normalized saved job rows.

    Unknown-only fields produce a disabled explanatory row instead of becoming
    a selectable ``unknown`` filter.  Salary options are exposed by a complete
    currency/period/basis signature, never by prose compensation text.
    """

    records = _records(jobs)
    options = [
        option
        for definition in _JOB_DEFINITIONS
        for option in _job_options(records, definition)
    ]
    return [option.as_dict() for option in options]


def _taxonomy_facts(records: Iterable[Any] | Any) -> tuple[TaxonomyFact, ...]:
    facts: list[TaxonomyFact] = []
    if records is None:
        return ()
    if isinstance(records, TaxonomyFact):
        return (records,)
    to_dict = getattr(records, "to_dict", None)
    if callable(to_dict):
        try:
            converted = to_dict("records")
        except (TypeError, ValueError):
            converted = None
        if isinstance(converted, list):
            records = converted
    iterable: Iterable[Any]
    if isinstance(records, dict):
        iterable = (records,)
    else:
        iterable = records
    for item in iterable:
        if isinstance(item, TaxonomyFact):
            facts.append(item)
            continue
        if not isinstance(item, dict):
            continue
        nested = item.get("taxonomy_facts")
        if isinstance(nested, (list, tuple)):
            facts.extend(fact for fact in nested if isinstance(fact, TaxonomyFact))
            continue
        provider = item.get("provider")
        if isinstance(provider, str):
            facts.extend(taxonomy_facts_from_record(provider, item))
    return tuple(facts)


def _fact_token(fact: TaxonomyFact) -> str:
    return "|".join(
        (
            fact.provider,
            fact.source_record_id or fact.entity_id or "unidentified",
            fact.raw_field,
            repr(fact.raw_value),
        )
    )


def build_taxonomy_facets(records: Iterable[Any] | Any) -> list[dict[str, Any]]:
    """Build JSON-ready facets without merging provider-native namespaces."""

    facts = _taxonomy_facts(records)
    total_records = len({_fact_token(fact) for fact in facts})
    grouped: dict[tuple[str, str, str], list[TaxonomyFact]] = defaultdict(list)
    for fact in facts:
        grouped[(fact.semantic_field, fact.namespace, fact.value)].append(fact)

    options: list[FacetOption] = []
    for (semantic_field, namespace, value), entries in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1], item[0][2].casefold())):
        definition = _TAXONOMY_DEFINITIONS.get(
            semantic_field,
            FacetDefinition(
                semantic_field, "taxonomy", semantic_field.replace("_", " ").title(),
                "provider-native", (), "display_only", "not_sortable",
                unavailable_reason="Provider-native field has no common cross-provider filter contract.",
            ),
        )
        providers = tuple(sorted({fact.provider for fact in entries}))
        raw_fields = tuple(sorted({fact.raw_field for fact in entries}))
        filterability = "filterable" if all(fact.filterability == "filterable" for fact in entries) else "display_only"
        reason = None if filterability == "filterable" else (definition.unavailable_reason or "The source marks this value as display-only.")
        options.append(
            FacetOption(
                semantic_field=semantic_field,
                scope="taxonomy",
                normalized_value=value,
                display_label=value,
                vocabulary_namespace=namespace,
                provider=providers,
                raw_field=raw_fields,
                record_count=len(entries),
                coverage_ratio=(len({_fact_token(fact) for fact in entries}) / total_records) if total_records else 0.0,
                filterability=filterability,
                sortability="not_sortable",
                comparability_requirements=("same provider-native namespace",),
                evidence_status="observed" if all(fact.evidence_status == "observed" for fact in entries) else "provider_scoped",
                disabled_reason=reason,
            )
        )
    return [option.as_dict() for option in options]


def field_availability(
    semantic_field: str,
    records: Iterable[Any] | Any = None,
    *,
    scope: str = "job",
) -> FacetAvailability:
    """Return a field-level availability summary suitable for a disabled UI row."""

    if scope == "job":
        definition = next((item for item in _JOB_DEFINITIONS if item.semantic_field == semantic_field), None)
        options = build_job_facets(records) if records is not None else []
    elif scope == "taxonomy":
        definition = _TAXONOMY_DEFINITIONS.get(semantic_field)
        options = build_taxonomy_facets(records) if records is not None else []
    else:
        definition = None
        options = []
    matching = [option for option in options if option["semantic_field"] == semantic_field]
    if definition is None:
        return FacetAvailability(
            semantic_field=semantic_field,
            scope=scope,
            filterability="forbidden",
            sortability="not_sortable",
            record_count=0,
            coverage_ratio=0.0,
            evidence_status="unavailable",
            unavailable_reason="No semantic field contract is registered for this scope.",
        )
    provider_names = tuple(sorted({provider for option in matching for provider in option["provider"]}))
    count = sum(int(option["record_count"]) for option in matching if option["normalized_value"] != "__unavailable__")
    coverage = max((float(option["coverage_ratio"]) for option in matching), default=0.0)
    selectable = any(bool(option["selectable"]) for option in matching)
    reason = None if selectable else next((option["disabled_reason"] for option in matching if option["disabled_reason"]), definition.unavailable_reason)
    return FacetAvailability(
        semantic_field=semantic_field,
        scope=scope,
        filterability="filterable" if selectable else (definition.filterability if definition.filterability != "filterable" else "display_only"),
        sortability=definition.sortability if selectable else "not_sortable",
        record_count=count,
        coverage_ratio=coverage,
        evidence_status="observed" if selectable and coverage == 1.0 else ("partial_snapshot_coverage" if selectable else "unavailable"),
        providers=provider_names,
        unavailable_reason=reason,
    )


def identity_link_status(records: Iterable[Any] | Any) -> list[dict[str, Any]]:
    """Expose linkage state without promoting name candidates to entity links."""

    values = _records(records)
    counts: dict[str, int] = {}
    for row in values:
        status = str(row.get("identity_link_status") or row.get("identity_status") or "unresolved")
        counts[status] = counts.get(status, 0) + 1
    total = len(values)
    return [
        {"semantic_field": "identity_link_status", "scope": "identity", "normalized_value": status,
         "display_label": status, "record_count": count, "coverage_ratio": count / total if total else 0.0,
         "filterability": "filterable" if status == "linked" else "display_only", "sortability": "not_sortable",
         "disabled_reason": None if status == "linked" else f"identity_{status}"}
        for status, count in sorted(counts.items())
    ]


def public_context(records: Iterable[Any] | Any) -> list[dict[str, Any]]:
    values = _records(records)
    fields = ("public_context", "institution_type_code", "legal_form", "ownership_sector")
    return [
        {"semantic_field": field, "scope": "public_identity", "record_count": sum(1 for row in values if row.get(field) not in (None, "", "unknown")),
         "coverage_ratio": facet_coverage(values, field), "filterability": "filterable" if field == "public_context" else "linked-identity-required",
         "disabled_reason": None if field == "public_context" else "identity_link_required"}
        for field in fields
    ]


def facet_count(records: Iterable[Any] | Any, field: str, value: str) -> int:
    return sum(1 for row in _records(records) if str(row.get(field) or "") == value)


def facet_coverage(records: Iterable[Any] | Any, field: str) -> float:
    values = _records(records)
    return sum(1 for row in values if row.get(field) not in (None, "", "unknown")) / len(values) if values else 0.0


def invalid_selection(records: Iterable[Any] | Any, selection: dict[str, str]) -> bool:
    return not any(all(str(row.get(field) or "") == value for field, value in selection.items()) for row in _records(records))


def facet_options_for_selection(records: Iterable[Any] | Any, selection: dict[str, str], field: str) -> list[dict[str, Any]]:
    selected = [row for row in _records(records) if all(str(row.get(key) or "") == value for key, value in selection.items())]
    counts: dict[str, int] = {}
    for row in selected:
        value = row.get(field)
        if value not in (None, "", "unknown"):
            counts[str(value)] = counts.get(str(value), 0) + 1
    if not counts:
        return [{"semantic_field": field, "normalized_value": "__unavailable__", "record_count": 0, "coverage_ratio": 0.0, "filterability": "unavailable", "disabled_reason": f"{field}_unavailable"}]
    return [{"semantic_field": field, "normalized_value": value, "record_count": count, "coverage_ratio": count / len(selected), "filterability": "filterable"} for value, count in sorted(counts.items())]
