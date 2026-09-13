"""Provider-native taxonomy extraction for company and posting records.

The module records what a provider actually says.  It does not try to turn a
legal-form code into ownership, an ATS department into an industry, or a
listing venue into a current market status.  Any future crosswalk belongs in a
separate, explicitly versioned mapping with its own evidence.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import TaxonomyFact
from .normalization import resolve_field_path


TAXONOMY_AXES = (
    "ownership_sector",
    "public_institution_type",
    "legal_form",
    "industry",
    "market_status",
    "posting_organization_unit",
    # Provider-native axes that must not be silently promoted to one of the
    # common axes above.
    "legal_entity_status",
    "entity_category",
    "filing_entity_type",
    "listing_venue",
    "public_institution_group",
    "public_business_name",
    "public_employment_type_code",
    "posting_office",
)


def _first(record: dict[str, Any], *paths: str) -> tuple[str | None, Any]:
    for path in paths:
        value = resolve_field_path(record, path)
        if value not in (None, "", [], {}):
            return path, value
    return None, None


def _values(value: Any) -> tuple[Any, ...]:
    if isinstance(value, list):
        return tuple(item for item in value if item not in (None, "", [], {}))
    return (value,) if value not in (None, "", [], {}) else ()


def _native_value(value: Any) -> str | None:
    """Extract an identifier from a provider value without translating it."""

    if isinstance(value, dict):
        for key in ("id", "code", "kod", "value", "name", "nazev"):
            nested = value.get(key)
            if nested not in (None, ""):
                return str(nested)
        return None
    return str(value).strip() or None


def _entity_id(provider: str, record: dict[str, Any], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    existing = record.get("entity_id")
    if existing not in (None, ""):
        return str(existing)
    identifiers = {
        "ares": ("ico", "ICO"),
        "gleif": ("id", "data.0.id"),
        "sec": ("cik", "CIK"),
        "alioplus": ("apbaId", "apba_id"),
    }
    prefix = {"ares": "ICO", "gleif": "LEI", "sec": "CIK", "alioplus": "ALIO"}
    path, value = _first(record, *identifiers.get(provider, ()))
    native = _native_value(value)
    return f"{prefix[provider]}:{native}" if path and native and provider in prefix else None


def _add(
    facts: list[TaxonomyFact],
    *,
    semantic_field: str,
    value: Any,
    namespace: str,
    provider: str,
    raw_field: str,
    raw_value: Any,
    entity_id: str | None,
    source_record_id: str | None,
    evidence_status: str = "observed",
    filterability: str = "filterable",
    sortability: str = "not_sortable",
) -> None:
    native = _native_value(value)
    if native is None:
        return
    fact = TaxonomyFact(
        semantic_field=semantic_field,
        value=native,
        namespace=namespace,
        provider=provider,
        raw_field=raw_field,
        raw_value=raw_value,
        entity_id=entity_id,
        source_record_id=source_record_id,
        evidence_status=evidence_status,
        filterability=filterability,
        sortability=sortability,
    )
    if fact not in facts:
        facts.append(fact)


def _add_many(
    facts: list[TaxonomyFact],
    *,
    semantic_field: str,
    field_path: str | None,
    value: Any,
    namespace: str,
    provider: str,
    entity_id: str | None,
    source_record_id: str | None,
    evidence_status: str = "observed",
    filterability: str = "filterable",
) -> None:
    if field_path is None:
        return
    for item in _values(value):
        _add(
            facts,
            semantic_field=semantic_field,
            value=item,
            namespace=namespace,
            provider=provider,
            raw_field=field_path,
            raw_value=item,
            entity_id=entity_id,
            source_record_id=source_record_id,
            evidence_status=evidence_status,
            filterability=filterability,
        )


def _ares_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    form_path, form = _first(record, "pravniForma", "pravniFormaRos", "dalsiUdaje.0.pravniForma", "dalsiUdaje.0.pravniFormaRos")
    _add_many(
        facts, semantic_field="legal_form", field_path=form_path, value=form,
        namespace="ARES:pravniForma", provider="ares", entity_id=entity_id, source_record_id=source_record_id,
    )
    nace_path, nace = _first(record, "czNace", "czNace2008", "dalsiUdaje.0.czNace", "dalsiUdaje.0.czNace2008")
    _add_many(
        facts, semantic_field="industry", field_path=nace_path, value=nace,
        namespace="CZ-NACE", provider="ares", entity_id=entity_id, source_record_id=source_record_id,
    )


def _gleif_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    form_path, form = _first(record, "attributes.entity.legalForm.id", "entity.legalForm.id", "legalForm.id", "data.0.attributes.entity.legalForm.id")
    _add_many(
        facts, semantic_field="legal_form", field_path=form_path, value=form,
        namespace="GLEIF:ELF", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
    )
    status_path, status = _first(record, "attributes.entity.status", "entity.status", "status", "data.0.attributes.entity.status")
    _add_many(
        facts, semantic_field="legal_entity_status", field_path=status_path, value=status,
        namespace="GLEIF:entity.status", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    category_path, category = _first(record, "attributes.entity.category", "entity.category", "category", "data.0.attributes.entity.category")
    _add_many(
        facts, semantic_field="entity_category", field_path=category_path, value=category,
        namespace="GLEIF:entity.category", provider="gleif", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )


def _sec_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    sic_path, sic = _first(record, "sic", "sic_code")
    _add_many(
        facts, semantic_field="industry", field_path=sic_path, value=sic,
        namespace="SEC:SIC", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
    )
    entity_type_path, entity_type = _first(record, "entityType", "entity_type")
    _add_many(
        facts, semantic_field="filing_entity_type", field_path=entity_type_path, value=entity_type,
        namespace="SEC:entityType", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    exchange_path, exchange = _first(record, "exchanges", "exchange")
    _add_many(
        facts, semantic_field="listing_venue", field_path=exchange_path, value=exchange,
        namespace="SEC:exchange", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    # Only an explicitly named market status becomes that axis.  An exchange
    # and a filing entity type are intentionally not substitutes for it.
    market_path, market = _first(record, "marketStatus", "market_status")
    _add_many(
        facts, semantic_field="market_status", field_path=market_path, value=market,
        namespace="SEC:marketStatus", provider="sec", entity_id=entity_id, source_record_id=source_record_id,
    )


def _alio_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    # ALIO Plus is an official public-institution context source.  It supports
    # a contextual sector fact but does not establish a legal form or industry.
    _add(
        facts, semantic_field="ownership_sector", value="public_institution",
        namespace="ALIO:source_scope", provider="alioplus", raw_field="provider_scope",
        raw_value="public_institution_context", entity_id=entity_id, source_record_id=source_record_id,
        evidence_status="provider_context", filterability="display_only",
    )
    type_path, institution_type = _first(record, "apbaTypeNa", "apba_type_name")
    _add_many(
        facts, semantic_field="public_institution_type", field_path=type_path, value=institution_type,
        namespace="ALIO:apbaTypeNa", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
    )
    group_path, group = _first(record, "apbaGb", "apba_group")
    _add_many(
        facts, semantic_field="public_institution_group", field_path=group_path, value=group,
        namespace="ALIO:apbaGb", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )
    business_path, business = _first(record, "bsnNa", "business_name")
    _add_many(
        facts, semantic_field="public_business_name", field_path=business_path, value=business,
        namespace="ALIO:bsnNa", provider="alioplus", entity_id=entity_id, source_record_id=source_record_id,
        filterability="display_only",
    )


def _mpm_facts(record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    _add(
        facts, semantic_field="ownership_sector", value="public_sector_employer",
        namespace="MPM:source_scope", provider="mpm_public_employment", raw_field="provider_scope",
        raw_value="public_employment_listing", entity_id=entity_id, source_record_id=source_record_id,
        evidence_status="provider_context", filterability="display_only",
    )
    organization_path, organization = _first(record, "institution_name", "insttname", "institutionName")
    _add_many(
        facts, semantic_field="posting_organization_unit", field_path=organization_path, value=organization,
        namespace="MPM:institution_name", provider="mpm_public_employment", entity_id=entity_id,
        source_record_id=source_record_id, evidence_status="unresolved_identity", filterability="display_only",
    )
    for path in ("type01", "type02", "posting_type"):
        value = resolve_field_path(record, path)
        _add_many(
            facts, semantic_field="public_employment_type_code", field_path=path, value=value,
            namespace=f"MPM:{path}", provider="mpm_public_employment", entity_id=entity_id,
            source_record_id=source_record_id, evidence_status="codebook_unverified", filterability="display_only",
        )


def _ats_facts(provider: str, record: dict[str, Any], facts: list[TaxonomyFact], entity_id: str | None, source_record_id: str | None) -> None:
    if provider == "greenhouse":
        departments = resolve_field_path(record, "departments")
        if departments is not None:
            for department in _values(departments):
                name = department.get("name") if isinstance(department, dict) else department
                _add(
                    facts, semantic_field="posting_organization_unit", value=name,
                    namespace="ATS:GREENHOUSE:department", provider=provider, raw_field="departments",
                    raw_value=department, entity_id=entity_id, source_record_id=source_record_id,
                    evidence_status="posting_scope",
                )
        offices = resolve_field_path(record, "offices")
        if offices is not None:
            for office in _values(offices):
                location = office.get("location") if isinstance(office, dict) else office
                _add(
                    facts, semantic_field="posting_office", value=location,
                    namespace="ATS:GREENHOUSE:office", provider=provider, raw_field="offices",
                    raw_value=office, entity_id=entity_id, source_record_id=source_record_id,
                    evidence_status="posting_scope",
                )
    elif provider == "lever":
        for path in ("categories.team", "categories.department"):
            value = resolve_field_path(record, path)
            _add_many(
                facts, semantic_field="posting_organization_unit", field_path=path, value=value,
                namespace=f"ATS:LEVER:{path.rsplit('.', 1)[-1]}", provider=provider, entity_id=entity_id,
                source_record_id=source_record_id, evidence_status="posting_scope",
            )


def taxonomy_facts_from_record(
    provider: str,
    record: dict[str, Any],
    *,
    entity_id: str | None = None,
    source_record_id: str | None = None,
) -> tuple[TaxonomyFact, ...]:
    """Extract facts from one saved provider record without joining entities.

    ``provider`` selects the source-specific contract.  Unknown providers
    return no facts rather than guessing at the meaning of similarly named
    fields.  This makes a newly added provider opt-in by design.
    """

    normalized_provider = provider.casefold().strip()
    aliases = {
        "mpm": "mpm_public_employment",
        "mpm_public_employment_list": "mpm_public_employment",
        "alio": "alioplus",
        "alio_plus": "alioplus",
    }
    normalized_provider = aliases.get(normalized_provider, normalized_provider)
    if not isinstance(record, dict):
        return ()

    resolved_entity = _entity_id(normalized_provider, record, entity_id)
    resolved_record_id = source_record_id or _native_value(
        resolve_field_path(record, "id")
        or resolve_field_path(record, "idx")
        or resolve_field_path(record, "posting_id")
    )
    facts: list[TaxonomyFact] = []
    if normalized_provider == "ares":
        _ares_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "gleif":
        _gleif_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "sec":
        _sec_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "alioplus":
        _alio_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider == "mpm_public_employment":
        _mpm_facts(record, facts, resolved_entity, resolved_record_id)
    elif normalized_provider in {"greenhouse", "lever"}:
        _ats_facts(normalized_provider, record, facts, resolved_entity, resolved_record_id)
    return tuple(facts)


def taxonomy_facts_from_records(provider: str, records: Iterable[dict[str, Any]]) -> tuple[TaxonomyFact, ...]:
    """Convenience helper that keeps each source record separate."""

    return tuple(fact for record in records for fact in taxonomy_facts_from_record(provider, record))
