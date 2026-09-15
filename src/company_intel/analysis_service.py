from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd

from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
)
from .job_trends import aggregate_job_trends

SERIES_SIGNATURE_FIELDS = ("series_id", "unit", "currency", "frequency", "adjustment")


def _series_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row.get(field) for field in SERIES_SIGNATURE_FIELDS)


def _series_group_id(axis: str, signature: tuple[Any, ...]) -> str:
    encoded = json.dumps([axis, signature], ensure_ascii=False, default=str, separators=(",", ":"))
    return f"{axis}:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()[:12]}"


def validate_series_signature(rows: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Time series must share metric, unit, currency, frequency and adjustment."""
    keys = {_series_signature(row) for row in rows}
    return (len(keys) <= 1, None if len(keys) <= 1 else "incompatible_series_signature")


def timeline_series_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Describe compatible series groups without collapsing different axes.

    A financial statement, a market-price series and a macro series normally
    have different metrics, units and frequencies.  They can be aligned on
    observation date for display, but are only comparable inside their own
    ``observation_axis × series signature`` group.
    """
    grouped: dict[tuple[str, tuple[Any, ...]], list[dict[str, Any]]] = {}
    for row in rows:
        axis = str(row.get("observation_axis") or row.get("axis") or "unknown")
        key = (axis, _series_signature(row))
        grouped.setdefault(key, []).append(row)
    output: list[dict[str, Any]] = []
    for (axis, signature), group_rows in sorted(
        grouped.items(), key=lambda item: (item[0][0], tuple(str(value) for value in item[0][1]))
    ):
        dates = sorted(
            str(row["observation_date"])
            for row in group_rows
            if row.get("observation_date") is not None
        )
        output.append(
            {
                "series_group_id": _series_group_id(axis, signature),
                "observation_axis": axis,
                "signature": dict(zip(SERIES_SIGNATURE_FIELDS, signature, strict=True)),
                "row_count": len(group_rows),
                "first_observation_date": dates[0] if dates else None,
                "last_observation_date": dates[-1] if dates else None,
                "comparison_scope": "within_group_only",
            }
        )
    return output


def build_company_timeline(
    rows: list[dict[str, Any]], *, entity_id: str, as_of: str
) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("entity_id", "")) != entity_id:
            continue
        available_at = row.get("available_at")
        if not available_at or str(available_at) > as_of:
            excluded.append({**row, "exclusion_reason": "not_available_as_of"})
            continue
        item = dict(row)
        item["observation_axis"] = item.get("axis") or "unknown"
        item["observation_date"] = (
            item.get("observation_date") or item.get("period_end") or item.get("event_date")
        )
        if not item["observation_date"]:
            excluded.append({**item, "exclusion_reason": "observation_date_missing"})
            continue
        accepted.append(item)
    series_groups = timeline_series_groups(accepted)
    group_ids = {
        (
            group["observation_axis"],
            tuple(group["signature"].get(field) for field in SERIES_SIGNATURE_FIELDS),
        ): group["series_group_id"]
        for group in series_groups
    }
    for item in accepted:
        key = (str(item["observation_axis"]), _series_signature(item))
        item["series_group_id"] = group_ids[key]
    accepted.sort(
        key=lambda item: (
            str(item.get("observation_date", "")),
            str(item.get("observation_axis", "")),
            str(item.get("series_group_id", "")),
            str(item.get("available_at", "")),
        )
    )
    exclusion_reasons: dict[str, int] = {}
    for item in excluded:
        reason = str(item.get("exclusion_reason", "unknown"))
        exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
    return {
        "timeline": pd.DataFrame(accepted),
        "exclusions": pd.DataFrame(excluded),
        "metadata": {
            "entity_id": entity_id,
            "as_of": as_of,
            "axes_remain_distinct": True,
            "alignment": {
                "key": "observation_date",
                "method": "outer-date-alignment",
                "comparability": "within_axis_and_signature_only",
            },
            "series_groups": series_groups,
            "excluded_count": len(excluded),
            "exclusions": {
                "count": len(excluded),
                "by_reason": dict(sorted(exclusion_reasons.items())),
            },
            "warning": (
                "Company, market and macro observations are date-aligned, "
                "not treated as equivalent facts."
            ),
        },
    }


def evaluate_valuation_scenarios(
    *, revenue: float | None, net_debt: float | None, shares: float | None,
    evidence: dict[str, str | None], years: int = 5
) -> dict[str, Any]:
    missing = [name for name, value in {"revenue": revenue, "net_debt": net_debt, "shares": shares}.items() if value is None]
    missing_evidence = [name for name in ("source_url", "available_at", "unit", "currency", "period", "concept") if not evidence.get(name)]
    if evidence.get("observation_kind") not in {None, "actual"}:
        missing_evidence.append("actual_observation_required")
    if missing or missing_evidence:
        return {"status": "unavailable", "missing_inputs": missing, "missing_evidence": missing_evidence}
    result = dcf_scenarios(float(revenue), float(net_debt), float(shares), years=years)
    return {
        "status": "scenario-only",
        "evidence": evidence,
        "result": result,
        "warning": "Assumption-bound scenario, not a forecast, price target, or investment recommendation.",
    }


def evaluate_ai_event(
    *, asset_returns: list[float], benchmark_returns: list[float], event_index: int,
    event_evidence: dict[str, str | None], treated_pre: list[float] | None = None,
    treated_post: list[float] | None = None, control_pre: list[float] | None = None,
    control_post: list[float] | None = None,
) -> dict[str, Any]:
    missing = [name for name in ("event_date", "source_url", "available_at") if not event_evidence.get(name)]
    if missing:
        return {"status": "unavailable", "missing_evidence": missing}
    if event_evidence.get("price_adjustment") == "raw":
        return {"status": "ineligible", "reasons": ["raw_price_series_not_accepted"]}
    if len(asset_returns) != len(benchmark_returns) or len(asset_returns) < 7:
        return {"status": "ineligible", "reasons": ["insufficient_or_unaligned_return_series"]}
    output: dict[str, Any] = {
        "status": "association-only",
        "event_evidence": event_evidence,
        "event_study": event_study(asset_returns, benchmark_returns, event_index),
        "causal_ready": False,
    }
    did_inputs = (treated_pre, treated_post, control_pre, control_post)
    if all(item for item in did_inputs) and event_evidence.get("control_signature"):
        output["difference_in_differences"] = difference_in_differences(*did_inputs)  # type: ignore[arg-type]
        output["causal_limitations"] = ["parallel_pre_trends_not_established", "simultaneous_shocks_not_ruled_out"]
    else:
        output["causal_limitations"] = ["control_group_or_pre_post_outcomes_missing"]
    return output


def evaluate_job_trends(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a job-posting trend only when repeated snapshots are comparable."""

    return aggregate_job_trends(snapshots)


def job_trend_timeline(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    result = evaluate_job_trends(snapshots)
    return {"status": result["status"], "series": result.get("series", []), "eligibility": result.get("eligibility", {})}


def job_event_boundary(trend_result: dict[str, Any], *, has_control: bool) -> dict[str, Any]:
    if trend_result.get("status") != "eligible":
        return {"status": "unavailable", "reason": trend_result.get("eligibility", {}).get("reason", "trend_ineligible")}
    return {"status": "association-only", "causal_ready": False, "reason": None if has_control else "control_group_missing"}
