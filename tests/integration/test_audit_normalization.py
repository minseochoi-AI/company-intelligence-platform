import json
from cil_integrations.providers.job_records import from_us_usajobs_record
from cil_integrations.research.capability_registry import CapabilityRegistry
from cil_integrations.storage.evidence import ResearchArtifactStore
from cil_application.research.report_service import run_research
from cil_contracts.requests import ReportRequest
from cil_reporting.research_workbook import render_research_workbook


def test_canonical_us_record_reaches_raw_archive_and_workbook_without_default_salary(
    tmp_path,
):
    raw = {
        "PositionID": "P",
        "PositionURI": "https://example.test/P",
        "OrganizationName": "Example",
        "PositionTitle": "Role",
        "PositionRemuneration": [{"MinimumRange": 0}],
        "custom": {"new": False},
    }
    record = from_us_usajobs_record(raw)
    assert record.salary_min == 0 and record.salary_max is None
    row = {
        **record.to_dict(),
        "provider_id": "saved",
        "posting_id": "P",
        "revision": "r",
        "available_at": "2026-10-19T00:00:00Z",
        "cluster_signature": record.cluster_signature.key,
    }
    request = ReportRequest.from_dict(
        {
            "purpose": ["selected-posting"],
            "question": "공고 보존",
            "as_of": "2026-10-20T00:00:00Z",
            "subject_refs": [
                {"provider_id": "saved", "posting_id": "P", "revision": "r"}
            ],
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    store = ResearchArtifactStore(tmp_path)
    run_research(
        request,
        {"source_kind": "fixture", "postings": [row]},
        CapabilityRegistry(),
        store,
        renderer=render_research_workbook,
    )
    assert (
        json.loads(store.read("facts/raw.json"))["postings"][0]["raw_attributes"] == raw
    )
