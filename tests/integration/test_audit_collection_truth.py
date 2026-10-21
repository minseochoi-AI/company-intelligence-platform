from cil_application.collection.service import CollectionService
from cil_integrations.research.capability_registry import (
    CapabilityRegistry,
    OperationStatus,
)


def test_archived_page_normalization_keeps_incomplete_collection_status():
    class TwoPages:
        def fetch_page(self, parameters, cursor):
            return {
                "records": [{"id": "one"}],
                "payload": {"items": [{"id": "one"}]},
                "next_cursor": "next",
            }

    collected = CollectionService().collect(
        TwoPages(), {}, authorized=True, max_pages=1
    )
    assert collected["status"] == "PARTIAL"
    registry = CapabilityRegistry(
        [OperationStatus("jobs", "local", "1", ("jobs",), ("id",), "posting", "local")]
    )
    registry.register_normalizer(
        "jobs", "1", lambda raw: {"posting_id": raw["id"], "revision": "r"}
    )
    saved = registry.ingest_saved(
        "jobs",
        "1",
        [p["records"] for p in collected["pages"]],
        source_kind="fixture",
        expected_pages=None,
    )
    assert saved["coverage"]["complete"] is False
