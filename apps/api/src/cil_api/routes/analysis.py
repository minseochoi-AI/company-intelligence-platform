"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_api.schemas import AiEventEvidenceRequest
from cil_api.schemas import DcfRequest
from cil_api.schemas import DidRequest
from cil_api.schemas import EventStudyRequest
from cil_api.schemas import EvidenceTimelineRequest
from cil_api.schemas import FutureScoreRequest
from cil_api.schemas import RankingRequest
from cil_api.schemas import ValuationEvidenceRequest
from cil_application.analysis.service import build_company_timeline
from cil_application.analysis.service import evaluate_ai_event
from cil_application.analysis.service import evaluate_job_trends
from cil_application.analysis.service import evaluate_valuation_scenarios
from cil_domain.finance.analytics import dcf_scenarios
from cil_domain.finance.analytics import difference_in_differences
from cil_domain.finance.analytics import event_study
from cil_domain.finance.analytics import event_study_prerequisites
from cil_domain.finance.analytics import future_value_score
from cil_domain.finance.analytics import rank_companies
from cil_domain.finance.analytics import valuation_prerequisites
from typing import Any


@app.post("/rankings")
def rankings(request: RankingRequest) -> list[dict[str, Any]]:
    return rank_companies(request.rows, request.weights, request.directions)


@app.post("/analysis/event-study")
def calculate_event_study(request: EventStudyRequest) -> dict[str, Any]:
    return event_study(
        request.asset_returns,
        request.benchmark_returns,
        request.event_index,
        tuple(request.windows),
    )


@app.post("/analysis/did")
def calculate_did(request: DidRequest) -> dict[str, Any]:
    return difference_in_differences(
        request.treated_pre,
        request.treated_post,
        request.control_pre,
        request.control_post,
    )


@app.post("/analysis/dcf")
def calculate_dcf(request: DcfRequest) -> dict[str, Any]:
    return dcf_scenarios(
        request.revenue, request.net_debt, request.shares, years=request.years
    )


@app.post("/analysis/future-score")
def calculate_future_score(request: FutureScoreRequest) -> dict[str, Any]:
    return future_value_score(request.components, request.confidence)


@app.post("/v1/company-timeline")
def evidence_timeline(request: EvidenceTimelineRequest) -> dict[str, Any]:
    result = build_company_timeline(
        request.rows, entity_id=request.entity_id, as_of=request.as_of
    )
    return {
        "timeline": result["timeline"]
        .astype(object)
        .where(result["timeline"].notna(), None)
        .to_dict("records"),
        "exclusions": result["exclusions"]
        .astype(object)
        .where(result["exclusions"].notna(), None)
        .to_dict("records"),
        "metadata": result["metadata"],
    }


@app.post("/v1/analysis/valuation-scenarios")
def valuation_scenarios(request: ValuationEvidenceRequest) -> dict[str, Any]:
    prerequisites = valuation_prerequisites(
        request.revenue, request.net_debt, request.shares, request.evidence
    )
    if prerequisites["status"] != "ready":
        return {"status": prerequisites["status"], "prerequisites": prerequisites}
    result = evaluate_valuation_scenarios(
        revenue=request.revenue,
        net_debt=request.net_debt,
        shares=request.shares,
        evidence=request.evidence,
        years=request.years,
    )
    return {**result, "prerequisites": prerequisites}


@app.post("/v1/analysis/ai-event")
def ai_event_analysis(request: AiEventEvidenceRequest) -> dict[str, Any]:
    value = request.model_dump()
    prerequisites = event_study_prerequisites(
        value["asset_returns"],
        value["benchmark_returns"],
        value["event_index"],
        value["event_evidence"],
        value.get("treated_pre"),
        value.get("treated_post"),
        value.get("control_pre"),
        value.get("control_post"),
    )
    if prerequisites["status"] != "association-only":
        return {"status": prerequisites["status"], "prerequisites": prerequisites}
    return {**evaluate_ai_event(**value), "prerequisites": prerequisites}
