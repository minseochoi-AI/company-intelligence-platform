from __future__ import annotations

import json
from typing import Any

from .analytics import financial_metrics, future_value_score
from .config import Settings
from .evidence import write_json

DART_CONCEPTS = {
    "revenue": ("IS", "ifrs-full_Revenue"),
    "operating_income": ("IS", "dart_OperatingIncomeLoss"),
    "net_income": ("IS", "ifrs-full_ProfitLoss"),
    "cfo": ("CF", "ifrs-full_CashFlowsFromUsedInOperatingActivities"),
    "capex": ("CF", "ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"),
    "cash": ("BS", "ifrs-full_CashAndCashEquivalents"),
    "current_assets": ("BS", "ifrs-full_CurrentAssets"),
    "current_liabilities": ("BS", "ifrs-full_CurrentLiabilities"),
    "liabilities": ("BS", "ifrs-full_Liabilities"),
    "equity": ("BS", "ifrs-full_Equity"),
}


def _load(settings: Settings, name: str) -> dict[str, Any] | None:
    path = settings.artifact_dir / "normalized" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def actual_analysis(settings: Settings) -> dict[str, Any]:
    output: dict[str, Any] = {"generated_from": "runtime normalized API responses"}
    dart = _load(settings, "opendart_samsung_financials")
    if dart:
        indexed = {
            (fact.get("statement"), fact.get("account_id")): fact
            for fact in dart["data"].get("financial_facts", [])
        }
        current: dict[str, float | None] = {}
        previous: dict[str, float | None] = {}
        evidence = {}
        for name, key in DART_CONCEPTS.items():
            fact = indexed.get(key, {})
            current[name] = fact.get("current_amount")
            previous[name] = fact.get("previous_amount")
            evidence[name] = {"statement": key[0], "concept_id": key[1], "receipt_no": fact.get("receipt_no")}
        current["revenue_previous"] = previous.get("revenue")
        current_metrics = financial_metrics(current)
        previous["revenue_previous"] = None
        previous_metrics = financial_metrics(previous)
        growth_score = None
        if current_metrics.get("revenue_growth") is not None:
            growth_score = min(max(50 + current_metrics["revenue_growth"] * 250, 0), 100)
        profitability_score = None
        if current_metrics.get("operating_margin") is not None:
            profitability_score = min(max(current_metrics["operating_margin"] * 400, 0), 100)
        preliminary_score = future_value_score(
            {"growth_quality": growth_score, "profitability": profitability_score},
            {"growth_quality": 0.5, "profitability": 0.5},
        )
        output["samsung_2025"] = {
            "entity_id": "DART:00126380",
            "report_year": dart["data"].get("financial_facts", [{}])[0].get("report_year"),
            "facts_current_krw": current,
            "facts_previous_krw": previous,
            "metrics_current": current_metrics,
            "metrics_previous": previous_metrics,
            "preliminary_partial_score": preliminary_score,
            "score_warning": "Only growth/profitability components are populated; no peer ranking or market valuation is included.",
            "evidence": evidence,
        }

    fred = _load(settings, "fred_federal_funds_rate")
    ecos = _load(settings, "ecos_korea_base_rate")
    alpha = _load(settings, "alphavantage_ibm_daily")
    output["macro_market_snapshot"] = {
        "fred_latest": (fred or {}).get("data", {}).get("observations", [])[-1:] or None,
        "ecos_latest": (ecos or {}).get("data", {}).get("observations", [])[-1:] or None,
        "ibm_latest": (alpha or {}).get("data", {}).get("prices", [])[:1] or None,
    }
    jobs = {}
    for name in ("greenhouse_airtable", "lever_spotify"):
        payload = _load(settings, name)
        if payload:
            jobs[name] = {
                "snapshot_at": payload["collected_at"],
                "open_posting_count": payload["data"].get("job_count"),
                "change": None,
                "note": "First local snapshot; change becomes measurable after later snapshots.",
            }
    output["job_demand_baseline"] = jobs
    output_path = settings.artifact_dir / "actual_analysis.json"
    write_json(output_path, output)
    return output
