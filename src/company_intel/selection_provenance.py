"""Hash-linked, replayable selection records without raw provider payloads."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .security import sanitize_manifest


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


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


def bind_selection_run(
    selection: Mapping[str, Any], snapshot: Mapping[str, Any], results: Mapping[str, Any], exports: Mapping[str, bytes] | None = None
) -> SelectionManifest:
    safe_selection = sanitize_manifest({"selection": dict(selection)}, allowlist={"selection"})["selection"]
    safe_snapshot = sanitize_manifest({key: snapshot.get(key) for key in ("snapshot_id", "collected_at", "status", "sources")})
    result_refs = {str(key): _hash(value) for key, value in sorted(results.items())}
    export_refs = {str(key): hashlib.sha256(value).hexdigest() for key, value in sorted((exports or {}).items())}
    payload = {"selection": safe_selection, "snapshot_ref": safe_snapshot, "result_refs": result_refs, "export_refs": export_refs}
    digest = _hash(payload)
    return SelectionManifest(f"selection-{digest[:16]}", dict(safe_selection), dict(safe_snapshot), result_refs, export_refs, digest)


def verify_run_chain(manifest: Mapping[str, Any]) -> bool:
    expected = manifest.get("manifest_sha256")
    payload = {key: manifest.get(key) for key in ("selection", "snapshot_ref", "result_refs", "export_refs")}
    return isinstance(expected, str) and _hash(payload) == expected


def replay_selection(manifest: Mapping[str, Any], executor: Callable[[Mapping[str, Any]], Any]) -> Any:
    if not verify_run_chain(manifest):
        raise ValueError("selection_manifest_tampered")
    return executor(dict(manifest.get("selection") or {}))
