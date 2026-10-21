"""Canonical responsibility owner; migrated from src/company_intel/selection_provenance.py."""

from __future__ import annotations
from cil_contracts.provenance import SelectionManifest
from cil_domain.provenance.redaction import sanitize_manifest
from typing import Any, Callable, Mapping
import hashlib
import json


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


def bind_selection_run(
    selection: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    results: Mapping[str, Any],
    exports: Mapping[str, bytes] | None = None,
) -> SelectionManifest:
    safe_selection = sanitize_manifest(
        {"selection": dict(selection)}, allowlist={"selection"}
    )["selection"]
    safe_snapshot = sanitize_manifest(
        {
            key: snapshot.get(key)
            for key in ("snapshot_id", "collected_at", "status", "sources")
        }
    )
    result_refs = {str(key): _hash(value) for key, value in sorted(results.items())}
    export_refs = {
        str(key): hashlib.sha256(value).hexdigest()
        for key, value in sorted((exports or {}).items())
    }
    payload = {
        "selection": safe_selection,
        "snapshot_ref": safe_snapshot,
        "result_refs": result_refs,
        "export_refs": export_refs,
    }
    digest = _hash(payload)
    return SelectionManifest(
        f"selection-{digest[:16]}",
        dict(safe_selection),
        dict(safe_snapshot),
        result_refs,
        export_refs,
        digest,
    )


def verify_run_chain(manifest: Mapping[str, Any]) -> bool:
    expected = manifest.get("manifest_sha256")
    payload = {
        key: manifest.get(key)
        for key in ("selection", "snapshot_ref", "result_refs", "export_refs")
    }
    return isinstance(expected, str) and _hash(payload) == expected
