def test_added_api_normalizer_preserves_new_fields_and_pagination_status(tmp_path):
    from cil_integrations.research.capability_registry import (
        CapabilityRegistry,
        OperationStatus,
    )
    from cil_contracts.requests import ReportRequest, content_hash
    from cil_application.research.report_service import run_research
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook
    import json

    registry = CapabilityRegistry()
    operation = OperationStatus(
        "new.jobs",
        "new",
        "2",
        ("jobs",),
        ("posting_id",),
        "posting_revision",
        "local-analysis",
        "ready",
    )
    registry.register(operation)
    registry.register_normalizer(
        "new.jobs",
        "2",
        lambda raw: {
            "posting_id": raw["id"],
            "revision": "r1",
            "available_at": "2026-10-19T00:00:00Z",
            "cluster_signature": "US:PRIVATE:ALL:REGULAR:REMOTE",
        },
    )
    raw = [{"id": "P1", "new_values": {"boolean": False, "amount": 0, "unknown": None}}]
    snapshot = registry.ingest_saved(
        "new.jobs", "2", [raw], source_kind="fixture", expected_pages=2
    )
    assert snapshot["coverage"]["complete"] is False
    request = ReportRequest.from_dict(
        {
            "purpose": ["selected-posting"],
            "question": "new API 확인",
            "as_of": "2026-10-20T00:00:00Z",
            "subject_refs": [
                {"provider_id": "new", "posting_id": "P1", "revision": "r1"}
            ],
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    store = ResearchArtifactStore(tmp_path)
    result = run_research(
        request, snapshot, registry, store, renderer=render_research_workbook
    )
    assert result["source_kind"] == "fixture"
    archived = json.loads(store.read("facts/raw.json"))
    assert archived["postings"][0]["raw_attributes"] == raw[0]
    assert archived["sources"][0]["snapshot_hash"] == content_hash([raw])
