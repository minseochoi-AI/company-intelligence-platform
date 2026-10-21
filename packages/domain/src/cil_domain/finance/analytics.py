"""Canonical responsibility owner; migrated from src/company_intel/analytics.py."""

from __future__ import annotations
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from typing import Any
import math
import numpy as np
import statistics


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
        "current_ratio": safe_div(
            facts.get("current_assets"), facts.get("current_liabilities")
        ),
        "quick_ratio": safe_div(
            (facts.get("current_assets") or 0.0) - (facts.get("inventory") or 0.0)
            if facts.get("current_assets") is not None
            else None,
            facts.get("current_liabilities"),
        ),
        "cash_ratio": safe_div(facts.get("cash"), facts.get("current_liabilities")),
        "debt_to_equity": safe_div(
            facts.get("debt")
            if facts.get("debt") is not None
            else facts.get("total_liabilities"),
            facts.get("equity"),
        ),
        "operating_cash_flow_ratio": safe_div(
            facts.get("cfo"), facts.get("current_liabilities")
        ),
        "working_capital": None
        if facts.get("current_assets") is None
        or facts.get("current_liabilities") is None
        else facts["current_assets"] - facts["current_liabilities"],
        "net_debt": None
        if facts.get("debt") is None or facts.get("cash") is None
        else facts["debt"] - facts["cash"],
        "net_debt_to_ebitda": safe_div(
            None
            if facts.get("debt") is None or facts.get("cash") is None
            else facts["debt"] - facts["cash"],
            facts.get("ebitda"),
        ),
        "interest_coverage": safe_div(
            facts.get("operating_income"), facts.get("interest_expense")
        ),
        "roic": safe_div(facts.get("nopat"), facts.get("invested_capital")),
        "revenue_per_employee": safe_div(revenue, facts.get("employees")),
        "ebit_per_employee": safe_div(
            facts.get("operating_income"), facts.get("employees")
        ),
        "inventory_turnover": safe_div(
            facts.get("cost_of_revenue"), facts.get("average_inventory")
        ),
        "capex_to_revenue": safe_div(facts.get("capex"), revenue),
    }


def _percentile(values: list[float], value: float, higher_is_better: bool) -> float:
    if len(values) == 1:
        return 0.5
    ordered = sorted(values, reverse=not higher_is_better)
    rank = (
        sum((item <= value for item in ordered))
        if higher_is_better
        else sum((item >= value for item in ordered))
    )
    return (rank - 1) / (len(values) - 1)


def _robust_z(values: list[float], value: float, higher_is_better: bool) -> float:
    median = statistics.median(values)
    mad = statistics.median((abs(item - median) for item in values))
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
                    metrics[metric] = {
                        "value": value,
                        "percentile": None,
                        "robust_z": None,
                    }
                    continue
                higher = directions.get(metric, True)
                percentile = _percentile(values, float(value), higher)
                robust_z = _robust_z(values, float(value), higher)
                metrics[metric] = {
                    "value": value,
                    "percentile": percentile,
                    "robust_z": robust_z,
                }
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
        key=lambda row: (
            row["composite_score"] is not None,
            row["composite_score"] or -1,
        ),
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
    y, x = (y[valid], x[valid])
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    predicted = design @ coefficients
    residual = y - predicted
    ss_total = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - float(np.sum(residual**2)) / ss_total if ss_total else 0.0
    correlations = {
        name: float(np.corrcoef(y, x[:, index])[0, 1])
        if np.std(x[:, index]) and np.std(y)
        else None
        for index, name in enumerate(names)
    }
    return {
        "observations": len(y),
        "intercept": float(coefficients[0]),
        "betas": {
            name: float(coefficients[index + 1]) for index, name in enumerate(names)
        },
        "correlations": correlations,
        "r_squared": r_squared,
        "warning": "Association, not causal effect; verify stationarity, lags, multicollinearity and release timing.",
    }


def hiring_change(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in snapshots:
        grouped[str(row["entity_id"]), str(row["snapshot_date"])].add(
            str(row["job_id"])
        )
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
                    "growth_rate": None
                    if previous in (None, 0)
                    else count / previous - 1,
                }
            )
            previous = count
    return output


def series_signature(row: Mapping[str, Any]) -> tuple[str, ...]:
    """Comparison key for a job trend; dimensions must not be mixed."""
    return tuple(
        (
            str(row.get(field) or "unknown")
            for field in (
                "provider",
                "country_code",
                "taxonomy_version",
                "normalizer_version",
                "coverage_cohort",
                "metric",
                "unit",
            )
        )
    )


def coverage_break(rows: Iterable[Mapping[str, Any]]) -> str | None:
    signatures = {series_signature(row) for row in rows}
    return None if len(signatures) <= 1 else "coverage_or_version_break"


def trend_comparison_groups(
    rows: Iterable[Mapping[str, Any]],
) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[series_signature(row)].append(dict(row))
    return {
        key: sorted(
            value,
            key=lambda item: str(
                item.get("collected_at") or item.get("snapshot_date") or ""
            ),
        )
        for key, value in groups.items()
    }


def event_study(
    asset_returns: list[float],
    benchmark_returns: list[float],
    event_index: int,
    windows: tuple[int, ...] = (1, 5, 20),
) -> dict[str, Any]:
    if len(asset_returns) != len(benchmark_returns):
        raise ValueError("Asset and benchmark return series must have equal length")
    abnormal = np.asarray(asset_returns, dtype=float) - np.asarray(
        benchmark_returns, dtype=float
    )
    output: dict[str, Any] = {
        "event_index": event_index,
        "observations": len(abnormal),
        "windows": {},
    }
    for window in windows:
        start, end = (
            max(0, event_index - window),
            min(len(abnormal), event_index + window + 1),
        )
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
    if any((len(values) == 0 for values in arrays)):
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
        DCFScenario("downside", 0.0, 0.1, 0.11, 0.01),
        DCFScenario("base", 0.05, 0.15, 0.09, 0.025),
        DCFScenario("upside", 0.1, 0.2, 0.08, 0.035),
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
            yearly_fcf.append(
                {
                    "year": year,
                    "revenue": projected_revenue,
                    "fcf": fcf,
                    "present_value": pv,
                }
            )
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
                "terminal_value_share": terminal_pv / enterprise_value
                if enterprise_value
                else None,
                "yearly_projection": yearly_fcf,
            }
        )
    return {
        "years": years,
        "scenarios": output,
        "warning": "Scenario output depends on assumptions; it is not a forecast guarantee.",
    }


def guarded_dcf_scenarios(
    revenue: float | None,
    net_debt: float | None,
    shares: float | None,
    *,
    evidence_complete: bool,
    years: int = 5,
) -> dict[str, Any]:
    if not evidence_complete or None in {revenue, net_debt, shares}:
        return {
            "status": "unavailable",
            "reason": "actual_period_unit_currency_evidence_required",
        }
    return {
        "status": "scenario-only",
        "result": dcf_scenarios(
            float(revenue), float(net_debt), float(shares), years=years
        ),
    }


VALUATION_EVIDENCE_FIELDS = (
    "source_url",
    "available_at",
    "unit",
    "currency",
    "period",
    "concept",
)


def _finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def valuation_prerequisites(
    revenue: float | None,
    net_debt: float | None,
    shares: float | None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Explain whether an evidence-bound valuation scenario can be calculated.

    This is a readiness contract, not a valuation calculator.  It deliberately
    separates a missing input from a missing fact lineage so the interactive
    CLI can disable only the unsupported step and explain why.
    """
    evidence = evidence or {}
    values = {"revenue": revenue, "net_debt": net_debt, "shares": shares}
    missing_inputs = [name for name, value in values.items() if value is None]
    invalid_inputs = [
        name
        for name, value in values.items()
        if value is not None and (not _finite_number(value))
    ]
    missing_evidence = [
        name for name in VALUATION_EVIDENCE_FIELDS if not evidence.get(name)
    ]
    observation_kind = evidence.get("observation_kind")
    actual_observation_required = observation_kind not in {None, "actual"}
    reasons = [f"missing_input:{name}" for name in missing_inputs]
    reasons.extend((f"invalid_input:{name}" for name in invalid_inputs))
    reasons.extend((f"missing_evidence:{name}" for name in missing_evidence))
    if actual_observation_required:
        reasons.append("actual_observation_required")
    return {
        "status": "ready" if not reasons else "unavailable",
        "reasons": reasons,
        "missing_inputs": missing_inputs,
        "invalid_inputs": invalid_inputs,
        "missing_evidence": missing_evidence,
        "required_inputs": list(values),
        "required_evidence": list(VALUATION_EVIDENCE_FIELDS),
        "actual_observation_required": actual_observation_required,
        "warning": "A ready scenario remains assumption-bound and is not a forecast or price target.",
    }


def event_study_prerequisites(
    asset_returns: Iterable[float],
    benchmark_returns: Iterable[float],
    event_index: int,
    event_evidence: Mapping[str, Any] | None,
    treated_pre: Iterable[float] | None = None,
    treated_post: Iterable[float] | None = None,
    control_pre: Iterable[float] | None = None,
    control_post: Iterable[float] | None = None,
) -> dict[str, Any]:
    """Explain event-study readiness without upgrading association to causality."""
    asset = list(asset_returns)
    benchmark = list(benchmark_returns)
    evidence = event_evidence or {}
    missing_evidence = [
        name
        for name in ("event_date", "source_url", "available_at")
        if not evidence.get(name)
    ]
    reasons = [f"missing_evidence:{name}" for name in missing_evidence]
    if evidence.get("price_adjustment") == "raw":
        reasons.append("raw_price_series_not_accepted")
    if len(asset) != len(benchmark) or len(asset) < 7:
        reasons.append("insufficient_or_unaligned_return_series")
    if not isinstance(event_index, int) or event_index < 0 or event_index >= len(asset):
        reasons.append("event_index_out_of_range")
    did_inputs = (treated_pre, treated_post, control_pre, control_post)
    did_series = [list(values) if values is not None else [] for values in did_inputs]
    control_complete = all(did_series) and bool(evidence.get("control_signature"))
    if missing_evidence:
        status = "unavailable"
    elif {
        "raw_price_series_not_accepted",
        "insufficient_or_unaligned_return_series",
        "event_index_out_of_range",
    } & set(reasons):
        status = "ineligible"
    else:
        status = "association-only"
    causal_limitations = (
        ["parallel_pre_trends_not_established", "simultaneous_shocks_not_ruled_out"]
        if control_complete
        else ["control_group_or_pre_post_outcomes_missing"]
    )
    return {
        "status": status,
        "reasons": reasons,
        "missing_evidence": missing_evidence,
        "return_series": {
            "asset_observations": len(asset),
            "benchmark_observations": len(benchmark),
            "aligned": len(asset) == len(benchmark),
            "minimum_observations": 7,
        },
        "event_index": event_index,
        "event_study_ready": status == "association-only",
        "did_inputs_present": control_complete,
        "causal_ready": False,
        "causal_limitations": causal_limitations,
        "warning": "Event-study outputs describe association; control data alone does not establish causality.",
    }


DEFAULT_SCORE_WEIGHTS = {
    "financial_health": 0.2,
    "profitability": 0.2,
    "growth_quality": 0.2,
    "valuation": 0.15,
    "macro_industry_fit": 0.1,
    "operations_workforce": 0.1,
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


def calculate_cluster_elasticity_breakdown(
    cohorts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate multi-tier cluster elasticity breakdown and detect Simpson's paradox.

    Each cohort dict should contain:
        - signature: str or ClusterSignature (e.g. 'KR:SOE:p01:REGULAR:ONSITE')
        - name: str (e.g. '한국전력공사 일반정규직')
        - rev_growth: float (e.g. 0.08)
        - hiring_growth: float (e.g. -0.081)
        - weight: float (optional, e.g. active postings or revenue base)
    """
    cohort_results: list[dict[str, Any]] = []
    total_rev_weighted = 0.0
    total_hiring_weighted = 0.0
    total_weight = 0.0
    private_elasticity: float | None = None
    soe_regular_elasticity: float | None = None
    soe_intern_elasticity: float | None = None
    for c in cohorts:
        sig_str = str(c.get("signature") or "ALL:ALL:ALL:ALL:ALL")
        name = str(c.get("name") or sig_str)
        rev_g = float(c.get("rev_growth") or 0.0)
        hire_g = float(c.get("hiring_growth") or 0.0)
        w = float(c.get("weight") or 1.0)
        elas = safe_div(hire_g, rev_g)
        diagnostic: str
        if rev_g > 0 and hire_g > rev_g:
            diagnostic = "aggressive_expansion"
        elif rev_g > 0 and hire_g >= 0:
            diagnostic = "balanced_growth"
        elif rev_g > 0 and hire_g < 0:
            diagnostic = "margin_expansion_hiring_freeze"
        elif rev_g <= 0 and hire_g > 0:
            diagnostic = "speculative_investment"
        else:
            diagnostic = "restructuring_or_contraction"
        cohort_results.append(
            {
                "signature": sig_str,
                "name": name,
                "rev_growth": rev_g,
                "hiring_growth": hire_g,
                "elasticity": elas,
                "diagnostic": diagnostic,
                "weight": w,
            }
        )
        total_rev_weighted += rev_g * w
        total_hiring_weighted += hire_g * w
        total_weight += w
        if ":PRIVATE:" in sig_str:
            private_elasticity = elas
        elif ":SOE:" in sig_str and ":REGULAR:" in sig_str:
            soe_regular_elasticity = elas
        elif ":SOE:" in sig_str and ":INTERN:" in sig_str:
            soe_intern_elasticity = elas
    macro_rev_g = safe_div(total_rev_weighted, total_weight) or 0.0
    macro_hiring_g = safe_div(total_hiring_weighted, total_weight) or 0.0
    macro_elasticity = safe_div(macro_hiring_g, macro_rev_g)
    distortion_index = 0.0
    if private_elasticity is not None and soe_regular_elasticity is not None:
        distortion_index = abs(private_elasticity - soe_regular_elasticity)
    simpson_detected = distortion_index > 0.5
    return {
        "status": "success",
        "macro_rollup": {
            "signature": "KR:ALL:ALL:ALL:ALL",
            "name": "전체 거시 통합 (Macro Roll-up)",
            "rev_growth": macro_rev_g,
            "hiring_growth": macro_hiring_g,
            "elasticity": macro_elasticity,
            "diagnostic": "aggregated_blended",
        },
        "cohorts": cohort_results,
        "simpsons_paradox_detected": simpson_detected,
        "distortion_index": distortion_index,
        "explanation": "심슨의 역설 발생: 사기업은 매출 성장에 맞춰 선제적 채용 확장(고탄력성)을 보이는 반면, 공공부문은 정원 규제로 정규직 채용이 위축(탄력성 0 수렴)되고 청년인턴으로 우회 확충됩니다. 따라서 두 부문을 단일 평균으로 합산하면 진실이 왜곡됩니다."
        if simpson_detected
        else "클러스터 간 유의미한 고용탄력성 왜곡이 발견되지 않았습니다.",
    }


CROSSWALK_FINANCIAL_METRICS: dict[str, dict[str, tuple[str, ...]]] = {
    "KR": {
        "current_assets": (
            "ifrs-full_CurrentAssets",
            "유동자산",
            "CurrentAssets",
            "current_assets",
        ),
        "current_liabilities": (
            "ifrs-full_CurrentLiabilities",
            "유동부채",
            "CurrentLiabilities",
            "current_liabilities",
        ),
        "inventories": (
            "ifrs-full_Inventories",
            "재고자산",
            "Inventories",
            "inventories",
        ),
        "total_liabilities": (
            "ifrs-full_Liabilities",
            "부채총계",
            "Liabilities",
            "total_liabilities",
        ),
        "total_equity": (
            "ifrs-full_Equity",
            "자본총계",
            "Equity",
            "total_equity",
            "equity",
        ),
        "operating_income": (
            "ifrs-full_OperatingIncomeLoss",
            "영업이익",
            "OperatingIncome",
            "operating_income",
        ),
        "interest_expense": (
            "ifrs-full_InterestExpense",
            "이자비용",
            "InterestExpense",
            "interest_expense",
        ),
        "revenue": ("ifrs-full_Revenue", "매출액", "Revenue", "revenue"),
    },
    "US": {
        "current_assets": ("AssetsCurrent", "CurrentAssets", "current_assets"),
        "current_liabilities": (
            "LiabilitiesCurrent",
            "CurrentLiabilities",
            "current_liabilities",
        ),
        "inventories": ("InventoryNet", "Inventories", "inventories"),
        "total_liabilities": ("Liabilities", "TotalLiabilities", "total_liabilities"),
        "total_equity": ("StockholdersEquity", "TotalEquity", "equity", "total_equity"),
        "operating_income": (
            "OperatingIncomeLoss",
            "OperatingIncome",
            "operating_income",
        ),
        "interest_expense": (
            "InterestExpense",
            "InterestAndDebtExpense",
            "interest_expense",
        ),
        "revenue": (
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "revenue",
        ),
    },
    "CZ": {
        "current_assets": (
            "Oběžná aktiva",
            "Aktiva celkem - Oběžná aktiva",
            "current_assets",
        ),
        "current_liabilities": ("Krátkodobé závazky", "current_liabilities"),
        "inventories": ("Zásoby", "inventories"),
        "total_liabilities": ("Cizí zdroje", "total_liabilities"),
        "total_equity": ("Vlastní kapitál", "total_equity", "equity"),
        "operating_income": ("Provozní výsledek hospodaření", "operating_income"),
        "interest_expense": ("Nákladové úroky", "interest_expense"),
        "revenue": ("Tržby z prodeje výrobků a služeb", "Tržby celkem", "revenue"),
    },
}


def _extract_canonical_fact(
    raw: Mapping[str, Any], aliases: tuple[str, ...]
) -> float | None:
    for alias in aliases:
        if alias in raw and raw[alias] is not None:
            try:
                val = float(raw[alias])
                if math.isfinite(val):
                    return val
            except (ValueError, TypeError):
                continue
    return None


def reconcile_cross_national_financials(
    raw_facts: Mapping[str, Any],
    country_code: str = "KR",
    accounting_standard: str | None = None,
) -> dict[str, Any]:
    """Reconcile disparate accounting taxonomies (K-IFRS, US-GAAP, Czech CAS) into 4 core ratios.

    1. Current Ratio = Current Assets / Current Liabilities
    2. Quick Ratio = (Current Assets - Inventory) / Current Liabilities
    3. Debt to Equity = Total Liabilities / Total Equity
    4. Interest Coverage = Operating Income / Interest Expense
    """
    country = (country_code or "KR").upper()
    mapping = CROSSWALK_FINANCIAL_METRICS.get(
        country, CROSSWALK_FINANCIAL_METRICS["KR"]
    )
    ca = _extract_canonical_fact(raw_facts, mapping["current_assets"])
    cl = _extract_canonical_fact(raw_facts, mapping["current_liabilities"])
    inv = _extract_canonical_fact(raw_facts, mapping["inventories"]) or 0.0
    tl = _extract_canonical_fact(raw_facts, mapping["total_liabilities"])
    eq = _extract_canonical_fact(raw_facts, mapping["total_equity"])
    ebit = _extract_canonical_fact(raw_facts, mapping["operating_income"])
    inte = _extract_canonical_fact(raw_facts, mapping["interest_expense"])
    rev = _extract_canonical_fact(raw_facts, mapping["revenue"])
    current_ratio = safe_div(ca, cl)
    quick_ratio = safe_div(ca - inv if ca is not None else None, cl)
    debt_to_equity = safe_div(tl, eq)
    interest_coverage = safe_div(ebit, inte)
    prior_cr = raw_facts.get("prior_current_ratio")
    discontinuity_flag = False
    if current_ratio is not None and prior_cr is not None and (prior_cr > 0):
        if abs(current_ratio / prior_cr - 1.0) > 0.5:
            discontinuity_flag = True
    return {
        "country_code": country,
        "accounting_standard": accounting_standard
        or ("K-IFRS" if country == "KR" else "US-GAAP" if country == "US" else "CAS"),
        "current_assets": ca,
        "current_liabilities": cl,
        "inventories": inv,
        "total_liabilities": tl,
        "total_equity": eq,
        "operating_income": ebit,
        "interest_expense": inte,
        "revenue": rev,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "debt_to_equity": debt_to_equity,
        "interest_coverage": interest_coverage,
        "discontinuity_flag": discontinuity_flag,
    }


def calculate_dynamic_wacc(
    base_rate: float,
    beta: float = 1.0,
    equity_risk_premium: float = 0.055,
    credit_spread: float = 0.015,
    tax_rate: float = 0.22,
    debt_to_equity: float = 0.5,
) -> dict[str, float]:
    """Calculate Dynamic WACC dynamically bound to macroeconomic base rate (ECOS/FRED).

    Ke = base_rate + beta * ERP
    Kd = base_rate + credit_spread
    D/V = D/E / (1 + D/E)
    E/V = 1 / (1 + D/E)
    WACC = (E/V) * Ke + (D/V) * Kd * (1 - tax_rate)
    """
    ke = base_rate + beta * equity_risk_premium
    kd = base_rate + credit_spread
    weight_debt = debt_to_equity / (1.0 + debt_to_equity)
    weight_equity = 1.0 / (1.0 + debt_to_equity)
    after_tax_kd = kd * (1.0 - tax_rate)
    wacc = weight_equity * ke + weight_debt * after_tax_kd
    return {
        "base_rate": base_rate,
        "cost_of_equity": ke,
        "cost_of_debt": kd,
        "after_tax_cost_of_debt": after_tax_kd,
        "weight_equity": weight_equity,
        "weight_debt": weight_debt,
        "wacc": wacc,
    }


def dynamic_macro_linked_dcf(
    revenue: float,
    net_debt: float,
    shares: float,
    base_rate: float = 0.0325,
    beta: float = 1.0,
    fx_change_pct: float = 0.0,
    is_exporter: bool = True,
    base_fcf_margin: float = 0.15,
    terminal_growth: float = 0.02,
    years: int = 5,
) -> dict[str, Any]:
    """Compute DCF enterprise value where WACC and FCF margin dynamically react to macro shocks.

    - Interest Rate Shock -> WACC alters discount rate
    - FX Shock -> FCF margin adjusted by elasticity (+0.25 for exporters, -0.20 for importers)
    """
    wacc_info = calculate_dynamic_wacc(base_rate=base_rate, beta=beta)
    discount_rate = wacc_info["wacc"]
    fx_elasticity = 0.25 if is_exporter else -0.2
    adjusted_fcf_margin = max(
        0.01, base_fcf_margin * (1.0 + fx_elasticity * fx_change_pct)
    )
    scenarios = [
        DCFScenario(
            "downside",
            0.0,
            adjusted_fcf_margin * 0.8,
            discount_rate + 0.015,
            max(0.005, terminal_growth - 0.01),
        ),
        DCFScenario("base", 0.05, adjusted_fcf_margin, discount_rate, terminal_growth),
        DCFScenario(
            "upside",
            0.1,
            adjusted_fcf_margin * 1.2,
            max(discount_rate - 0.01, terminal_growth + 0.01),
            terminal_growth + 0.01,
        ),
    ]
    base_dcf = dcf_scenarios(
        revenue=revenue,
        net_debt=net_debt,
        shares=shares,
        scenarios=scenarios,
        years=years,
    )
    base_dcf["macro_inputs"] = {
        "base_rate": base_rate,
        "dynamic_wacc": discount_rate,
        "fx_change_pct": fx_change_pct,
        "adjusted_fcf_margin": adjusted_fcf_margin,
    }
    return base_dcf


def verify_parallel_trends(
    treated_pre_series: list[float], control_pre_series: list[float]
) -> dict[str, Any]:
    """Test parallel pre-trends assumption before treatment (H0: slope_diff = 0).

    If p_value > 0.05, parallel pre-trend holds (DiD is econometrically valid).
    """
    t_len = min(len(treated_pre_series), len(control_pre_series))
    if t_len < 2:
        return {"valid": False, "reason": "insufficient_pre_periods", "p_value": None}
    x = np.arange(t_len)
    y_diff = np.array(treated_pre_series[:t_len]) - np.array(control_pre_series[:t_len])
    slope, intercept = np.polyfit(x, y_diff, 1)
    y_pred = slope * x + intercept
    residuals = y_diff - y_pred
    dof = max(1, t_len - 2)
    s_err = np.sqrt(np.sum(residuals**2) / dof) / np.sqrt(
        np.sum((x - np.mean(x)) ** 2) or 1.0
    )
    t_stat = slope / s_err if s_err > 0 else 0.0
    p_val = float(2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0)))))
    return {
        "valid": p_val > 0.05,
        "slope_difference": float(slope),
        "t_statistic": float(t_stat),
        "p_value": p_val,
        "interpretation": "Parallel pre-trends hold (DiD valid)"
        if p_val > 0.05
        else "Parallel pre-trends violated (biased)",
    }


def panel_difference_in_differences(
    cohort_panel_rows: list[dict[str, Any]],
    metric_key: str = "ebit_per_employee",
    treated_key: str = "is_treated",
    post_key: str = "is_post",
) -> dict[str, Any]:
    """Perform Panel Difference-in-Differences with 4 cell means and t-statistic.

    delta_DiD = (Mean_Treated_Post - Mean_Treated_Pre) - (Mean_Control_Post - Mean_Control_Pre)
    """
    cells = {
        ("treat", "pre"): [],
        ("treat", "post"): [],
        ("ctrl", "pre"): [],
        ("ctrl", "post"): [],
    }
    for row in cohort_panel_rows:
        val = row.get(metric_key)
        if val is None or not math.isfinite(float(val)):
            continue
        val_f = float(val)
        is_tr = bool(row.get(treated_key))
        is_po = bool(row.get(post_key))
        group = "treat" if is_tr else "ctrl"
        period = "post" if is_po else "pre"
        cells[group, period].append(val_f)
    if any((len(v) == 0 for v in cells.values())):
        raise ValueError(
            "All 4 DiD panel cells (treated/control x pre/post) require non-empty observations"
        )
    means = {k: float(np.mean(v)) for k, v in cells.items()}
    vars_ = {
        k: float(np.var(v, ddof=1) if len(v) > 1 else 0.0) for k, v in cells.items()
    }
    ns = {k: len(v) for k, v in cells.items()}
    treat_change = means["treat", "post"] - means["treat", "pre"]
    ctrl_change = means["ctrl", "post"] - means["ctrl", "pre"]
    delta_did = treat_change - ctrl_change
    se_did = math.sqrt(sum((vars_[k] / ns[k] for k in cells if ns[k] > 0)))
    t_stat = delta_did / se_did if se_did > 0 else 0.0
    p_val = float(2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0)))))
    return {
        "metric": metric_key,
        "treated_pre_mean": means["treat", "pre"],
        "treated_post_mean": means["treat", "post"],
        "control_pre_mean": means["ctrl", "pre"],
        "control_post_mean": means["ctrl", "post"],
        "treated_change": treat_change,
        "control_change": ctrl_change,
        "did_estimate": delta_did,
        "standard_error": se_did,
        "t_statistic": t_stat,
        "p_value": p_val,
        "is_significant_1pct": p_val < 0.01,
        "is_significant_5pct": p_val < 0.05,
    }
