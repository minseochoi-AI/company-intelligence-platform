import pytest
from cil_domain.observations.normalization import normalize_to_calendar_quarter, calculate_quarterly_flow
from cil_domain.finance.analytics import reconcile_cross_national_financials, CROSSWALK_FINANCIAL_METRICS


def test_calendar_quarter_normalization_multi_country():
    # 1. Apple (US) Fiscal Year ending in September
    # FY24 Q1 ended 2023-12-30 -> Calendar Q4 2023
    assert normalize_to_calendar_quarter("2023-12-30") == "CY2023-Q4"
    # FY24 Q2 ended 2024-03-30 -> Calendar Q1 2024
    assert normalize_to_calendar_quarter("2024-03-30") == "CY2024-Q1"
    # FY24 Q3 ended 2024-06-29 -> Calendar Q2 2024
    assert normalize_to_calendar_quarter("2024-06-29") == "CY2024-Q2"
    # FY24 Q4 ended 2024-09-28 -> Calendar Q3 2024
    assert normalize_to_calendar_quarter("2024-09-28") == "CY2024-Q3"

    # 2. Kakao / Samsung (KR) 12-month calendar fiscal year
    assert normalize_to_calendar_quarter("2023-12-31") == "CY2023-Q4"
    assert normalize_to_calendar_quarter("2024-03-31") == "CY2024-Q1"
    assert normalize_to_calendar_quarter("20240930") == "CY2024-Q3"

    # 3. Invalid inputs
    with pytest.raises(ValueError):
        normalize_to_calendar_quarter("")
    with pytest.raises(ValueError):
        normalize_to_calendar_quarter("2024-15-30")


def test_calculate_quarterly_flow_subtraction():
    # YTD Cumulative series
    ytd = [
        {"calendar_quarter": "CY2024-Q1", "cumulative_amount": 100.0},
        {"calendar_quarter": "CY2024-Q2", "cumulative_amount": 250.0},
        {"calendar_quarter": "CY2024-Q3", "cumulative_amount": 420.0},
        {"calendar_quarter": "CY2024-Q4", "cumulative_amount": 600.0},
    ]
    flows = calculate_quarterly_flow(ytd)
    assert len(flows) == 4
    assert flows[0]["quarterly_flow"] == 100.0  # Q1 = YTD Q1
    assert flows[1]["quarterly_flow"] == 150.0  # Q2 = 250 - 100
    assert flows[2]["quarterly_flow"] == 170.0  # Q3 = 420 - 250
    assert flows[3]["quarterly_flow"] == 180.0  # Q4 = 600 - 420


def test_reconcile_cross_national_financials_kr():
    # Korea DART K-IFRS facts
    kr_facts = {
        "ifrs-full_CurrentAssets": 2000000000.0,
        "ifrs-full_CurrentLiabilities": 1000000000.0,
        "ifrs-full_Inventories": 200000000.0,
        "ifrs-full_Liabilities": 1500000000.0,
        "ifrs-full_Equity": 2500000000.0,
        "ifrs-full_OperatingIncomeLoss": 300000000.0,
        "ifrs-full_InterestExpense": 30000000.0,
    }
    rec = reconcile_cross_national_financials(kr_facts, country_code="KR")
    assert rec["current_ratio"] == 2.0  # 20억 / 10억
    assert rec["quick_ratio"] == 1.8    # (20억 - 2억) / 10억
    assert rec["debt_to_equity"] == 0.6 # 15억 / 25억
    assert rec["interest_coverage"] == 10.0 # 3억 / 3000만
    assert rec["discontinuity_flag"] is False


def test_reconcile_cross_national_financials_us():
    # US SEC US-GAAP facts
    us_facts = {
        "AssetsCurrent": 50000.0,
        "LiabilitiesCurrent": 25000.0,
        "InventoryNet": 5000.0,
        "Liabilities": 40000.0,
        "StockholdersEquity": 60000.0,
        "OperatingIncomeLoss": 12000.0,
        "InterestExpense": 1500.0,
        "prior_current_ratio": 1.2,
    }
    rec = reconcile_cross_national_financials(us_facts, country_code="US")
    assert rec["current_ratio"] == 2.0  # 50,000 / 25,000
    assert rec["quick_ratio"] == 1.8    # (50,000 - 5,000) / 25,000
    assert rec["debt_to_equity"] == pytest.approx(0.6667, rel=1e-3)
    assert rec["interest_coverage"] == 8.0 # 12,000 / 1,500
    assert rec["discontinuity_flag"] is True # 2.0 vs 1.2 > 50% change


def test_reconcile_cross_national_financials_cz():
    # Czech ARES CAS facts
    cz_facts = {
        "Oběžná aktiva": 12000000.0,
        "Krátkodobé závazky": 8000000.0,
        "Zásoby": 2000000.0,
        "Cizí zdroje": 10000000.0,
        "Vlastní kapitál": 15000000.0,
        "Provozní výsledek hospodaření": 2500000.0,
        "Nákladové úroky": 250000.0,
    }
    rec = reconcile_cross_national_financials(cz_facts, country_code="CZ")
    assert rec["current_ratio"] == 1.5  # 12M / 8M
    assert rec["quick_ratio"] == 1.25   # (12M - 2M) / 8M
    assert rec["debt_to_equity"] == pytest.approx(0.6667, rel=1e-3)
    assert rec["interest_coverage"] == 10.0
