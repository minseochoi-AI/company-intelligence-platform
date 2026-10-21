"""Canonical responsibility owner; migrated from src/company_intel/live_snapshots.py."""

from __future__ import annotations
from cil_contracts.snapshots import SnapshotManifest
from cil_contracts.snapshots import SnapshotRequest
from cil_domain.provenance.snapshots import _sha256
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Mapping

Collector = Callable[[Mapping[str, Any]], Any]


def refresh_sources(
    collectors: Mapping[str, Collector],
    request: SnapshotRequest,
    *,
    collected_at: str | None = None,
) -> SnapshotManifest:
    """Collect each requested provider independently and preserve partial failure.

    The manifest stores only parameter names/values and response digests.  It
    never contains response bodies, credentials, or transport headers.
    """
    timestamp = collected_at or datetime.now(UTC).isoformat()
    sources: list[dict[str, Any]] = []
    for provider in request.providers:
        parameters = dict(request.parameters.get(provider, {}))
        collector = collectors.get(provider)
        if collector is None:
            sources.append(
                {
                    "provider": provider,
                    "status": "unavailable",
                    "reason": "collector_not_registered",
                    "parameters": parameters,
                }
            )
            continue
        try:
            payload = collector(parameters)
            record_count = (
                len(payload)
                if isinstance(payload, list)
                else len(payload.get("jobs", payload.get("polozky", [])))
                if isinstance(payload, dict)
                else None
            )
            sources.append(
                {
                    "provider": provider,
                    "status": "collected",
                    "parameters": parameters,
                    "record_count": record_count,
                    "payload_sha256": _sha256(payload),
                }
            )
        except Exception as error:
            sources.append(
                {
                    "provider": provider,
                    "status": "failed",
                    "parameters": parameters,
                    "reason": type(error).__name__,
                }
            )
    failed = [item for item in sources if item["status"] != "collected"]
    status = (
        "complete"
        if not failed
        else "partial"
        if len(failed) < len(sources)
        else "failed"
    )
    snapshot_id = (
        "snapshot-"
        + _sha256({"at": timestamp, "request": asdict(request), "sources": sources})[
            :20
        ]
    )
    return SnapshotManifest(
        snapshot_id,
        timestamp,
        tuple(sources),
        status,
        bool(failed and status == "partial"),
        asdict(request),
    )


def select_snapshot(
    snapshots: Mapping[str, Mapping[str, Any]], snapshot_id: str | None = None
) -> dict[str, Any]:
    """Select one immutable snapshot; no implicit latest refresh is performed."""
    if snapshot_id:
        selected = snapshots.get(snapshot_id)
        if selected is None:
            raise ValueError("snapshot_id_not_found")
        return dict(selected)
    if not snapshots:
        raise ValueError("snapshot_unavailable")
    identifier, selected = max(
        snapshots.items(), key=lambda item: str(item[1].get("collected_at", ""))
    )
    return {"snapshot_id": identifier, **dict(selected)}
