"""Canonical responsibility owner; migrated from src/company_intel/source_catalog.py."""

from __future__ import annotations
from cil_contracts.facts import AtomicFieldContract
from cil_contracts.facts import FacetAvailability
from cil_contracts.facts import ProviderHealth
from cil_contracts.facts import SourcePolicy
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceCatalog:
    schema_version: str
    operations: tuple[SourcePolicy, ...]

    def by_id(self, operation_id: str) -> SourcePolicy:
        for operation in self.operations:
            if operation.operation_id == operation_id:
                return operation
        raise KeyError(operation_id)

    def field_capabilities(self, operation_id: str) -> tuple[FacetAvailability, ...]:
        """Return declared field boundaries for one atomic provider operation."""
        return field_capabilities(self.by_id(operation_id))


_NATIVE_FIELD_CAPABILITIES: dict[str, tuple[tuple[str, str, str, str | None], ...]] = {
    "greenhouse": (
        ("country_code", "filterable", "not_sortable", None),
        (
            "location_raw",
            "filterable",
            "not_sortable",
            "Location is board text, not a normalized geocode.",
        ),
        (
            "workplace_type",
            "filterable",
            "not_sortable",
            "Derived only from explicit or clearly marked board location text.",
        ),
        ("posting_language", "filterable", "not_sortable", None),
        (
            "salary",
            "filterable",
            "not_sortable",
            "Only structured pay ranges with currency and interval are comparable.",
        ),
        (
            "company_type",
            "forbidden",
            "not_sortable",
            "Greenhouse board responses do not establish legal form or ownership.",
        ),
    ),
    "lever": (
        ("country_code", "filterable", "not_sortable", None),
        (
            "location_raw",
            "filterable",
            "not_sortable",
            "Location is board text, not a normalized geocode.",
        ),
        ("workplace_type", "filterable", "not_sortable", None),
        (
            "employment_type",
            "filterable",
            "not_sortable",
            "Commitment is preserved separately when it cannot be normalized.",
        ),
        (
            "salary",
            "filterable",
            "not_sortable",
            "Only structured salaryRange values with a shared signature are comparable.",
        ),
        (
            "company_type",
            "forbidden",
            "not_sortable",
            "Lever posting data does not establish legal form or ownership.",
        ),
    ),
    "mpm_public_employment": (
        ("country_code", "filterable", "not_sortable", None),
        (
            "posting_organization_unit",
            "display_only",
            "not_sortable",
            "Institution names are not identity-resolved companies.",
        ),
        (
            "public_employment_type_code",
            "display_only",
            "not_sortable",
            "A codebook mapping has not been verified.",
        ),
        (
            "salary",
            "forbidden",
            "not_sortable",
            "The list response has no verified salary field.",
        ),
        (
            "location",
            "forbidden",
            "not_sortable",
            "The list response has no verified location field.",
        ),
        (
            "requirements",
            "forbidden",
            "not_sortable",
            "The list response has no verified qualification field.",
        ),
    ),
    "mpsv_cz": (
        ("country_code", "filterable", "not_sortable", None),
        (
            "occupation_code",
            "filterable",
            "not_sortable",
            "Use only within the CZ-ISCO namespace.",
        ),
        (
            "salary",
            "filterable",
            "not_sortable",
            "Currency, period, and basis must be retained for comparison.",
        ),
    ),
    "ares": (
        (
            "legal_form",
            "filterable",
            "not_sortable",
            "Use only within the ARES legal-form namespace.",
        ),
        (
            "industry",
            "filterable",
            "not_sortable",
            "Use only within the CZ-NACE namespace.",
        ),
        (
            "ownership_sector",
            "forbidden",
            "not_sortable",
            "ARES legal form is not an ownership classification.",
        ),
    ),
    "gleif": (
        (
            "legal_form",
            "filterable",
            "not_sortable",
            "Use only within the GLEIF legal-form namespace.",
        ),
        (
            "legal_entity_status",
            "display_only",
            "not_sortable",
            "Legal entity status is not a market-listing status.",
        ),
        (
            "ownership_sector",
            "forbidden",
            "not_sortable",
            "GLEIF legal entity metadata does not establish ownership.",
        ),
    ),
    "sec": (
        (
            "industry",
            "filterable",
            "not_sortable",
            "Use SEC SIC codes and descriptions as a separate namespace.",
        ),
        (
            "listing_venue",
            "display_only",
            "not_sortable",
            "An exchange value does not prove current market status.",
        ),
        (
            "market_status",
            "forbidden",
            "not_sortable",
            "SEC submissions does not supply a verified current market-status field.",
        ),
    ),
    "alioplus": (
        (
            "ownership_sector",
            "display_only",
            "not_sortable",
            "ALIO Plus is public-institution context, not a company ownership registry.",
        ),
        (
            "public_institution_type",
            "filterable",
            "not_sortable",
            "Use only within the ALIO Plus type namespace.",
        ),
        (
            "industry",
            "forbidden",
            "not_sortable",
            "ALIO program and facility names are not industry classifications.",
        ),
    ),
}


def field_capabilities(policy: SourcePolicy) -> tuple[FacetAvailability, ...]:
    """Declare which provider-native fields can be offered to a consumer.

    ``filterable`` means an exact value can be filtered within the declared
    provider namespace.  It never authorizes cross-provider code comparison.
    The result is declared capability only; saved-snapshot coverage is reported
    by :mod:`company_intel.facets`.
    """
    capabilities: dict[str, FacetAvailability] = {}
    for contract in policy.field_contracts:
        capabilities[contract.internal_field] = FacetAvailability(
            semantic_field=contract.internal_field,
            scope=policy.data_role,
            filterability="display_only",
            sortability="not_sortable",
            record_count=0,
            coverage_ratio=0.0,
            evidence_status="declared",
            providers=(policy.provider,),
            unavailable_reason="Provider-native raw field needs a semantic adapter before filtering.",
        )
    for (
        field_name,
        filterability,
        sortability,
        reason,
    ) in _NATIVE_FIELD_CAPABILITIES.get(policy.provider, ()):
        capabilities[field_name] = FacetAvailability(
            semantic_field=field_name,
            scope=policy.data_role,
            filterability=filterability,
            sortability=sortability,
            record_count=0,
            coverage_ratio=0.0,
            evidence_status="declared",
            providers=(policy.provider,),
            unavailable_reason=reason if filterability != "filterable" else None,
        )
    return tuple((capabilities[name] for name in sorted(capabilities)))
