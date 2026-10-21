import pytest
from cil_domain.finance.analytics import calculate_dynamic_wacc, dynamic_macro_linked_dcf
from cil_integrations.providers.bea.cubes import BEACubeLoader
from cil_integrations.providers.eurostat.cubes import EurostatCubeLoader
from cil_domain.finance.macro import MacroCubeManager
from cil_contracts.macro import MacroObservation


def test_calculate_dynamic_wacc_rate_sensitivity():
    # Base case: 3.5% base rate
    wacc_high = calculate_dynamic_wacc(base_rate=0.035, beta=1.0, equity_risk_premium=0.055, credit_spread=0.015)
    # Rate cut case: 3.0% base rate (-50bp)
    wacc_low = calculate_dynamic_wacc(base_rate=0.030, beta=1.0, equity_risk_premium=0.055, credit_spread=0.015)

    assert wacc_high["cost_of_equity"] == pytest.approx(0.090) # 3.5% + 5.5%
    assert wacc_low["cost_of_equity"] == pytest.approx(0.085)  # 3.0% + 5.5%
    assert wacc_low["wacc"] < wacc_high["wacc"]                # WACC strictly drops
    assert (wacc_high["wacc"] - wacc_low["wacc"]) > 0.004      # Drops by ~43bp


def test_dynamic_macro_linked_dcf_valuation_uplift():
    rev = 2000000000.0  # 20억
    debt = 100000000.0  # 1억
    shares = 100000.0   # 10만주

    # 1. High rate environment (3.5%)
    dcf_high = dynamic_macro_linked_dcf(revenue=rev, net_debt=debt, shares=shares, base_rate=0.035)
    base_val_high = next(s for s in dcf_high["scenarios"] if s["name"] == "base")["value_per_share"]

    # 2. Rate cut environment (3.0%)
    dcf_low = dynamic_macro_linked_dcf(revenue=rev, net_debt=debt, shares=shares, base_rate=0.030)
    base_val_low = next(s for s in dcf_low["scenarios"] if s["name"] == "base")["value_per_share"]

    # Lower rate must produce higher equity value per share
    assert base_val_low > base_val_high
    uplift_pct = (base_val_low / base_val_high - 1.0) * 100.0
    assert uplift_pct > 5.0 # At least 5% valuation uplift on 50bp rate cut


def test_dynamic_macro_linked_dcf_fx_elasticity():
    rev = 1000000000.0
    debt = 0.0
    shares = 100000.0

    # Exporter with 10% currency depreciation (positive FX shock)
    dcf_exp_deprec = dynamic_macro_linked_dcf(
        revenue=rev, net_debt=debt, shares=shares, fx_change_pct=0.10, is_exporter=True, base_fcf_margin=0.15
    )
    # Exporter with neutral FX
    dcf_exp_neutral = dynamic_macro_linked_dcf(
        revenue=rev, net_debt=debt, shares=shares, fx_change_pct=0.0, is_exporter=True, base_fcf_margin=0.15
    )

    margin_deprec = dcf_exp_deprec["macro_inputs"]["adjusted_fcf_margin"]
    margin_neutral = dcf_exp_neutral["macro_inputs"]["adjusted_fcf_margin"]

    assert margin_deprec > margin_neutral # Margin expands from 15% to 15.375%


def test_macro_cube_loader_parsing():
    bea_raw = [
        {"TimePeriod": "2024Q1", "DataValue": "22,758.2", "SeriesCode": "A191RX"},
        {"TimePeriod": "2024Q2", "DataValue": "22,925.7", "SeriesCode": "A191RX"},
    ]
    bea_obs = BEACubeLoader.parse_bea_nipa_table(bea_raw)
    assert len(bea_obs) == 2
    assert bea_obs[0].calendar_quarter == "CY2024-Q1"
    assert bea_obs[0].value == 22758.2

    euro_raw = [
        {"time": "2024-Q1", "value": "56400.5"},
        {"time": "2024-Q2", "value": "56900.2"},
    ]
    cz_obs = EurostatCubeLoader.parse_eurostat_tsv_or_json(euro_raw, country_code="CZ")
    assert len(cz_obs) == 2
    assert cz_obs[0].country_code == "CZ"
    assert cz_obs[0].calendar_quarter == "CY2024-Q1"

    mgr = MacroCubeManager(bea_obs + cz_obs)
    # Check default fallbacks
    assert mgr.get_latest_base_rate("KR") is None
    assert mgr.get_real_gdp_growth("US") > 0.005 # 22925.7 / 22758.2 - 1 = ~0.73%
