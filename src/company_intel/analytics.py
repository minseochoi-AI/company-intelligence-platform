from __future__ import annotations

import math
import statistics
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1.0


def financial_metrics(facts: dict[str, float | None]) -> dict[str, float | None]:
    revenue = facts.get("revenue")
    return {
        "revenue_growth": pct_change(revenue, facts.get("revenue_previous")),
        "gross_margin": safe_div(facts.get("gross_profit"), revenue),
        "operating_margin": safe_div(facts.get("operating_income"), revenue),
        "net_margin": safe_div(facts.get("net_income"), revenue),
        "cfo_margin": safe_div(facts.get("cfo"), revenue),
        "fcf": None
        if facts.get("cfo") is None or facts.get("capex") is None
        else facts["cfo"] - abs(facts["capex"]),
        "fcf_margin": safe_div(
            None
            if facts.get("cfo") is None or facts.get("capex") is None
            else facts["cfo"] - abs(facts["capex"]),
            revenue,
        ),
        "cash_conversion": safe_div(facts.get("cfo"), facts.get("net_income")),
        "current_ratio": safe_div(facts.get("current_assets"), facts.get("current_liabilities")),
        "net_debt": None
        if facts.get("debt") is None or facts.get("cash") is None
        else facts["debt"] - facts["cash"],
        "net_debt_to_ebitda": safe_div(
            None if facts.get("debt") is None or facts.get("cash") is None else facts["debt"] - facts["cash"],
            facts.get("ebitda"),
        ),
        "interest_coverage": safe_div(facts.get("operating_income"), facts.get("interest_expense")),
        "roic": safe_div(facts.get("nopat"), facts.get("invested_capital")),
        "revenue_per_employee": safe_div(revenue, facts.get("employees")),
        "ebit_per_employee": safe_div(facts.get("operating_income"), facts.get("employees")),
        "inventory_turnover": safe_div(facts.get("cost_of_revenue"), facts.get("average_inventory")),
        "capex_to_revenue": safe_div(facts.get("capex"), revenue),
    }


def _percentile(values: list[float], value: float, higher_is_better: bool) -> float:
    if len(values) == 1:
        return 0.5
    ordered = sorted(values, reverse=not higher_is_better)
    rank = (
        sum(item <= value for item in ordered) if higher_is_better else sum(item >= value for item in ordered)
    )
    return (rank - 1) / (len(values) - 1)


def _robust_z(values: list[float], value: float, higher_is_better: bool) -> float:
    median = statistics.median(values)
    mad = statistics.median(abs(item - median) for item in values)
    z = 0.0 if mad == 0 else 0.67448975 * (value - median) / mad
    return z if higher_is_better else -z


def rank_companies(
    rows: list[dict[str, Any]],
    weights: dict[str, float],
    directions: dict[str, bool] | None = None,
) -> list[dict[str, Any]]:
    """Rank only inside country × industry × size_bucket peer groups."""
    directions = directions or {}
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row.get("country", "UNKNOWN"),
            row.get("industry", "UNKNOWN"),
            row.get("size_bucket", "UNKNOWN"),
        )
        groups[key].append(row)

    ranked: list[dict[str, Any]] = []
    for peer_key, peers in groups.items():
        values_by_metric = {
            metric: [
                float(row[metric])
                for row in peers
                if row.get(metric) is not None and math.isfinite(float(row[metric]))
            ]
            for metric in weights
        }
        for row in peers:
            metrics: dict[str, Any] = {}
            weighted_total = 0.0
            used_weight = 0.0
            for metric, weight in weights.items():
                value = row.get(metric)
                values = values_by_metric[metric]
                if value is None or not values:
                    metrics[metric] = {"value": value, "percentile": None, "robust_z": None}
                    continue
                higher = directions.get(metric, True)
                percentile = _percentile(values, float(value), higher)
                robust_z = _robust_z(values, float(value), higher)
                metrics[metric] = {"value": value, "percentile": percentile, "robust_z": robust_z}
                weighted_total += percentile * weight
                used_weight += weight
            score = 100.0 * weighted_total / used_weight if used_weight else None
            coverage = used_weight / sum(weights.values()) if weights else 0.0
            ranked.append(
                {
                    **row,
                    "peer_group": "|".join(peer_key),
                    "peer_count": len(peers),
                    "metrics": metrics,
                    "composite_score": score,
                    "data_coverage": coverage,
                }
            )
    return sorted(
        ranked,
        key=lambda row: (row["composite_score"] is not None, row["composite_score"] or -1),
        reverse=True,
    )


def macro_sensitivity(
    company_returns: Iterable[float], macro_changes: dict[str, Iterable[float]]
) -> dict[str, Any]:
    y = np.asarray(list(company_returns), dtype=float)
    names = list(macro_changes)
    if not names:
        raise ValueError("At least one macro series is required")
    columns = [np.asarray(list(macro_changes[name]), dtype=float) for name in names]
    length = min([len(y), *[len(column) for column in columns]])
    if length < len(names) + 3:
        raise ValueError("Not enough aligned observations")
    y = y[-length:]
    x = np.column_stack([column[-length:] for column in columns])
    valid = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    y, x = y[valid], x[valid]
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    predicted = design @ coefficients
    residual = y - predicted
    ss_total = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - float(np.sum(residual**2)) / ss_total if ss_total else 0.0
    correlations = {
        name: float(np.corrcoef(y, x[:, index])[0, 1]) if np.std(x[:, index]) and np.std(y) else None
        for index, name in enumerate(names)
    }
    return {
        "observations": len(y),
        "intercept": float(coefficients[0]),
        "betas": {name: float(coefficients[index + 1]) for index, name in enumerate(names)},
        "correlations": correlations,
        "r_squared": r_squared,
        "warning": "Association, not causal effect; verify stationarity, lags, multicollinearity and release timing.",
    }


def hiring_change(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in snapshots:
        grouped[(str(row["entity_id"]), str(row["snapshot_date"]))].add(str(row["job_id"]))
    per_entity: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for (entity_id, day), job_ids in grouped.items():
        per_entity[entity_id].append((day, len(job_ids)))
    output = []
    for entity_id, series in per_entity.items():
        series.sort()
        previous = None
        for day, count in series:
            output.append(
                {
                    "entity_id": entity_id,
                    "snapshot_date": day,
                    "open_postings": count,
                    "absolute_change": None if previous is None else count - previous,
                    "growth_rate": None if previous in (None, 0) else count / previous - 1,
                }
            )
            previous = count
    return output


def event_study(
    asset_returns: list[float],
    benchmark_returns: list[float],
    event_index: int,
    windows: tuple[int, ...] = (1, 5, 20),
) -> dict[str, Any]:
    if len(asset_returns) != len(benchmark_returns):
        raise ValueError("Asset and benchmark return series must have equal length")
    abnormal = np.asarray(asset_returns, dtype=float) - np.asarray(benchmark_returns, dtype=float)
    output: dict[str, Any] = {"event_index": event_index, "observations": len(abnormal), "windows": {}}
    for window in windows:
        start, end = max(0, event_index - window), min(len(abnormal), event_index + window + 1)
        selected = abnormal[start:end]
        output["windows"][f"[-{window},+{window}]"] = {
            "start_index": start,
            "end_index": end - 1,
            "car": float(np.nansum(selected)),
            "mean_abnormal_return": float(np.nanmean(selected)),
            "observation_count": int(np.sum(np.isfinite(selected))),
        }
    return output


def difference_in_differences(
    treated_pre: Iterable[float],
    treated_post: Iterable[float],
    control_pre: Iterable[float],
    control_post: Iterable[float],
) -> dict[str, Any]:
    arrays = [
        np.asarray(list(values), dtype=float)
        for values in (treated_pre, treated_post, control_pre, control_post)
    ]
    if any(len(values) == 0 for values in arrays):
        raise ValueError("All four groups require observations")
    means = [float(np.nanmean(values)) for values in arrays]
    treated_change = means[1] - means[0]
    control_change = means[3] - means[2]
    return {
        "treated_pre_mean": means[0],
        "treated_post_mean": means[1],
        "control_pre_mean": means[2],
        "control_post_mean": means[3],
        "treated_change": treated_change,
        "control_change": control_change,
        "did_estimate": treated_change - control_change,
        "warning": "Causal interpretation requires parallel pre-trends and no simultaneous differential shock.",
    }


@dataclass(frozen=True)
class DCFScenario:
    name: str
    revenue_growth: float
    fcf_margin: float
    discount_rate: float
    terminal_growth: float


def dcf_scenarios(
    revenue: float,
    net_debt: float,
    shares: float,
    scenarios: list[DCFScenario] | None = None,
    years: int = 5,
) -> dict[str, Any]:
    scenarios = scenarios or [
        DCFScenario("downside", 0.00, 0.10, 0.11, 0.01),
        DCFScenario("base", 0.05, 0.15, 0.09, 0.025),
        DCFScenario("upside", 0.10, 0.20, 0.08, 0.035),
    ]
    output = []
    for scenario in scenarios:
        if scenario.discount_rate <= scenario.terminal_growth:
            raise ValueError("discount_rate must exceed terminal_growth")
        projected_revenue = revenue
        present_value = 0.0
        yearly_fcf = []
        for year in range(1, years + 1):
            projected_revenue *= 1 + scenario.revenue_growth
            fcf = projected_revenue * scenario.fcf_margin
            pv = fcf / (1 + scenario.discount_rate) ** year
            present_value += pv
            yearly_fcf.append({"year": year, "revenue": projected_revenue, "fcf": fcf, "present_value": pv})
        terminal_value = (
            yearly_fcf[-1]["fcf"]
            * (1 + scenario.terminal_growth)
            / (scenario.discount_rate - scenario.terminal_growth)
        )
        terminal_pv = terminal_value / (1 + scenario.discount_rate) ** years
        enterprise_value = present_value + terminal_pv
        equity_value = enterprise_value - net_debt
        output.append(
            {
                **asdict(scenario),
                "enterprise_value": enterprise_value,
                "equity_value": equity_value,
                "value_per_share": safe_div(equity_value, shares),
                "terminal_value_share": terminal_pv / enterprise_value if enterprise_value else None,
                "yearly_projection": yearly_fcf,
            }
        )
    return {
        "years": years,
        "scenarios": output,
        "warning": "Scenario output depends on assumptions; it is not a forecast guarantee.",
    }


def guarded_dcf_scenarios(revenue: float | None, net_debt: float | None, shares: float | None, *, evidence_complete: bool, years: int = 5) -> dict[str, Any]:
    if not evidence_complete or None in {revenue, net_debt, shares}:
        return {"status": "unavailable", "reason": "actual_period_unit_currency_evidence_required"}
    return {"status": "scenario-only", "result": dcf_scenarios(float(revenue), float(net_debt), float(shares), years=years)}


DEFAULT_SCORE_WEIGHTS = {
    "financial_health": 0.20,
    "profitability": 0.20,
    "growth_quality": 0.20,
    "valuation": 0.15,
    "macro_industry_fit": 0.10,
    "operations_workforce": 0.10,
    "disclosure_governance": 0.05,
}


def future_value_score(
    components: dict[str, float | None], confidence: dict[str, float] | None = None
) -> dict[str, Any]:
    confidence = confidence or {}
    weighted = 0.0
    usable_weight = 0.0
    detail: dict[str, Any] = {}
    for name, weight in DEFAULT_SCORE_WEIGHTS.items():
        value = components.get(name)
        reliability = min(max(confidence.get(name, 1.0), 0.0), 1.0)
        if value is None:
            detail[name] = {"score": None, "weight": weight, "confidence": 0.0}
            continue
        bounded = min(max(float(value), 0.0), 100.0)
        effective_weight = weight * reliability
        weighted += bounded * effective_weight
        usable_weight += effective_weight
        detail[name] = {"score": bounded, "weight": weight, "confidence": reliability}
    total_weight = sum(DEFAULT_SCORE_WEIGHTS.values())
    return {
        "future_value_score": weighted / usable_weight if usable_weight else None,
        "data_confidence": usable_weight / total_weight,
        "components": detail,
        "interpretation": "Peer-relative composite, not a price target. Read with scenario DCF and source evidence.",
    }
