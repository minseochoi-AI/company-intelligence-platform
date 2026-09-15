"""Versioned, redacted snapshots for provider-backed job discovery.

The module intentionally has no HTTP client dependency.  Connectors are passed
in as narrow callables so a caller can use the same collection contract for a
saved fixture, a provider client, or a later scheduled refresh.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Mapping


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


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


Collector = Callable[[Mapping[str, Any]], Any]


def snapshot_freshness(collected_at: str | None, *, now: str | None = None, max_age_seconds: int = 86_400) -> dict[str, Any]:
    """Return an explicit freshness verdict without silently refreshing data."""

    if not collected_at:
        return {"status": "missing", "fresh": False, "age_seconds": None}
    try:
        collected = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
        current = datetime.fromisoformat((now or datetime.now(UTC).isoformat()).replace("Z", "+00:00"))
    except ValueError:
        return {"status": "invalid_timestamp", "fresh": False, "age_seconds": None}
    age = max(0.0, (current - collected).total_seconds())
    return {"status": "fresh" if age <= max_age_seconds else "stale", "fresh": age <= max_age_seconds, "age_seconds": age}


def refresh_sources(
    collectors: Mapping[str, Collector], request: SnapshotRequest, *, collected_at: str | None = None
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
            sources.append({"provider": provider, "status": "unavailable", "reason": "collector_not_registered", "parameters": parameters})
            continue
        try:
            payload = collector(parameters)
            record_count = len(payload) if isinstance(payload, list) else len(payload.get("jobs", payload.get("polozky", []))) if isinstance(payload, dict) else None
            sources.append({
                "provider": provider,
                "status": "collected",
                "parameters": parameters,
                "record_count": record_count,
                "payload_sha256": _sha256(payload),
            })
        except Exception as error:  # Provider failures are data, not a reason to discard peer results.
            sources.append({"provider": provider, "status": "failed", "parameters": parameters, "reason": type(error).__name__})
    failed = [item for item in sources if item["status"] != "collected"]
    status = "complete" if not failed else "partial" if len(failed) < len(sources) else "failed"
    snapshot_id = "snapshot-" + _sha256({"at": timestamp, "request": asdict(request), "sources": sources})[:20]
    return SnapshotManifest(snapshot_id, timestamp, tuple(sources), status, bool(failed and status == "partial"), asdict(request))


def select_snapshot(snapshots: Mapping[str, Mapping[str, Any]], snapshot_id: str | None = None) -> dict[str, Any]:
    """Select one immutable snapshot; no implicit latest refresh is performed."""

    if snapshot_id:
        selected = snapshots.get(snapshot_id)
        if selected is None:
            raise ValueError("snapshot_id_not_found")
        return dict(selected)
    if not snapshots:
        raise ValueError("snapshot_unavailable")
    identifier, selected = max(snapshots.items(), key=lambda item: str(item[1].get("collected_at", "")))
    return {"snapshot_id": identifier, **dict(selected)}
