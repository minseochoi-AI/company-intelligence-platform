from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import AtomicFieldContract, FacetAvailability, ProviderHealth, SourcePolicy

REQUIRED_OPERATION_KEYS = {
    "operation_id", "provider", "regions", "access_mode", "data_role", "required_paths",
    "field_semantics", "activation_policy", "quota", "license", "last_verified",
}


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


def _policy(value: dict[str, Any]) -> SourcePolicy:
    missing = REQUIRED_OPERATION_KEYS - set(value)
    if missing:
        raise ValueError(f"source catalog operation is missing: {', '.join(sorted(missing))}")
    semantics = value["field_semantics"]
    if not isinstance(semantics, dict) or not semantics:
        raise ValueError(f"{value.get('operation_id')}: field_semantics must be a non-empty object")
    return SourcePolicy(
        operation_id=str(value["operation_id"]), provider=str(value["provider"]),
        regions=tuple(str(item) for item in value["regions"]), access_mode=str(value["access_mode"]),
        data_role=str(value["data_role"]), required_paths=tuple(str(item) for item in value["required_paths"]),
        field_contracts=tuple(
            AtomicFieldContract(
                key,
                str(mapped.get("internal_field", key)) if isinstance(mapped, dict) else str(mapped),
                str(mapped.get("meaning", mapped.get("internal_field", key))) if isinstance(mapped, dict) else str(mapped),
            )
            for key, mapped in semantics.items()
        ),
        activation_policy=str(value["activation_policy"]), secret_env=value.get("secret_env"),
        quota=str(value["quota"]), license=str(value["license"]), last_verified=str(value["last_verified"]),
        semantic_contract=tuple(str(item) for item in value.get("semantic_contract", ())),
        provider_disposition=str(value.get("provider_disposition", "production")),
    )


def load_source_catalog(path: Path) -> SourceCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    operations = payload.get("atomic_operations")
    if not isinstance(operations, list):
        raise TypeError("source catalog requires atomic_operations")
    return SourceCatalog(str(payload.get("schema_version", "")), tuple(_policy(item) for item in operations))


def validate_atomic_contract(catalog: SourceCatalog, expected_operation_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    ids = [item.operation_id for item in catalog.operations]
    if len(ids) != len(set(ids)):
        errors.append("duplicate operation_id")
    for operation in catalog.operations:
        if not operation.required_paths:
            errors.append(f"{operation.operation_id}: required_paths is empty")
        if not operation.field_contracts:
            errors.append(f"{operation.operation_id}: field semantics is empty")
        if operation.access_mode == "registered-key" and not operation.secret_env:
            errors.append(f"{operation.operation_id}: registered-key requires secret_env")
        if operation.provider_disposition not in {"production", "metadata_only", "context_only", "proxy_only", "candidate_pending_semantic_validation", "rejected"}:
            errors.append(f"{operation.operation_id}: invalid provider_disposition")
    if expected_operation_ids is not None and set(ids) != expected_operation_ids:
        errors.append("catalog operation IDs do not match registered probes")
    return errors


_NATIVE_FIELD_CAPABILITIES: dict[str, tuple[tuple[str, str, str, str | None], ...]] = {
    # These are *semantic boundaries*, not an assertion that every saved board
    # snapshot contains the field.  The dynamic facet builder lowers declared
    # availability to unavailable when a snapshot has no usable values.
    "greenhouse": (
        ("country_code", "filterable", "not_sortable", None),
        ("location_raw", "filterable", "not_sortable", "Location is board text, not a normalized geocode."),
        ("workplace_type", "filterable", "not_sortable", "Derived only from explicit or clearly marked board location text."),
        ("posting_language", "filterable", "not_sortable", None),
        ("salary", "filterable", "not_sortable", "Only structured pay ranges with currency and interval are comparable."),
        ("company_type", "forbidden", "not_sortable", "Greenhouse board responses do not establish legal form or ownership."),
    ),
    "lever": (
        ("country_code", "filterable", "not_sortable", None),
        ("location_raw", "filterable", "not_sortable", "Location is board text, not a normalized geocode."),
        ("workplace_type", "filterable", "not_sortable", None),
        ("employment_type", "filterable", "not_sortable", "Commitment is preserved separately when it cannot be normalized."),
        ("salary", "filterable", "not_sortable", "Only structured salaryRange values with a shared signature are comparable."),
        ("company_type", "forbidden", "not_sortable", "Lever posting data does not establish legal form or ownership."),
    ),
    "mpm_public_employment": (
        ("country_code", "filterable", "not_sortable", None),
        ("posting_organization_unit", "display_only", "not_sortable", "Institution names are not identity-resolved companies."),
        ("public_employment_type_code", "display_only", "not_sortable", "A codebook mapping has not been verified."),
        ("salary", "forbidden", "not_sortable", "The list response has no verified salary field."),
        ("location", "forbidden", "not_sortable", "The list response has no verified location field."),
        ("requirements", "forbidden", "not_sortable", "The list response has no verified qualification field."),
    ),
    "mpsv_cz": (
        ("country_code", "filterable", "not_sortable", None),
        ("occupation_code", "filterable", "not_sortable", "Use only within the CZ-ISCO namespace."),
        ("salary", "filterable", "not_sortable", "Currency, period, and basis must be retained for comparison."),
    ),
    "ares": (
        ("legal_form", "filterable", "not_sortable", "Use only within the ARES legal-form namespace."),
        ("industry", "filterable", "not_sortable", "Use only within the CZ-NACE namespace."),
        ("ownership_sector", "forbidden", "not_sortable", "ARES legal form is not an ownership classification."),
    ),
    "gleif": (
        ("legal_form", "filterable", "not_sortable", "Use only within the GLEIF legal-form namespace."),
        ("legal_entity_status", "display_only", "not_sortable", "Legal entity status is not a market-listing status."),
        ("ownership_sector", "forbidden", "not_sortable", "GLEIF legal entity metadata does not establish ownership."),
    ),
    "sec": (
        ("industry", "filterable", "not_sortable", "Use SEC SIC codes and descriptions as a separate namespace."),
        ("listing_venue", "display_only", "not_sortable", "An exchange value does not prove current market status."),
        ("market_status", "forbidden", "not_sortable", "SEC submissions does not supply a verified current market-status field."),
    ),
    "alioplus": (
        ("ownership_sector", "display_only", "not_sortable", "ALIO Plus is public-institution context, not a company ownership registry."),
        ("public_institution_type", "filterable", "not_sortable", "Use only within the ALIO Plus type namespace."),
        ("industry", "forbidden", "not_sortable", "ALIO program and facility names are not industry classifications."),
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
    for field_name, filterability, sortability, reason in _NATIVE_FIELD_CAPABILITIES.get(policy.provider, ()):
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
    return tuple(capabilities[name] for name in sorted(capabilities))


def evaluate_activation(operation: SourcePolicy, environment: dict[str, str]) -> ProviderHealth:
    if operation.secret_env and not environment.get(operation.secret_env):
        return ProviderHealth(operation.operation_id, "waiting-credential", f"{operation.secret_env} is not configured")
    if operation.activation_policy == "user-agent-required":
        value = environment.get("SEC_USER_AGENT", "").strip()
        if not value or "your-real-email" in value or "@" not in value:
            return ProviderHealth(operation.operation_id, "waiting-configuration", "SEC_USER_AGENT must identify a reachable operator")
    if operation.provider_disposition == "rejected":
        return ProviderHealth(operation.operation_id, "rejected", "Operation is explicitly excluded from production routing")
    if operation.provider_disposition in {"metadata_only", "context_only", "proxy_only", "candidate_pending_semantic_validation"}:
        return ProviderHealth(operation.operation_id, operation.provider_disposition, "Configured but limited to its declared semantic scope")
    if operation.activation_policy.endswith("http-only"):
        return ProviderHealth(operation.operation_id, "ready-with-http-boundary", "HTTP-only source; do not send personal search data")
    return ProviderHealth(operation.operation_id, "ready", "catalog contract is configured")
