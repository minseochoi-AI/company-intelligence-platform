from io import BytesIO
from openpyxl import load_workbook


def test_workbook_is_byte_deterministic_and_does_not_execute_source_formulas():
    from cil_reporting.research_workbook import render_research_workbook

    tables = {
        "Postings": [
            {
                "_row_id": "posting-one",
                "posting_id": "P1",
                "text": "=1+1",
                "value": None,
            }
        ]
    }
    one, two = render_research_workbook(tables), render_research_workbook(tables)
    assert one.data == two.data
    workbook = load_workbook(BytesIO(one.data), data_only=False)
    cells = [cell for row in workbook["Postings"] for cell in row]
    assert any(cell.value == "=1+1" and cell.data_type == "s" for cell in cells)
    assert any(cell.value == "null" for cell in cells)
    assert all(cell.data_type != "f" for cell in cells)


def test_fact_run_preserves_raw_fields_with_model_and_network_calls_blocked(
    tmp_path, monkeypatch, proof
):
    import builtins
    import json
    import socket
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import run_research
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in {"openai", "anthropic", "langchain", "litellm"}:
            raise AssertionError("model SDK imported in fact path")
        return original_import(name, *args, **kwargs)

    def forbidden_network(*args, **kwargs):
        raise AssertionError("network used in saved fact path")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    monkeypatch.setattr(socket.socket, "connect", forbidden_network)
    request = ReportRequest.from_dict(
        {
            "purpose": ["selected-posting"],
            "question": "필수 조건과 원문 보존",
            "subject_refs": [
                {
                    "provider_id": "saved",
                    "posting_id": "P1",
                    "revision": "r1",
                    "entity_id": "E1",
                }
            ],
            "as_of": "2026-10-20T00:00:00Z",
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    raw = {
        "source_kind": "fixture",
        "postings": [
            {
                "provider_id": "saved",
                "posting_id": "P1",
                "revision": "r1",
                "entity_id": "E1",
                "available_at": "2026-10-19T00:00:00Z",
                "cluster_signature": "KR:ALL:ALL:ALL:ALL",
                "new_api_value": {"nested": [False, 0, "=1+1"]},
            }
        ],
    }
    store = ResearchArtifactStore(tmp_path)
    result = proof.invoke(
        "SK-D05-contract",
        run_research,
        request,
        raw,
        CapabilityRegistry(),
        store,
        renderer=render_research_workbook,
        checks={
            "input": lambda b, a, r, e: (
                b["args"][1]["source_kind"] == "fixture"
                and b["args"][1]["postings"][0]["new_api_value"]["nested"]
                == [False, 0, "=1+1"]
            ),
            "return": lambda b, a, r, e: (
                e is None and r["source_kind"] == "fixture" and r["status"] == "PARTIAL"
            ),
            "relation": lambda b, a, r, e: (
                json.loads(store.read("facts/raw.json")) == b["args"][1]
                and store.exists("research.xlsx")
            ),
        },
    )
    assert result["source_kind"] == "fixture"
    assert json.loads(store.read("facts/raw.json")) == raw
    tables = json.loads(store.read("tables.json"))
    assert any(r.get("value") == "=1+1" for r in tables["RawFields"])
    assert store.exists("research.xlsx") and store.exists("manifest.json")


def test_report_rejects_unsupported_numbers_and_fact_mutation(tmp_path):
    import json
    import pytest
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import (
        run_research,
        validate_report_claims,
        verify_sealed_bundle,
    )
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    request = ReportRequest.from_dict(
        {
            "purpose": ["financial"],
            "question": "재무 근거 확인",
            "as_of": "2026-10-20T00:00:00Z",
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    store = ResearchArtifactStore(tmp_path)
    result = run_research(
        request,
        {"source_kind": "fixture", "postings": []},
        CapabilityRegistry(),
        store,
        renderer=render_research_workbook,
    )
    claims = {
        "contract_version": "research-claims-v1",
        "manifest_sha256": result["manifest_sha256"],
        "claims": [],
    }
    with pytest.raises(ValueError, match="unbound numeric"):
        validate_report_claims(
            store, result["manifest_sha256"], "시연 자료. 연봉 999999원이다.", claims
        )
    (tmp_path / "facts/tables.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_sealed_bundle(store, result["manifest_sha256"])


def test_supported_report_is_separate_and_preserves_sealed_facts(tmp_path):
    import json
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import (
        run_research,
        seal_report,
        verify_sealed_bundle,
    )
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    request = ReportRequest.from_dict(
        {
            "purpose": ["financial"],
            "question": "시연 재무",
            "as_of": "2026-10-20T00:00:00Z",
            "financial_spec": {"entity_id": "E"},
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    fact = {
        "entity_id": "E",
        "concept": "Revenue",
        "scope": "consolidated",
        "currency": "KRW",
        "unit": "KRW",
        "frequency": "annual",
        "period_basis": "fiscal_year",
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
        "available_at": "2025-03-01T00:00:00Z",
        "value": 100,
        "source_id": "s1",
    }
    store = ResearchArtifactStore(tmp_path)
    result = run_research(
        request,
        {"source_kind": "fixture", "financials": [fact]},
        CapabilityRegistry(),
        store,
        renderer=render_research_workbook,
    )
    table = json.loads(store.read("tables.json"))["FinancialHistory"]
    row = next(r for r in table if r["record_kind"] == "source_fact")
    narrative = "시연 자료의 매출은 100 KRW다."
    claims = {
        "contract_version": "research-claims-v1",
        "manifest_sha256": result["manifest_sha256"],
        "claims": [
            {
                "claim_id": "revenue",
                "text": narrative,
                "kind": "observed",
                "value": 100,
                "unit": "KRW",
                "refs": [
                    {
                        "table_id": "FinancialHistory",
                        "row_id": row["_row_id"],
                        "column_id": "value",
                    }
                ],
            }
        ],
    }
    before = store.read("facts/tables.json")
    receipt = seal_report(store, result["manifest_sha256"], narrative, claims)
    assert (
        receipt["status"] == "REFERENCES_VALIDATED"
        and receipt["semantic_review"] == "human_required"
    )
    assert receipt["report_path"].startswith("reports/") and store.exists(
        receipt["report_path"]
    )
    assert store.read("facts/tables.json") == before
    verify_sealed_bundle(store, result["manifest_sha256"])
