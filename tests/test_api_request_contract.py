import pytest
from pathlib import Path
from fastapi import HTTPException

from cil_api.schemas import CurrentJobRequest, SearchProfileRequest
from cil_api.routes.companies import company_search
from cil_domain.providers.parsing import get_path
from cil_integrations.providers.registry import keyless_probes
from cil_integrations.catalog.repository import load_source_catalog
from cil_application.validation.providers import SemanticFieldCheck


def test_snapshot_request_metadata_does_not_leak_into_search_profile():
    request = CurrentJobRequest(
        payloads={}, countries=["KR"], job_keywords=["Engineer"],
        snapshot_id="fixture-1", active_as_of="2026-10-13T00:00:00Z",
    )
    profile = request.to_domain()
    assert profile.countries == ("KR",)
    assert profile.job_keywords == ("Engineer",)
    assert "snapshot_id" not in profile.__dataclass_fields__
    assert request.snapshot_id == "fixture-1"


def test_current_job_default_metadata_is_also_excluded():
    request = CurrentJobRequest(payloads={}, countries=["KR"], occupations=["2512"])
    assert request.to_domain().occupations == ("2512",)


def test_invalid_company_search_returns_client_error():
    with pytest.raises(HTTPException) as caught:
        company_search(SearchProfileRequest(countries=["KR"]))
    assert caught.value.status_code == 422
    assert "provide job_keywords" in caught.value.detail


def test_worldbank_catalog_and_probe_agree_on_metadata_and_observation_paths():
    root = Path(__file__).resolve().parents[1]
    policy = load_source_catalog(root / "config/providers.json").by_id("world_bank_gdp")
    probe = next(p for p in keyless_probes("audit@example.test") if p.id == policy.operation_id)
    payload = [{"total": 1}, [{"countryiso3code": "KOR", "date": "2025", "value": 123}]]
    assert policy.required_paths == tuple(probe.required_paths)
    assert all(SemanticFieldCheck.present(get_path(payload, path)) for path in policy.required_paths)


def test_hrdkorea_and_worknet_catalog_and_probe_agree_on_paths():
    from cil_integrations.providers.registry import keyed_probes

    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")
    probes = {p.id: p for p in keyed_probes()}

    # Verify hrdkorea_ncs_duty
    hrd_policy = catalog.by_id("hrdkorea_ncs_duty")
    hrd_probe = probes["hrdkorea_ncs_duty"]
    assert hrd_policy.required_paths == tuple(hrd_probe.required_paths)
    hrd_sample_payload = {"items": [{"ncs_sub_cd": "02010101", "duty_cd": "0201"}]}
    assert all(SemanticFieldCheck.present(get_path(hrd_sample_payload, path)) for path in hrd_policy.required_paths)

    # Verify worknet_job_duty_bridge
    wn_policy = catalog.by_id("worknet_job_duty_bridge")
    wn_probe = probes["worknet_job_duty_bridge"]
    assert wn_policy.required_paths == tuple(wn_probe.required_paths)
    wn_sample_payload = {"duties": [{"ncs_cl_cd": "02010101", "duty_cd": "0201"}]}
    assert all(SemanticFieldCheck.present(get_path(wn_sample_payload, path)) for path in wn_policy.required_paths)

