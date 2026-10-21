from cil_integrations.runtime.settings import Settings
from company_intel.connectors import build_probes
from cil_integrations.providers.mpm.jobs import MPMPublicEmploymentConnector
from cil_integrations.providers.alio.evidence import alio_context_evidence
from cil_integrations.providers.mpsv.jobs import MPSVVacancyConnector
from cil_integrations.providers.parsing import _select
from cil_integrations.transport.http import HttpClient
from cil_contracts.facts import Probe


def test_public_korea_probes_use_explicit_namespaces(monkeypatch, tmp_path):
    for name in (
        "ALIO_PLUS_FACILITY_API_KEY",
        "ALIO_PLUS_EVENT_API_KEY",
        "ALIO_PLUS_BUSINESS_API_KEY",
        "ALIO_PLUS_ORGANIZATION_API_KEY",
        "MPM_PUBLIC_EMPLOYMENT_API_KEY",
    ):
        monkeypatch.setenv(name, "test-secret")

    probes = build_probes(Settings.from_env(tmp_path), {"alioplus", "mpm_public_employment"})

    assert [probe.id for probe in probes] == [
        "alioplus_facility",
        "alioplus_event",
        "alioplus_business",
        "alioplus_organization",
        "mpm_public_employment_list",
    ]
    assert all(probe.form_body and "X-API-AUTH-KEY" in probe.form_body for probe in probes[:4])
    assert probes[3].required_paths == ["0.title", "0.apbaTypeNa"]
    assert probes[3].capabilities == ["kr_public_institution_name", "public_institution_businesses"]
    assert probes[-1].params["serviceKey"] == "test-secret"


def test_public_korea_job_taxonomy_probes_and_xml_normalizers(monkeypatch, tmp_path):
    monkeypatch.setenv("HRDKOREA_NCS_API_KEY", "hrd-secret-key")
    monkeypatch.setenv("WORKNET_JOB_DUTY_API_KEY", "worknet-secret-key")

    probes = build_probes(Settings.from_env(tmp_path), {"hrdkorea", "worknet"})
    assert [p.id for p in probes] == ["hrdkorea_ncs_duty", "worknet_job_duty_bridge"]

    hrd_probe = probes[0]
    assert hrd_probe.params["serviceKey"] == "hrd-secret-key"
    assert hrd_probe.required_paths == ["items.0.ncs_sub_cd"]

    # Verify real raw XML body normalization for HRD Korea
    ncs_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
        <body>
            <items>
                <item>
                    <ncsLclsCd>02</ncsLclsCd>
                    <ncsMclsCd>0201</ncsMclsCd>
                    <ncsSclsCd>020101</ncsSclsCd>
                    <ncsSubCd>02010101</ncsSubCd>
                    <ncsSubNm>빅데이터분석</ncsSubNm>
                    <dutyCd>020101</dutyCd>
                    <compUnitCd>0201010101_16v3</compUnitCd>
                </item>
            </items>
            <totalCount>1</totalCount>
        </body>
    </response>""".encode("utf-8")
    normalized_ncs = hrd_probe.normalizer(ncs_xml, "application/xml")
    assert normalized_ncs["result_code"] == "00"
    assert normalized_ncs["items"][0]["ncs_sub_cd"] == "02010101"
    assert normalized_ncs["items"][0]["ncsSubCd"] == "02010101"
    assert normalized_ncs["items"][0]["duty_cd"] == "020101"

    wn_probe = probes[1]
    assert wn_probe.params["authKey"] == "worknet-secret-key"
    assert wn_probe.required_paths == ["duties.0.ncs_cl_cd"]

    # Verify real raw XML body normalization for Worknet
    worknet_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <jobDutyList>
        <total>1</total>
        <jobDuty>
            <dutyCd>020101</dutyCd>
            <dutyNm>빅데이터기획</dutyNm>
            <ncsClCd>02010101</ncsClCd>
        </jobDuty>
    </jobDutyList>""".encode("utf-8")
    normalized_wn = wn_probe.normalizer(worknet_xml, "application/xml")
    assert normalized_wn["total"] == 1
    assert normalized_wn["duties"][0]["ncs_cl_cd"] == "02010101"
    assert normalized_wn["duties"][0]["ncsClCd"] == "02010101"
    assert normalized_wn["duties"][0]["duty_cd"] == "020101"


def test_alio_organization_falls_back_to_display_name_without_claiming_identity():
    evidence = alio_context_evidence(
        {"apbaId": "", "apbaNa": None, "title": "근로복지공단", "apbaTypeNa": "준정부기관"}
    )

    assert evidence == {
        "institution_id": None,
        "institution_name": "근로복지공단",
        "institution_type": "준정부기관",
        "identity_status": "context_only_no_source_identifier",
        "evidence_scope": "public_institution_context",
        "is_job_requirement": False,
    }


def test_http_client_encodes_form_body(monkeypatch):
    captured = {}

    class Response:
        status = 200

        class Headers:
            @staticmethod
            def items():
                return []

        headers = Headers()

        @staticmethod
        def read():
            return b"[]"

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

    def fake_urlopen(request, timeout):
        captured["data"] = request.data
        captured["content_type"] = request.get_header("Content-type")
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = HttpClient(retries=0).execute(
        Probe(
            id="form",
            provider="test",
            category="test",
            regions=[],
            method="POST",
            url="https://example.test/form",
            form_body={"X-API-AUTH-KEY": "a+b", "pageSize": 1},
        )
    )

    assert result.status_code == 200
    assert captured["data"] == b"X-API-AUTH-KEY=a%2Bb&pageSize=1"
    assert captured["content_type"] == "application/x-www-form-urlencoded"


def test_normalizer_preserves_all_rows_instead_of_diagnostic_compaction():
    normalizer = _select({"rows": "rows"})
    rows = [{"id": number, "nested": {"value": number}} for number in range(9)]
    assert normalizer(("{\"rows\": " + __import__("json").dumps(rows) + "}").encode(), "application/json")["rows"] == rows


def test_public_snapshot_connectors_are_bounded_and_preserve_ids():
    connector = MPMPublicEmploymentConnector(lambda params: {"jobs": [{"posting_id": str(params["pageNo"])}]} if params["pageNo"] == 1 else {"jobs": []})
    assert connector.collect_snapshot(page_size=1)["record_count"] == 1
    snapshot = MPSVVacancyConnector().download_snapshot([b'{"polozky":[{"portalId":"x"}]}'], collected_at="2026-09-14T00:00:00Z")
    assert snapshot["record_count"] == 1
