from company_intel.analysis_service import (
    build_company_timeline,
    compare_revenue_and_hiring_trends,
    evaluate_ai_event,
    evaluate_valuation_scenarios,
    evaluate_job_trends,
)


def test_point_in_time_and_analysis_limits() -> None:
    result = build_company_timeline([
        {"entity_id": "A", "axis": "financial", "period_end": "2025-12-31", "available_at": "2026-02-01", "value": 10},
        {"entity_id": "A", "axis": "macro", "observation_date": "2026-01-01", "available_at": "2026-06-01", "value": 2},
    ], entity_id="A", as_of="2026-03-01")
    assert list(result["timeline"]["observation_axis"]) == ["financial"]
    assert list(result["exclusions"]["exclusion_reason"]) == ["not_available_as_of"]

    unavailable = evaluate_valuation_scenarios(revenue=100, net_debt=10, shares=10, evidence={"source_url": None})
    assert unavailable["status"] == "unavailable"
    event = evaluate_ai_event(asset_returns=[0.0] * 7, benchmark_returns=[0.0] * 7, event_index=3, event_evidence={"event_date": "2026-01-01", "source_url": "https://e", "available_at": "2026-01-01"})
    assert event["status"] == "association-only"
    assert event["causal_ready"] is False


def test_raw_market_prices_and_projections_are_rejected_for_evidence_analysis() -> None:
    valuation = evaluate_valuation_scenarios(revenue=10, net_debt=1, shares=1, evidence={"source_url": "https://x", "available_at": "2026-01-01", "unit": "USD", "currency": "USD", "period": "2025", "concept": "revenue", "observation_kind": "projection"})
    assert valuation["status"] == "unavailable"
    event = evaluate_ai_event(asset_returns=[0.0] * 7, benchmark_returns=[0.0] * 7, event_index=3, event_evidence={"event_date": "2026-01-01", "source_url": "https://e", "available_at": "2026-01-01", "price_adjustment": "raw"})
    assert event["status"] == "ineligible"


def test_multi_axis_timeline_groups_keep_incompatible_signatures_independent() -> None:
    result = build_company_timeline(
        [
            {
                "entity_id": "A",
                "axis": "financial",
                "series_id": "revenue",
                "unit": "USD",
                "currency": "USD",
                "frequency": "annual",
                "adjustment": "reported",
                "period_end": "2025-12-31",
                "available_at": "2026-02-01",
            },
            {
                "entity_id": "A",
                "axis": "market",
                "series_id": "close",
                "unit": "USD/share",
                "currency": "USD",
                "frequency": "daily",
                "adjustment": "adjusted",
                "observation_date": "2026-01-02",
                "available_at": "2026-01-02",
            },
            {
                "entity_id": "A",
                "axis": "macro",
                "series_id": "policy_rate",
                "unit": "percent",
                "currency": None,
                "frequency": "monthly",
                "adjustment": "seasonally_adjusted",
                "observation_date": "2026-01-01",
                "available_at": "2026-02-01",
            },
            {
                "entity_id": "A",
                "axis": "financial",
                "series_id": "revenue",
                "unit": "EUR",
                "currency": "EUR",
                "frequency": "annual",
                "adjustment": "reported",
                "period_end": "2024-12-31",
                "available_at": "2025-02-01",
            },
        ],
        entity_id="A",
        as_of="2026-03-01",
    )

    assert len(result["timeline"]) == 4
    assert result["timeline"]["series_group_id"].nunique() == 4
    assert len(result["metadata"]["series_groups"]) == 4
    assert result["metadata"]["alignment"]["key"] == "observation_date"
    assert "incompatible_series_signature" not in set(result["exclusions"].get("exclusion_reason", []))


def test_job_trend_unavailable_reason_is_exposed():
    result = evaluate_job_trends([{"snapshot_id": "one", "collected_at": "2026-09-01", "provider": "mpsv", "jobs": []}])
    assert result["status"] == "ineligible"
    assert result["eligibility"]["reason"] == "insufficient_history"


def test_compare_revenue_and_hiring_trends():
    revenue_records = [
        {"observation_date": "2026-01-31", "revenue": 1000000.0},
        {"observation_date": "2026-02-28", "revenue": 1200000.0},
    ]
    job_snapshots = [
        {
            "snapshot_id": "snap-1",
            "collected_at": "2026-01-15T00:00:00Z",
            "provider": "mpsv_cz",
            "taxonomy_version": "1.0",
            "normalizer_version": "1.0",
            "coverage_cohort": "full",
            "jobs": [{"provider": "mpsv_cz", "job_id": "job-1"}],
        },
        {
            "snapshot_id": "snap-2",
            "collected_at": "2026-02-15T00:00:00Z",
            "provider": "mpsv_cz",
            "taxonomy_version": "1.0",
            "normalizer_version": "1.0",
            "coverage_cohort": "full",
            "jobs": [
                {"provider": "mpsv_cz", "job_id": "job-1"},
                {"provider": "mpsv_cz", "job_id": "job-2"},
            ],
        },
    ]
    comparison = compare_revenue_and_hiring_trends(revenue_records, job_snapshots)
    assert comparison["status"] == "success"
    assert comparison["periods_count"] == 2
    assert comparison["aligned_series"][0]["period"] == "2026-01"
    assert comparison["aligned_series"][0]["revenue"] == 1000000.0
    assert comparison["aligned_series"][0]["active_postings"] == 1

    second = comparison["aligned_series"][1]
    assert second["period"] == "2026-02"
    assert second["revenue"] == 1200000.0
    assert second["active_postings"] == 2
    assert round(second["revenue_growth"], 2) == 0.20
    assert round(second["hiring_growth"], 2) == 1.00
    assert round(second["hiring_elasticity"], 1) == 5.0
    assert second["diagnostic"] == "aggressive_expansion"

