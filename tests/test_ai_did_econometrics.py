import pytest
from company_intel.analytics import verify_parallel_trends, panel_difference_in_differences
from company_intel.analysis_service import evaluate_ai_adoption_impact


def test_parallel_trends_valid():
    # Treated and control moving with identical slope (slope diff = 0)
    treated_pre = [10.0, 11.0, 12.0, 13.0]
    control_pre = [5.0, 6.0, 7.0, 8.0]
    res = verify_parallel_trends(treated_pre, control_pre)
    assert res["valid"] is True
    assert res["slope_difference"] == pytest.approx(0.0, abs=1e-5)
    assert res["p_value"] > 0.05


def test_parallel_trends_divergent():
    # Treated rising much faster than control in pre-treatment (violated)
    treated_pre = [10.0, 15.0, 22.0, 31.0]
    control_pre = [10.0, 10.5, 11.0, 11.5]
    res = verify_parallel_trends(treated_pre, control_pre)
    assert res["valid"] is False
    assert res["p_value"] < 0.05


def test_panel_difference_in_differences_significance():
    # 4 cell panel rows
    panel_rows = [
        {"entity_id": "T1", "is_treated": True, "is_post": False, "ebit_margin": 10.0},
        {"entity_id": "T2", "is_treated": True, "is_post": False, "ebit_margin": 10.5},
        {"entity_id": "T1", "is_treated": True, "is_post": True, "ebit_margin": 25.0},
        {"entity_id": "T2", "is_treated": True, "is_post": True, "ebit_margin": 26.0},
        {"entity_id": "C1", "is_treated": False, "is_post": False, "ebit_margin": 10.0},
        {"entity_id": "C2", "is_treated": False, "is_post": False, "ebit_margin": 10.2},
        {"entity_id": "C1", "is_treated": False, "is_post": True, "ebit_margin": 12.0},
        {"entity_id": "C2", "is_treated": False, "is_post": True, "ebit_margin": 12.2},
    ]
    # Treated change: ~25.5 - 10.25 = 15.25
    # Control change: ~12.1 - 10.1 = 2.0
    # DiD = 13.25
    did = panel_difference_in_differences(panel_rows, metric_key="ebit_margin")
    assert did["did_estimate"] == pytest.approx(13.25, abs=0.1)
    assert did["t_statistic"] > 2.0
    assert did["is_significant_5pct"] is True


def test_evaluate_ai_adoption_impact_suite():
    res = evaluate_ai_adoption_impact()
    assert res["status"] == "success"
    assert "2022-11-30" in res["treatment_event"]
    assert res["parallel_trends_test"]["valid"] is True
    assert res["labor_productivity_did"]["did_estimate"] > 3.0 # Substantial EBIT improvement
    assert res["sw_developer_demand_did"]["did_estimate"] > 0 # Developer demand expands
    assert res["admin_role_demand_did"]["did_estimate"] < 0   # Admin demand contracts
    assert "executive_summary" in res
