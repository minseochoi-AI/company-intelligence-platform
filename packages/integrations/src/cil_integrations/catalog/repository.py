"""Canonical responsibility owner; migrated from src/company_intel/source_catalog.py."""

from __future__ import annotations
from cil_contracts.facts import AtomicFieldContract
from cil_contracts.facts import FacetAvailability
from cil_contracts.facts import ProviderHealth
from cil_contracts.facts import SourcePolicy
from cil_contracts.providers import SourceCatalog
from pathlib import Path
from typing import Any
import json

REQUIRED_OPERATION_KEYS = {
    "operation_id",
    "provider",
    "regions",
    "access_mode",
    "data_role",
    "required_paths",
    "field_semantics",
    "activation_policy",
    "quota",
    "license",
    "last_verified",
}


def _policy(value: dict[str, Any]) -> SourcePolicy:
    missing = REQUIRED_OPERATION_KEYS - set(value)
    if missing:
        raise ValueError(
            f"source catalog operation is missing: {', '.join(sorted(missing))}"
        )
    semantics = value["field_semantics"]
    if not isinstance(semantics, dict) or not semantics:
        raise ValueError(
            f"{value.get('operation_id')}: field_semantics must be a non-empty object"
        )
    return SourcePolicy(
        operation_id=str(value["operation_id"]),
        provider=str(value["provider"]),
        regions=tuple((str(item) for item in value["regions"])),
        access_mode=str(value["access_mode"]),
        data_role=str(value["data_role"]),
        required_paths=tuple((str(item) for item in value["required_paths"])),
        field_contracts=tuple(
            (
                AtomicFieldContract(
                    key,
                    str(mapped.get("internal_field", key))
                    if isinstance(mapped, dict)
                    else str(mapped),
                    str(mapped.get("meaning", mapped.get("internal_field", key)))
                    if isinstance(mapped, dict)
                    else str(mapped),
                )
                for key, mapped in semantics.items()
            )
        ),
        activation_policy=str(value["activation_policy"]),
        secret_env=value.get("secret_env"),
        quota=str(value["quota"]),
        license=str(value["license"]),
        last_verified=str(value["last_verified"]),
        semantic_contract=tuple(
            (str(item) for item in value.get("semantic_contract", ()))
        ),
        provider_disposition=str(value.get("provider_disposition", "production")),
        schema_version=str(value.get("schema_version", "1.0.0")),
    )


def load_source_catalog(path: Path | None = None) -> SourceCatalog:
    from importlib.resources import files

    source = (
        path
        if path is not None and path.is_file()
        else files("cil_integrations").joinpath("resources/providers.json")
    )
    payload = json.loads(source.read_text(encoding="utf-8"))
    operations = payload.get("atomic_operations")
    if not isinstance(operations, list):
        raise TypeError("source catalog requires atomic_operations")
    return SourceCatalog(
        str(payload.get("schema_version", "")),
        tuple((_policy(item) for item in operations)),
    )
