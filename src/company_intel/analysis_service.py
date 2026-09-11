from __future__ import annotations

from typing import Any

import pandas as pd

from .analytics import dcf_scenarios, difference_in_differences, event_study


def validate_series_signature(rows: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Time series must share metric, unit, currency, frequency and adjustment."""
    keys = {
        (row.get("series_id"), row.get("unit"), row.get("currency"), row.get("frequency"), row.get("adjustment"))
        for row in rows
    }
    return (len(keys) <= 1, None if len(keys) <= 1 else "incompatible_series_signature")


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
        item["observation_axis"] = item.get("axis", "unknown")
        item["observation_date"] = (
            item.get("observation_date") or item.get("period_end") or item.get("event_date")
        )
        accepted.append(item)
    compatible, reason = validate_series_signature(accepted)
    if not compatible:
        excluded.extend({**row, "exclusion_reason": reason} for row in accepted)
        accepted = []
    accepted.sort(key=lambda item: (str(item.get("observation_date", "")), str(item.get("available_at", ""))))
    return {
        "timeline": pd.DataFrame(accepted),
        "exclusions": pd.DataFrame(excluded),
        "metadata": {
            "entity_id": entity_id,
            "as_of": as_of,
            "axes_remain_distinct": True,
            "warning": "Company, market and macro observations are aligned, not treated as equivalent facts.",
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
