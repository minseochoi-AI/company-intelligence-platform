from __future__ import annotations

import openpyxl
import pytest

from cil_domain.finance.analytics import calculate_cluster_elasticity_breakdown
from cil_application.analysis.service import run_temporal_analytics_suite
from cil_domain.clusters.signature import ClusterSignature
from cil_integrations.providers.job_records import from_cz_ares, from_cz_mpsv, from_kr_opendart, from_kr_public_job, from_kr_worknet, from_us_sec_or_usaspending
from cil_reporting.xlsx.occupations import build_occupational_lattice_workbook


def test_cluster_signature_properties_and_matching():
    sig = ClusterSignature(
        region="KR",
        sector="STATE_OWNED",
        tier="MARKET_SOE",
        contract="INTERN",
        workplace="ONSITE",
    )
    assert sig.key == "KR:STATE_OWNED:MARKET_SOE:INTERN:ONSITE"

    # Wildcard roll-up matching
    macro_filter = ClusterSignature.parse("KR:ALL:ALL:ALL:ALL")
    assert macro_filter.matches(sig) is True

    sector_filter = ClusterSignature.parse("KR:STATE_OWNED:ALL:ALL:ALL")
    assert sector_filter.matches(sig) is True

    contract_filter = ClusterSignature.parse("KR:STATE_OWNED:ALL:REGULAR:ALL")
    assert contract_filter.matches(sig) is False  # INTERN != REGULAR

    # Parsing fallback
    parsed = ClusterSignature.parse("CZ:PRIVATE:CZ_AS:REGULAR:HYBRID")
    assert parsed.region == "CZ"
    assert parsed.sector == "PRIVATE"
    assert parsed.tier == "CZ_AS"
    assert parsed.contract == "REGULAR"
    assert parsed.workplace == "HYBRID"


def test_api_normalization_factories():
    # 1. KR Public Job (Insa)
    sig_p01_e01 = from_kr_public_job(instt_se="p01", pblanc_ty="e01")
    assert sig_p01_e01.region == "KR"
    assert sig_p01_e01.sector == "STATE_OWNED"
    assert sig_p01_e01.tier == "MARKET_SOE"
    assert sig_p01_e01.contract == "REGULAR"

    sig_p01_e03 = from_kr_public_job(instt_se="p01", pblanc_ty="e03")
    assert sig_p01_e03.contract == "INTERN"

    sig_p02 = from_kr_public_job(instt_se="p02", pblanc_ty="e01")
    assert sig_p02.sector == "PUBLIC_INSTITUTION"
    assert sig_p02.tier == "QUASI_GOV"

    # 2. KR WorkNet
    sig_wn_large = from_kr_worknet(coclcd="01", emptype="10")
    assert sig_wn_large.region == "KR"
    assert sig_wn_large.sector == "UNKNOWN"
    assert sig_wn_large.tier == "LARGE_CONGLOMERATE"
    assert sig_wn_large.contract == "REGULAR"

    sig_wn_soe = from_kr_worknet(coclcd="05", emptype="20")
    assert sig_wn_soe.sector == "STATE_OWNED"
    assert sig_wn_soe.contract == "NON_REGULAR"

    # 3. KR OpenDART
    sig_dart_kospi = from_kr_opendart(corp_cls="Y")
    assert sig_dart_kospi.region == "KR"
    assert sig_dart_kospi.tier == "KOSPI"

    sig_dart_kosdaq = from_kr_opendart(corp_cls="K")
    assert sig_dart_kosdaq.tier == "KOSDAQ"

    # 4. CZ ARES
    sig_ares_sro = from_cz_ares(pravni_forma="112")
    assert sig_ares_sro.region == "CZ"
    assert sig_ares_sro.sector == "UNKNOWN"
    assert sig_ares_sro.tier == "CZ_SRO"

    sig_ares_soe = from_cz_ares(pravni_forma="301")
    assert sig_ares_soe.sector == "STATE_OWNED"
    assert sig_ares_soe.tier == "CZ_STATNI_PODNIK"

    # 5. CZ MPSV
    sig_mpsv_pub = from_cz_mpsv(statni_sprava=True)
    assert sig_mpsv_pub.sector == "UNKNOWN"
    sig_mpsv_pri = from_cz_mpsv(statni_sprava=False)
    assert sig_mpsv_pri.sector == "UNKNOWN"

    # 6. US SEC / USAspending
    sig_us_profit = from_us_sec_or_usaspending(recipient_type="for_profit_organization")
    assert sig_us_profit.region == "US"
    assert sig_us_profit.sector == "UNKNOWN"

    sig_us_gov = from_us_sec_or_usaspending(recipient_type="state_government")
    assert sig_us_gov.sector == "GOVERNMENT"


def test_cluster_elasticity_breakdown_and_simpsons_paradox():
    cohorts = [
        {
            "signature": "KR:PRIVATE:KOSPI:REGULAR:ONSITE",
            "name": "민간 사기업",
            "rev_growth": 0.15,
            "hiring_growth": 0.22,
            "weight": 5000,
        },
        {
            "signature": "KR:SOE:p01:REGULAR:ONSITE",
            "name": "공기업 일반정규직",
            "rev_growth": 0.08,
            "hiring_growth": -0.08,
            "weight": 1200,
        },
        {
            "signature": "KR:SOE:p01:INTERN:ONSITE",
            "name": "공기업 청년인턴",
            "rev_growth": 0.08,
            "hiring_growth": 0.24,
            "weight": 800,
        },
    ]

    res = calculate_cluster_elasticity_breakdown(cohorts)
    assert res["status"] == "success"
    assert res["simpsons_paradox_detected"] is True
    assert res["distortion_index"] > 1.0
    assert len(res["cohorts"]) == 3
    assert "심슨의 역설" in res["explanation"]


def test_temporal_analytics_suite_cluster_integration():
    report = run_temporal_analytics_suite(entity_id="00258801", isco_code="2512", demo=True)
    assert "methodologies" in report
    elas_result = report["methodologies"]["2_elasticity"]
    assert "cluster_breakdown" in elas_result
    cb = elas_result["cluster_breakdown"]
    assert cb["status"] == "success"
    assert cb["simpsons_paradox_detected"] is True
    assert len(cb["cohorts"]) >= 3


def test_excel_workbook_cluster_lattice_sheets(tmp_path):
    import pytest
    target = tmp_path / 'test_cluster_wb.xlsx'
    with pytest.raises(ValueError, match='explicit'):
        build_occupational_lattice_workbook(target)
    assert not target.exists()
