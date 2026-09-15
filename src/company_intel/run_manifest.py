"""Reproducible, redacted lineage records for local CLI runs.

The manifest is intentionally a *description* of a run, rather than a copy of
provider payloads.  It lets a user reconstruct which saved inputs, facets and
output hashes were used without persisting credentials, contact details, or
raw responses alongside an export.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .security import SENSITIVE_EXPORT_KEYS, SENSITIVE_QUERY_KEYS, sanitize_manifest

SCHEMA_VERSION = "1.0"

# Export redaction is deliberately stricter than query-string redaction.  A
# run manifest can contain user-entered profiles, so credential-shaped fields
# must never be retained just because their exact provider key is unknown.
SENSITIVE_MANIFEST_KEYS = SENSITIVE_EXPORT_KEYS | SENSITIVE_QUERY_KEYS | {
    "access_token",
    "bearer",
    "client_secret",
    "credential",
    "credentials",
    "cookie",
    "password",
    "private_key",
    "secret",
    "token",
}

_RAW_OR_CONTACT_KEYS = {
    "body",
    "description_html",
    "email",
    "headers",
    "phone",
    "raw_body",
    "raw_detail",
    "raw_payload",
    "raw_response",
    "response_body",
    "telephone",
}


def _is_sensitive_key(key: object) -> bool:
    value = str(key).casefold()
    return (
        value in SENSITIVE_MANIFEST_KEYS
        or value in _RAW_OR_CONTACT_KEYS
        or value.endswith("_token")
        or value.endswith("_secret")
        or value.endswith("_password")
    )


def _redact_manifest_url(value: str) -> str:
    parts = urlsplit(value)
    query = [
        (key, "<redacted>" if _is_sensitive_key(key) else item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _json_safe(value: Any, *, key: str | None = None) -> Any:
    """Return deterministic JSON-safe data with secrets and raw payloads removed."""
    if key is not None and _is_sensitive_key(key):
        return "<redacted>"
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe(asdict(value), key=key)
    if isinstance(value, Mapping):
        return {
            str(item_key): _json_safe(item_value, key=str(item_key))
            for item_key, item_value in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        values = [_json_safe(item) for item in value]
        # Sets have no input order.  Sorting their canonical JSON values makes
        # the resulting manifest hash repeatable without reordering lists.
        if isinstance(value, (set, frozenset)):
            return sorted(values, key=_canonical_json)
        return values
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return {"sha256": hashlib.sha256(value).hexdigest(), "bytes": len(value)}
    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            return _redact_manifest_url(value)
        return value
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _normalise_output_files(output_files: Any) -> list[dict[str, Any]]:
    """Convert file bytes, manifest-style rows, or file paths to hash records."""
    if not output_files:
        return []
    entries: list[dict[str, Any]] = []
    if isinstance(output_files, Mapping):
        iterable: Sequence[tuple[Any, Any]] = tuple(output_files.items())
        for name, content in iterable:
            if isinstance(content, bytes):
                entries.append(
                    {"name": str(name), "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
                )
            elif isinstance(content, Path):
                if content.is_file():
                    body = content.read_bytes()
                    entries.append(
                        {"name": str(name), "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
                    )
                else:
                    entries.append({"name": str(name), "status": "not_found"})
            elif isinstance(content, Mapping):
                item = _json_safe(content)
                if isinstance(item, dict):
                    entries.append({"name": str(name), **item})
            else:
                entries.append({"name": str(name), "value": _json_safe(content)})
    elif isinstance(output_files, Sequence) and not isinstance(output_files, (str, bytes, bytearray)):
        for item in output_files:
            if isinstance(item, Mapping):
                safe_item = _json_safe(item)
                if isinstance(safe_item, dict):
                    entries.append(safe_item)
            elif isinstance(item, Path):
                entries.extend(_normalise_output_files({item.name: item}))
            else:
                entries.append({"name": str(item)})
    else:
        entries.append({"name": str(output_files)})
    return sorted(entries, key=lambda item: (str(item.get("name", "")), _canonical_json(item)))


def build_run_manifest(
    command: str,
    profile: Mapping[str, Any] | Any | None = None,
    facets: Sequence[Mapping[str, Any]] | None = None,
    sources: Sequence[Mapping[str, Any]] | None = None,
    verdict_counts: Mapping[str, int] | None = None,
    output_files: Mapping[str, Any] | Sequence[Any] | None = None,
    *,
    manifest: Mapping[str, Any] | None = None,
    output_manifest: Mapping[str, Any] | None = None,
    run_id: str | None = None,
    generated_at: str | None = None,
    selection: Mapping[str, Any] | None = None,
    snapshot_ref: Mapping[str, Any] | None = None,
    eligibility: Mapping[str, Any] | None = None,
    result_refs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a redacted, JSON-safe record linking inputs to output hashes.

    ``manifest`` is retained as a friendly alias for ``output_manifest`` so
    callers can pass the export manifest they already received from the export
    service.  The body is canonicalized before deriving a default run ID, which
    makes a repeated saved-snapshot run identifiable without using credentials.
    """
    if manifest is not None and output_manifest is not None:
        raise ValueError("pass either manifest or output_manifest, not both")
    safe_profile = _json_safe(profile or {})
    safe_facets = [_json_safe(item) for item in (facets or [])]
    safe_sources = [_json_safe(item) for item in (sources or [])]
    safe_counts = _json_safe(verdict_counts or {})
    safe_output_manifest = _json_safe(output_manifest if output_manifest is not None else manifest or {})
    content = {
        "command": str(command),
        "profile": safe_profile,
        "facets": safe_facets,
        "sources": safe_sources,
        "verdict_counts": safe_counts,
        "output_files": _normalise_output_files(output_files),
        "output_manifest": safe_output_manifest,
    }
    resolved_run_id = run_id or f"run-{_sha256(content)[:16]}"
    output = {
        "schema_version": "2.0" if any(item is not None for item in (selection, snapshot_ref, eligibility, result_refs)) else SCHEMA_VERSION,
        "run_id": str(resolved_run_id),
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        **content,
        "lineage": {
            "profile_sha256": _sha256(safe_profile),
            "facet_snapshot_sha256": _sha256(safe_facets),
            "source_snapshot_sha256": _sha256(safe_sources),
            "output_manifest_sha256": _sha256(safe_output_manifest),
        },
    }
    if selection is not None:
        output["selection_ref"] = sanitize_manifest({"selection": dict(selection)}, allowlist={"selection"})["selection"]
    if snapshot_ref is not None:
        output["snapshot_ref"] = sanitize_manifest(dict(snapshot_ref))
    if eligibility is not None:
        output["eligibility"] = sanitize_manifest({"eligibility": dict(eligibility)}, allowlist={"eligibility"})["eligibility"]
    if result_refs is not None:
        output["result_refs"] = sanitize_manifest({"result_refs": dict(result_refs)}, allowlist={"result_refs"})["result_refs"]
    return output


def sanitize_manifest_value(value: Any) -> Any:
    """Expose the manifest-safe projection for export and reporting boundaries."""
    return _json_safe(value)


def snapshot_ref(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return sanitize_manifest({key: snapshot.get(key) for key in ("snapshot_id", "collected_at", "status", "sources")})


def selection_ref(selection: Mapping[str, Any]) -> dict[str, Any]:
    return sanitize_manifest({"selection": dict(selection)}, allowlist={"selection"})["selection"]


def result_refs(results: Mapping[str, Any]) -> dict[str, str]:
    return {str(key): _sha256(value) for key, value in sorted(results.items())}


def verify_manifest(manifest: Mapping[str, Any]) -> bool:
    """Validate only the deterministic lineage hashes that this module owns."""

    lineage = manifest.get("lineage")
    if not isinstance(lineage, Mapping):
        return False
    return lineage.get("profile_sha256") == _sha256(manifest.get("profile", {})) and lineage.get("source_snapshot_sha256") == _sha256(manifest.get("sources", []))


def write_run_manifest(path: Path, manifest: Mapping[str, Any]) -> Path:
    """Persist a sanitized manifest as deterministic, human-readable JSON."""
    safe_manifest = _json_safe(manifest)
    if not isinstance(safe_manifest, dict):
        raise ValueError("run manifest must be an object")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(safe_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(encoded, encoding="utf-8")
    return path
