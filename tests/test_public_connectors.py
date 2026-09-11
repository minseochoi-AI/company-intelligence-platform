from company_intel.config import Settings
from company_intel.connectors import build_probes
from company_intel.connectors.keyed import alio_context_evidence
from company_intel.connectors.keyless import _select
from company_intel.http import HttpClient
from company_intel.models import Probe


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
