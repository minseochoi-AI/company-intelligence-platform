from __future__ import annotations

from pathlib import Path
import pytest
from cil_integrations.runtime.settings import Settings
from cil_integrations.providers.koneps.procurements import CanonicalProcurementRecord, CURATED_KONEPS_FIXTURES
from cil_integrations.storage.duckdb.repository import Warehouse


@pytest.fixture
def test_warehouse(tmp_path: Path) -> Warehouse:
    root = Path(__file__).resolve().parents[1]
    settings = Settings(
        project_root=root,
        artifact_dir=tmp_path / "artifacts",
        database_url=f"duckdb:///{tmp_path / 'test_incremental.duckdb'}",
        sec_user_agent="test@example.com",
    )
    wh = Warehouse(settings)
    wh.initialize()
    return wh


def test_watermark_lifecycle_and_accumulation(test_warehouse: Warehouse):
    source = "KONEPS"
    assert test_warehouse.get_watermark(source) is None

    # First sync: 5 records
    test_warehouse.update_watermark(
        source_name=source,
        records_synced=5,
        sync_status="SUCCESS",
        last_watermark_value="2026-10-01",
        details={"batch": 1},
    )
    wm1 = test_warehouse.get_watermark(source)
    assert wm1 is not None
    assert wm1["records_synced"] == 5
    assert wm1["sync_status"] == "SUCCESS"
    assert wm1["last_watermark_value"] == "2026-10-01"

    # Second incremental sync: 3 more records
    test_warehouse.update_watermark(
        source_name=source,
        records_synced=3,
        sync_status="SUCCESS",
        last_watermark_value="2026-10-15",
        details={"batch": 2},
    )
    wm2 = test_warehouse.get_watermark(source)
    assert wm2 is not None
    # Cumulative records synced should be 5 + 3 = 8
    assert wm2["records_synced"] == 8
    assert wm2["last_watermark_value"] == "2026-10-15"


def test_incremental_sync_source_with_procurements(test_warehouse: Warehouse):
    records = [CanonicalProcurementRecord(**item).to_dict() for item in CURATED_KONEPS_FIXTURES[:3]]

    def dummy_fetcher(since_val):
        return records, "2026-10-19"

    res = test_warehouse.incremental_sync_source("KONEPS", dummy_fetcher)
    assert res["status"] == "SUCCESS"
    assert res["records_synced"] == 3
    assert res["watermark"] == "2026-10-19"

    # Verify rows in duckdb table
    with test_warehouse.connect() as conn:
        count = conn.execute("SELECT count(*) FROM public_procurement").fetchone()[0]
        assert count == 3
        row = conn.execute("SELECT buyer_name, contract_amount FROM public_procurement WHERE procurement_id=?", [records[0]["procurement_id"]]).fetchone()
        assert row[0] == records[0]["buyer_name"]
        assert row[1] == records[0]["contract_amount"]
