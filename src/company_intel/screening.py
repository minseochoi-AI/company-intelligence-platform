from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from .analytics import rank_companies
from .normalization import comparability_signature


@dataclass(frozen=True)
class ScreenerProfile:
    countries: tuple[str, ...]
    industries: tuple[str, ...]
    size_buckets: tuple[str, ...]
    metrics: dict[str, float]
    directions: dict[str, bool] = field(default_factory=dict)
    as_of: str | None = None
    minimum_peer_size: int = 2


@dataclass(frozen=True)
class ScreenerResult:
    rankings: pd.DataFrame
    exclusions: pd.DataFrame
    metadata: dict[str, Any]


def screen_companies(rows: list[dict[str, Any]], profile: ScreenerProfile) -> ScreenerResult:
    if not profile.countries or not profile.industries or not profile.size_buckets:
        raise ValueError("countries, industries and size_buckets are required")
    if not profile.metrics or any(weight <= 0 for weight in profile.metrics.values()):
        raise ValueError("metrics must contain positive weights")
    if profile.minimum_peer_size < 1:
        raise ValueError("minimum_peer_size must be positive")

    eligible: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for row in rows:
        entity_id = str(row.get("entity_id", ""))
        reason = None
        field_name = None
        if row.get("country") not in profile.countries:
            reason, field_name = "country_out_of_scope", "country"
        elif row.get("industry") not in profile.industries:
            reason, field_name = "industry_out_of_scope", "industry"
        elif row.get("size_bucket") not in profile.size_buckets:
            reason, field_name = "size_out_of_scope", "size_bucket"
        elif profile.as_of and (not row.get("available_at") or str(row["available_at"]) > profile.as_of):
            reason, field_name = "not_available_as_of", "available_at"
        elif row.get("metric_role") == "proxy" or row.get("is_proxy") is True:
            reason, field_name = "proxy_metric_not_rankable", "metric_role"
        elif not any(row.get(metric) is not None for metric in profile.metrics):
            reason, field_name = "all_selected_metrics_missing", "metrics"
        if reason:
            exclusions.append({"entity_id": entity_id, "reason": reason, "field": field_name})
        else:
            eligible.append(row)

    # Do not rank numerically similar values unless their meaning matches.
    signatures: dict[tuple[str | None, ...], list[dict[str, Any]]] = {}
    for row in eligible:
        signature = comparability_signature(row)
        values = signature.key()
        signatures.setdefault(values, []).append({**row, "comparability_signature": "|".join(value or "unknown" for value in values)})
    if len(signatures) > 1:
        canonical = max(signatures.values(), key=len)
        canonical_ids = {str(row.get("entity_id")) for row in canonical}
        for row in eligible:
            if str(row.get("entity_id")) not in canonical_ids:
                exclusions.append({"entity_id": row.get("entity_id"), "reason": "incompatible_comparability_signature", "field": "unit/currency/period/concept/vintage/coverage"})
        eligible = canonical
    ranked = rank_companies(eligible, profile.metrics, profile.directions)
    output: list[dict[str, Any]] = []
    for row in ranked:
        if row["peer_count"] < profile.minimum_peer_size:
            exclusions.append(
                {"entity_id": row.get("entity_id"), "reason": "insufficient_peer_group", "field": "peer_count"}
            )
            continue
        output.append(row)
    return ScreenerResult(
        rankings=pd.DataFrame(output),
        exclusions=pd.DataFrame(exclusions, columns=("entity_id", "reason", "field")),
        metadata={
            "as_of": profile.as_of,
            "metrics": profile.metrics,
            "directions": profile.directions,
            "minimum_peer_size": profile.minimum_peer_size,
            "interpretation": "Ranks are valid only inside country × industry × size bucket × currency × period × unit × concept × vintage × coverage groups.",
        },
    )
