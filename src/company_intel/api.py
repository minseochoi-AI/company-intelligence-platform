from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    future_value_score,
    rank_companies,
)
from .config import Settings
from .warehouse import Warehouse

app = FastAPI(title="Company Intelligence API", version="0.1.0")


class RankingRequest(BaseModel):
    rows: list[dict[str, Any]]
    weights: dict[str, float]
    directions: dict[str, bool] = Field(default_factory=dict)


class EventStudyRequest(BaseModel):
    asset_returns: list[float]
    benchmark_returns: list[float]
    event_index: int
    windows: list[int] = [1, 5, 20]


class DidRequest(BaseModel):
    treated_pre: list[float]
    treated_post: list[float]
    control_pre: list[float]
    control_post: list[float]


class DcfRequest(BaseModel):
    revenue: float
    net_debt: float
    shares: float
    years: int = 5


class FutureScoreRequest(BaseModel):
    components: dict[str, float | None]
    confidence: dict[str, float] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/validation/latest")
def latest_validation() -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    path = settings.artifact_dir / "validation_results.json"
    if not path.exists():
        raise HTTPException(404, "Run company-intel validate first")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/rankings")
def rankings(request: RankingRequest) -> list[dict[str, Any]]:
    return rank_companies(request.rows, request.weights, request.directions)


@app.post("/analysis/event-study")
def calculate_event_study(request: EventStudyRequest) -> dict[str, Any]:
    return event_study(
        request.asset_returns, request.benchmark_returns, request.event_index, tuple(request.windows)
    )


@app.post("/analysis/did")
def calculate_did(request: DidRequest) -> dict[str, Any]:
    return difference_in_differences(
        request.treated_pre, request.treated_post, request.control_pre, request.control_post
    )


@app.post("/analysis/dcf")
def calculate_dcf(request: DcfRequest) -> dict[str, Any]:
    return dcf_scenarios(request.revenue, request.net_debt, request.shares, years=request.years)


@app.post("/analysis/future-score")
def calculate_future_score(request: FutureScoreRequest) -> dict[str, Any]:
    return future_value_score(request.components, request.confidence)


@app.get("/company/{entity_id}/timeline")
def company_timeline(entity_id: str) -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    warehouse = Warehouse(settings)
    try:
        financials = warehouse.query(
            "SELECT * FROM financial_fact WHERE entity_id=? ORDER BY available_at, period_end", [entity_id]
        )
        workforce = warehouse.query(
            "SELECT * FROM workforce_fact WHERE entity_id=? ORDER BY available_at, period_end", [entity_id]
        )
        events = warehouse.query(
            "SELECT * FROM company_event WHERE entity_id=? ORDER BY available_at, event_date", [entity_id]
        )
    except Exception as error:
        raise HTTPException(503, str(error)) from error
    return {"entity_id": entity_id, "financials": financials, "workforce": workforce, "events": events}
