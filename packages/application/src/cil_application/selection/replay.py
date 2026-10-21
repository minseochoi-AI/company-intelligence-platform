"""Canonical responsibility owner; migrated from src/company_intel/selection_provenance.py."""

from __future__ import annotations
from cil_domain.provenance.selection import verify_run_chain
from typing import Any, Callable, Mapping


def replay_selection(
    manifest: Mapping[str, Any], executor: Callable[[Mapping[str, Any]], Any]
) -> Any:
    if not verify_run_chain(manifest):
        raise ValueError("selection_manifest_tampered")
    return executor(dict(manifest.get("selection") or {}))
