"""Canonical responsibility owner; migrated from src/company_intel/live_snapshots.py."""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class SnapshotRequest:
    providers: tuple[str, ...]
    parameters: Mapping[str, Mapping[str, Any]]
    requested_at: str
    reuse_if_fresh: bool = True


@dataclass(frozen=True)
class SnapshotManifest:
    snapshot_id: str
    collected_at: str
    sources: tuple[dict[str, Any], ...]
    status: str
    partial_failure: bool
    request: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
