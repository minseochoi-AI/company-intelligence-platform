"""Versioned provider capabilities; registration does not imply live coverage."""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable
from cil_contracts.requests import content_hash


@dataclass(frozen=True)
class OperationStatus:
    operation_id: str
    provider_id: str
    schema_version: str
    capabilities: tuple[str, ...]
    fields: tuple[str, ...]
    grain: str
    rights: str
    status: str = "registered"
    authentication: str = "unknown"


class CapabilityRegistry:
    """Adapters advertise exact operations and meanings, never provider counts."""

    def __init__(self, operations: list[OperationStatus] | None = None) -> None:
        self._operations: dict[tuple[str, str], OperationStatus] = {}
        self._normalizers: dict[tuple[str, str], Callable] = {}
        for operation in operations or []:
            self.register(operation)

    def register(self, operation: OperationStatus) -> None:
        if not isinstance(operation, OperationStatus):
            raise TypeError("OperationStatus required")
        if not all(
            (
                operation.operation_id,
                operation.provider_id,
                operation.schema_version,
                operation.grain,
            )
        ):
            raise ValueError("operation identity, version and grain are required")
        if operation.status not in {
            "candidate",
            "registered",
            "ready",
            "partial",
            "auth_error",
            "error",
            "unknown",
        }:
            raise ValueError("unknown capability status")
        if operation.status == "ready" and (
            not operation.fields or operation.rights == "unknown"
        ):
            raise ValueError("ready requires fields and an explicit rights policy")
        key = operation.operation_id, operation.schema_version
        if key in self._operations:
            raise ValueError("operation/version already registered")
        self._operations[key] = operation

    @classmethod
    def from_catalog(cls, catalog: dict[str, Any]) -> CapabilityRegistry:
        rows = []
        for op in catalog.get("atomic_operations", []):
            rows.append(
                OperationStatus(
                    op["operation_id"],
                    op["provider"],
                    str(op.get("schema_version", "1.0.0")),
                    (str(op["data_role"]),),
                    tuple(op.get("field_semantics", {})),
                    str(op.get("grain", op["data_role"])),
                    str(op.get("license", "unknown")),
                    "registered",
                    str(op.get("access_mode", "unknown")),
                )
            )
        return cls(rows)

    def resolve_binding(self, binding: dict[str, Any]) -> list[dict[str, str]]:
        allowed = {
            "provider_id",
            "operation_id",
            "schema_version",
            "snapshot_hash",
            "auth_ref",
            "source_id",
        }
        if not isinstance(binding, dict) or set(binding) - allowed:
            return [{"field": "source_bindings", "reason": "unknown_binding_field"}]
        operation = self._operations.get(
            (binding.get("operation_id"), binding.get("schema_version"))
        )
        if operation is None:
            return [
                {"field": "source_bindings", "reason": "unregistered_operation_version"}
            ]
        if binding.get("provider_id") != operation.provider_id:
            return [
                {"field": "source_bindings", "reason": "provider_operation_mismatch"}
            ]
        if operation.status in {"candidate", "error", "auth_error", "unknown"}:
            return [
                {"field": "source_bindings", "reason": "operation_" + operation.status}
            ]
        digest = binding.get("snapshot_hash")
        if not isinstance(digest, str) or len(digest.removeprefix("sha256:")) != 64:
            return [{"field": "source_bindings", "reason": "snapshot_hash_required"}]
        return []

    def known_field(self, field: str, postings: list[dict[str, Any]]) -> bool:
        # Saved fields remain visible even before a provider adapter knows how to
        # normalize them. Predicate semantics require an explicit version below.
        top = field.split(".")[0]
        return any(top in row for row in postings) or any(
            field in op.fields for op in self._operations.values()
        )

    def snapshot(self) -> list[dict[str, Any]]:
        return [deepcopy(op.__dict__) for _, op in sorted(self._operations.items())]

    def summary(self) -> dict[str, int]:
        values = list(self._operations.values())
        return {
            "registered_operations": len(values),
            "providers": len({op.provider_id for op in values}),
            "ready_operations": sum(op.status == "ready" for op in values),
            "declared_fields": len({field for op in values for field in op.fields}),
        }

    def register_normalizer(
        self, operation_id: str, schema_version: str, normalizer: Callable
    ) -> None:
        key = operation_id, schema_version
        if (
            key not in self._operations
            or not callable(normalizer)
            or key in self._normalizers
        ):
            raise ValueError(
                "registered operation and unique callable normalizer required"
            )
        self._normalizers[key] = normalizer

    @classmethod
    def from_source_catalog(cls, catalog) -> CapabilityRegistry:
        return cls(
            [
                OperationStatus(
                    o.operation_id,
                    o.provider,
                    o.schema_version,
                    (o.data_role,),
                    tuple(f.internal_field for f in o.field_contracts),
                    o.data_role,
                    o.license,
                    "registered",
                    o.access_mode,
                )
                for o in catalog.operations
            ]
        )

    def ingest_saved(
        self,
        operation_id: str,
        schema_version: str,
        pages: list[list[dict[str, Any]]],
        *,
        source_kind: str,
        expected_pages: int | None = None,
    ) -> dict[str, Any]:
        """Normalize archived pages through an explicit adapter; perform no fetch."""
        key = operation_id, schema_version
        operation = self._operations.get(key)
        if (
            operation is None
            or key not in self._normalizers
            or operation.status not in {"ready", "registered", "partial"}
        ):
            raise ValueError("operation normalizer is not available")
        if source_kind not in {"observed", "fixture", "demo"} or not isinstance(
            pages, list
        ):
            raise ValueError("explicit source kind and archived pages required")
        if expected_pages is not None and (
            type(expected_pages) is not int or expected_pages < len(pages)
        ):
            raise ValueError("invalid expected page count")
        source_id = operation_id + ":" + content_hash(pages)[:20]
        postings = []
        seen = set()
        for page_index, page in enumerate(pages):
            if not isinstance(page, list) or any(
                not isinstance(row, dict) for row in page
            ):
                raise ValueError("adapter pages must contain objects")
            for raw in page:
                normalized = self._normalizers[key](deepcopy(raw))
                if (
                    not isinstance(normalized, dict)
                    or not normalized.get("posting_id")
                    or not normalized.get("revision")
                ):
                    raise ValueError(
                        "normalizer must return a posting identity and revision"
                    )
                if source_kind == "observed" and normalized.get("source_kind") in {
                    "fixture",
                    "demo",
                }:
                    raise ValueError("fixture cannot be promoted to observed")
                identity = normalized["posting_id"], normalized["revision"]
                if identity in seen:
                    raise ValueError("duplicate posting revision across pages")
                seen.add(identity)
                postings.append(
                    {
                        **normalized,
                        "provider_id": operation.provider_id,
                        "source_id": source_id,
                        "source_kind": source_kind,
                        "raw_attributes": deepcopy(raw),
                        "source_page_index": page_index,
                    }
                )
        complete = expected_pages is not None and expected_pages == len(pages)
        return {
            "source_kind": source_kind,
            "postings": postings,
            "coverage": {
                "received_pages": len(pages),
                "expected_pages": expected_pages,
                "complete": complete,
            },
            "sources": [
                {
                    "source_id": source_id,
                    "provider_id": operation.provider_id,
                    "operation_id": operation_id,
                    "schema_version": schema_version,
                    "snapshot_hash": content_hash(pages),
                    "payload": deepcopy(pages),
                    "rights": operation.rights,
                    "grain": operation.grain,
                    "status": "complete_saved" if complete else "partial_saved",
                }
            ],
        }
