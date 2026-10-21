"""Canonical responsibility owner; migrated from src/company_intel/run_manifest.py."""

from __future__ import annotations
from cil_domain.provenance.manifests import _json_safe
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
import json


def write_run_manifest(path: Path, manifest: Mapping[str, Any]) -> Path:
    """Persist a sanitized manifest as deterministic, human-readable JSON."""
    safe_manifest = _json_safe(manifest)
    if not isinstance(safe_manifest, dict):
        raise ValueError("run manifest must be an object")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(safe_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    path.write_text(encoded, encoding="utf-8")
    return path
