from __future__ import annotations

import json
import os
from typing import Any

from ..config import Settings
from ..models import Probe
from ..provider_clusters import ProviderCluster, classify_operation, select_operations
from ..source_catalog import evaluate_activation, load_source_catalog
from .keyed import keyed_probes
from .keyless import keyless_probes


def build_probes(settings: Settings, provider_filter: set[str] | None = None, purpose: str = "probe") -> list[Probe]:
    probes = keyed_probes() + keyless_probes(settings.sec_user_agent)
    if purpose not in {"probe", "production"}:
        raise ValueError("purpose must be probe or production")
    selected = probes if not provider_filter or "all" in provider_filter else [
        probe for probe in probes if probe.provider in provider_filter or probe.id in provider_filter
    ]
    if purpose == "probe":
        return selected
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    environment = dict(os.environ)
    return [
        probe for probe in selected
        if evaluate_activation(catalog.by_id(probe.id), environment).status.startswith("ready")
    ]


def source_health(settings: Settings) -> dict[str, dict[str, Any]]:
    """Show declared eligibility separately from the last saved live probe.

    A configured credential may still be rejected by its provider (for
    example, an inactive BEA key).  Combining those states would make
    ``provider-status`` deceptively green, so the latest validation receipt is
    surfaced as observation data rather than overwriting the catalog policy.
    """
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    environment = dict(os.environ)
    latest: dict[str, dict[str, Any]] = {}
    validation_file = settings.artifact_dir / "validation_results.json"
    if validation_file.is_file():
        try:
            payload = json.loads(validation_file.read_text(encoding="utf-8"))
            latest = {
                str(item["id"]): item
                for item in payload.get("results", [])
                if isinstance(item, dict) and item.get("id")
            }
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            # Provider status remains usable even if a manually edited receipt
            # is unreadable; the catalog is still the source of policy truth.
            latest = {}

    health: dict[str, dict[str, Any]] = {}
    for operation in catalog.operations:
        selection = classify_operation(operation)
        last = latest.get(operation.operation_id)
        health[operation.operation_id] = {
            "activation": evaluate_activation(operation, environment).status,
            "disposition": selection.disposition,
            "reason": selection.reason,
            "last_probe": None if last is None else {
                "status": last.get("status"),
                "http_status": last.get("http_status"),
                "collected_at": last.get("collected_at"),
                "detail": last.get("provider_error") or last.get("transport_error") or last.get("parse_error"),
            },
        }
    return health


def production_adapters(settings: Settings, cluster: ProviderCluster | None = None) -> list[Probe]:
    """Select enabled production operations, never fixed validation fixtures."""
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    if cluster is None:
        allowed = {
            item.operation_id
            for selected_cluster in ProviderCluster
            for item in select_operations(catalog.operations, selected_cluster)
        }
    else:
        allowed = {item.operation_id for item in select_operations(catalog.operations, cluster)}
    return [probe for probe in build_probes(settings, purpose="production") if probe.id in allowed]
