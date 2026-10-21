"""Canonical responsibility owner; migrated from src/company_intel/source_catalog.py."""

from __future__ import annotations
from cil_contracts.facts import AtomicFieldContract
from cil_contracts.facts import FacetAvailability
from cil_contracts.facts import ProviderHealth
from cil_contracts.facts import SourcePolicy
from cil_contracts.providers import SourceCatalog


def validate_atomic_contract(
    catalog: SourceCatalog, expected_operation_ids: set[str] | None = None
) -> list[str]:
    errors: list[str] = []
    ids = [item.operation_id for item in catalog.operations]
    if len(ids) != len(set(ids)):
        errors.append("duplicate operation_id")
    for operation in catalog.operations:
        if not operation.required_paths:
            errors.append(f"{operation.operation_id}: required_paths is empty")
        if not operation.field_contracts:
            errors.append(f"{operation.operation_id}: field semantics is empty")
        if operation.access_mode == "registered-key" and (not operation.secret_env):
            errors.append(
                f"{operation.operation_id}: registered-key requires secret_env"
            )
        if operation.provider_disposition not in {
            "production",
            "metadata_only",
            "context_only",
            "proxy_only",
            "candidate_pending_semantic_validation",
            "rejected",
        }:
            errors.append(f"{operation.operation_id}: invalid provider_disposition")
    if expected_operation_ids is not None and set(ids) != expected_operation_ids:
        errors.append("catalog operation IDs do not match registered probes")
    return errors


def evaluate_activation(
    operation: SourcePolicy, environment: dict[str, str]
) -> ProviderHealth:
    if operation.secret_env and (not environment.get(operation.secret_env)):
        return ProviderHealth(
            operation.operation_id,
            "waiting-credential",
            f"{operation.secret_env} is not configured",
        )
    if operation.activation_policy == "user-agent-required":
        value = environment.get("SEC_USER_AGENT", "").strip()
        if not value or "your-real-email" in value or "@" not in value:
            return ProviderHealth(
                operation.operation_id,
                "waiting-configuration",
                "SEC_USER_AGENT must identify a reachable operator",
            )
    if operation.provider_disposition == "rejected":
        return ProviderHealth(
            operation.operation_id,
            "rejected",
            "Operation is explicitly excluded from production routing",
        )
    if operation.provider_disposition in {
        "metadata_only",
        "context_only",
        "proxy_only",
        "candidate_pending_semantic_validation",
    }:
        return ProviderHealth(
            operation.operation_id,
            operation.provider_disposition,
            "Configured but limited to its declared semantic scope",
        )
    if operation.activation_policy.endswith("http-only"):
        return ProviderHealth(
            operation.operation_id,
            "ready-with-http-boundary",
            "HTTP-only source; do not send personal search data",
        )
    return ProviderHealth(
        operation.operation_id, "ready", "catalog contract is configured"
    )
