import math

from cil_domain.finance.analytics import dcf_scenarios, difference_in_differences, event_study_prerequisites, event_study, financial_metrics, future_value_score, hiring_change, rank_companies, valuation_prerequisites, coverage_break, series_signature


def test_financial_metrics_cashflow_and_margins():
    result = financial_metrics(
        {
            "revenue": 100,
            "revenue_previous": 80,
            "gross_profit": 40,
            "operating_income": 20,
            "net_income": 10,
            "cfo": 15,
            "capex": 5,
        }
    )
    assert math.isclose(result["revenue_growth"], 0.25)
    assert math.isclose(result["operating_margin"], 0.2)
    assert math.isclose(result["fcf"], 10)
    assert math.isclose(result["fcf_margin"], 0.1)


def test_financial_metrics_liquidity_and_solvency():
    result = financial_metrics(
        {
            "current_assets": 200,
            "inventory": 50,
            "cash": 60,
            "current_liabilities": 100,
            "debt": 150,
            "equity": 250,
            "cfo": 30,
        }
    )
    assert math.isclose(result["current_ratio"], 2.0)
    assert math.isclose(result["quick_ratio"], 1.5)
    assert math.isclose(result["cash_ratio"], 0.6)
    assert math.isclose(result["debt_to_equity"], 0.6)
    assert math.isclose(result["operating_cash_flow_ratio"], 0.3)
    assert math.isclose(result["working_capital"], 100.0)


def test_ranking_is_peer_scoped_and_lower_leverage_is_better():
    rows = [
        {
            "entity_id": "A",
            "country": "US",
            "industry": "SW",
            "size_bucket": "L",
            "growth": 0.2,
            "leverage": 0.2,
        },
        {
            "entity_id": "B",
            "country": "US",
            "industry": "SW",
            "size_bucket": "L",
            "growth": 0.1,
            "leverage": 1.0,
        },
    ]
    ranked = rank_companies(rows, {"growth": 0.5, "leverage": 0.5}, {"leverage": False})
    assert ranked[0]["entity_id"] == "A"
    assert ranked[0]["peer_count"] == 2


def test_event_did_dcf_future_score():
    event = event_study([0.02, 0.03, 0.01], [0.01, 0.01, 0.0], 1, (1,))
    assert math.isclose(event["windows"]["[-1,+1]"]["car"], 0.04)
    did = difference_in_differences([10, 10], [14, 14], [10, 10], [11, 11])
    assert math.isclose(did["did_estimate"], 3.0)
    dcf = dcf_scenarios(100, 0, 10)
    assert len(dcf["scenarios"]) == 3
    score = future_value_score({"financial_health": 80, "profitability": 60})
    assert 60 <= score["future_value_score"] <= 80
    assert score["data_confidence"] < 1


def test_hiring_snapshots_do_not_claim_hires():
    result = hiring_change(
        [
            {"entity_id": "A", "snapshot_date": "2026-01-01", "job_id": "1"},
            {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "1"},
            {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "2"},
        ]
    )
    assert result[-1]["open_postings"] == 2
    assert result[-1]["absolute_change"] == 1


def test_analysis_prerequisites_return_deterministic_readiness_reasons():
    valuation = valuation_prerequisites(
        100,
        None,
        10,
        {"source_url": "https://evidence.example", "available_at": "2026-01-01"},
    )
    assert valuation["status"] == "unavailable"
    assert valuation["reasons"] == [
        "missing_input:net_debt",
        "missing_evidence:unit",
        "missing_evidence:currency",
        "missing_evidence:period",
        "missing_evidence:concept",
    ]

    event = event_study_prerequisites(
        [0.0] * 7,
        [0.0] * 7,
        3,
        {"event_date": "2026-01-01", "source_url": "https://evidence.example", "available_at": "2026-01-02"},
    )
    assert event["status"] == "association-only"
    assert event["causal_ready"] is False
    assert event["causal_limitations"] == ["control_group_or_pre_post_outcomes_missing"]

    raw_price_event = event_study_prerequisites(
        [0.0] * 7,
        [0.0] * 7,
        3,
        {
            "event_date": "2026-01-01",
            "source_url": "https://evidence.example",
            "available_at": "2026-01-02",
            "price_adjustment": "raw",
        },
    )
    assert raw_price_event["status"] == "ineligible"
    assert raw_price_event["reasons"] == ["raw_price_series_not_accepted"]


def test_job_series_signature_detects_coverage_break():
    first = {"provider": "mpsv", "country_code": "CZ", "taxonomy_version": "1", "normalizer_version": "1", "coverage_cohort": "all", "metric": "active_postings", "unit": "postings"}
    second = {**first, "coverage_cohort": "partial"}
    assert series_signature(first) != series_signature(second)
    assert coverage_break([first, second]) == "coverage_or_version_break"
