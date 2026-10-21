from cil_application.analysis.service import run_temporal_analytics_suite
from cil_domain.finance.macro import MacroCubeManager


def test_empty_temporal_inputs_have_no_synthetic_observations():
    result = run_temporal_analytics_suite()
    assert result['status'] == 'NEEDS_EVIDENCE' and 'methodologies' not in result
    assert MacroCubeManager().get_real_gdp_growth('US') is None
