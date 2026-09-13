from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from .analytics import rank_companies
from .models import ComparabilitySignature
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
    comparability_group: str | None = None
    require_complete_signature: bool = True


@dataclass(frozen=True)
class ScreenerResult:
    rankings: pd.DataFrame
    exclusions: pd.DataFrame
    metadata: dict[str, Any]


@dataclass(frozen=True)
class _ComparableGroup:
    group_id: str
    label: str
    peer_scope: tuple[str | None, str | None, str | None]
    signature: ComparabilitySignature
    rows: tuple[dict[str, Any], ...]


_NON_MONETARY_UNITS = {
    "%",
    "percent",
    "percentage",
    "ratio",
    "count",
    "index",
    "persons",
    "headcount",
}


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _signature_missing_fields(signature: ComparabilitySignature) -> tuple[str, ...]:
    """Return required semantic components absent from an otherwise scoped row."""

    missing = [
        name
        for name, value in (
            ("period", signature.period),
            ("unit", signature.unit),
            ("concept", signature.concept),
            ("vintage", signature.vintage),
            ("coverage", signature.coverage),
        )
        if not _text(value)
    ]
    unit = (_text(signature.unit) or "").casefold()
    if not _text(signature.currency) and unit not in _NON_MONETARY_UNITS:
        missing.append("currency")
    return tuple(missing)


def _group_id(
    peer_scope: tuple[str | None, str | None, str | None], signature: ComparabilitySignature
) -> str:
    canonical = json.dumps(
        {"peer_scope": peer_scope, "signature": signature.key()},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"cmp-{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


def _signature_label(signature: ComparabilitySignature) -> str:
    names = ("currency", "period", "unit", "concept", "vintage", "coverage")
    values = (
        signature.currency,
        signature.period,
        signature.unit,
        signature.concept,
        signature.vintage,
        signature.coverage,
    )
    return "; ".join(f"{name}={value or 'unknown'}" for name, value in zip(names, values, strict=True))


def _group_metadata(group: _ComparableGroup, *, selected: bool, choice_required: bool) -> dict[str, Any]:
    return {
        "group_id": group.group_id,
        "label": group.label,
        "peer_scope": {
            "country": group.peer_scope[0],
            "industry": group.peer_scope[1],
            "size_bucket": group.peer_scope[2],
        },
        "signature": {
            "country_code": group.signature.country_code,
            "industry": group.signature.industry,
            "size_bucket": group.signature.size_bucket,
            "currency": group.signature.currency,
            "period": group.signature.period,
            "unit": group.signature.unit,
            "concept": group.signature.concept,
            "vintage": group.signature.vintage,
            "coverage": group.signature.coverage,
        },
        "peer_count": len(group.rows),
        "selected": selected,
        "choice_required": choice_required,
    }


def _comparability_groups(rows: list[dict[str, Any]]) -> list[_ComparableGroup]:
    grouped: dict[
        tuple[tuple[str | None, str | None, str | None], tuple[str | None, ...]],
        list[dict[str, Any]],
    ] = defaultdict(list)
    signatures: dict[
        tuple[tuple[str | None, str | None, str | None], tuple[str | None, ...]],
        ComparabilitySignature,
    ] = {}
    for row in rows:
        signature = comparability_signature(row)
        peer_scope = (signature.country_code, signature.industry, signature.size_bucket)
        key = (peer_scope, signature.key())
        grouped[key].append(row)
        signatures[key] = signature
    output = []
    for (peer_scope, signature_key), group_rows in grouped.items():
        signature = signatures[(peer_scope, signature_key)]
        group_id = _group_id(peer_scope, signature)
        output.append(
            _ComparableGroup(
                group_id=group_id,
                label=(
                    f"{' | '.join(value or 'unknown' for value in peer_scope)} "
                    f"— {_signature_label(signature)}"
                ),
                peer_scope=peer_scope,
                signature=signature,
                rows=tuple(group_rows),
            )
        )
    return sorted(
        output,
        key=lambda group: (tuple(value or "" for value in group.peer_scope), group.group_id),
    )


def _select_comparability_groups(
    groups: list[_ComparableGroup], profile: ScreenerProfile, exclusions: list[dict[str, Any]]
) -> tuple[list[_ComparableGroup], dict[str, bool]]:
    if profile.comparability_group:
        selected = [group for group in groups if group.group_id == profile.comparability_group]
        if not selected:
            raise ValueError("comparability_group does not match an available comparability group")
        selected_ids = {group.group_id for group in selected}
        for group in groups:
            if group.group_id in selected_ids:
                continue
            for row in group.rows:
                exclusions.append(
                    {
                        "entity_id": row.get("entity_id"),
                        "reason": "comparability_group_not_selected",
                        "field": "comparability_group",
                        "comparability_group_id": group.group_id,
                    }
                )
        return selected, {group.group_id: False for group in groups}

    by_scope: dict[tuple[str | None, str | None, str | None], list[_ComparableGroup]] = defaultdict(list)
    for group in groups:
        by_scope[group.peer_scope].append(group)
    selected: list[_ComparableGroup] = []
    choice_required: dict[str, bool] = {}
    for scope_groups in by_scope.values():
        if len(scope_groups) == 1:
            selected.extend(scope_groups)
            choice_required[scope_groups[0].group_id] = False
            continue
        # Preserve the prior largest-group fallback for script compatibility,
        # but expose every alternative so an interactive caller can override
        # it instead of silently losing a valid comparison cohort.
        canonical = max(scope_groups, key=lambda group: len(group.rows))
        selected.append(canonical)
        for group in scope_groups:
            choice_required[group.group_id] = True
            if group.group_id == canonical.group_id:
                continue
            for row in group.rows:
                exclusions.append(
                    {
                        "entity_id": row.get("entity_id"),
                        "reason": "incompatible_comparability_signature",
                        "field": "comparability_group",
                        "comparability_group_id": group.group_id,
                    }
                )
    return selected, choice_required


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
            continue
        signature = comparability_signature(row)
        missing = _signature_missing_fields(signature) if profile.require_complete_signature else ()
        if missing:
            exclusions.append(
                {
                    "entity_id": entity_id,
                    "reason": "unverifiable_comparability_signature",
                    "field": ",".join(missing),
                }
            )
            continue
        eligible.append(row)

    groups = _comparability_groups(eligible)
    selected_groups, choice_required = _select_comparability_groups(groups, profile, exclusions)
    selected_rows: list[dict[str, Any]] = []
    for group in selected_groups:
        signature_text = "|".join(value or "not_applicable" for value in group.signature.key())
        selected_rows.extend(
            {
                **row,
                "comparability_signature": signature_text,
                "comparability_group_id": group.group_id,
                "comparability_group_label": group.label,
            }
            for row in group.rows
        )

    ranked = rank_companies(selected_rows, profile.metrics, profile.directions)
    output: list[dict[str, Any]] = []
    for row in ranked:
        if row["peer_count"] < profile.minimum_peer_size:
            exclusions.append(
                {
                    "entity_id": row.get("entity_id"),
                    "reason": "insufficient_peer_group",
                    "field": "peer_count",
                }
            )
            continue
        output.append(row)
    output.sort(
        key=lambda row: (
            str(row.get("peer_group", "")),
            -float(row["composite_score"]) if row.get("composite_score") is not None else float("inf"),
            str(row.get("entity_id", "")),
        )
    )
    selected_ids = {group.group_id for group in selected_groups}
    group_metadata = [
        _group_metadata(
            group,
            selected=group.group_id in selected_ids,
            choice_required=choice_required.get(group.group_id, False),
        )
        for group in groups
    ]
    return ScreenerResult(
        rankings=pd.DataFrame(output),
        exclusions=pd.DataFrame(
            exclusions,
            columns=("entity_id", "reason", "field", "comparability_group_id"),
        ),
        metadata={
            "as_of": profile.as_of,
            "metrics": profile.metrics,
            "directions": profile.directions,
            "minimum_peer_size": profile.minimum_peer_size,
            "comparability_group": profile.comparability_group,
            "default_comparability_selection": (
                "legacy_largest_group" if not profile.comparability_group else None
            ),
            "require_complete_signature": profile.require_complete_signature,
            "comparability_groups": group_metadata,
            "interpretation": (
                "Ranks are valid only inside the selected country × industry × size bucket × currency × "
                "period × unit × concept × vintage × coverage group. When several signatures occur in "
                "one peer scope, the legacy largest group is selected only as a backwards-compatible "
                "default; select comparability_group to choose another valid group."
            ),
        },
    )
