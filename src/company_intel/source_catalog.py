from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import AtomicFieldContract, ProviderHealth, SourcePolicy

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
