"""Canonical responsibility owner; migrated from src/company_intel/selection_provenance.py."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class SelectionManifest:
    run_id: str
    selection: dict[str, Any]
    snapshot_ref: dict[str, Any]
    result_refs: dict[str, str]
    export_refs: dict[str, str]
    manifest_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
