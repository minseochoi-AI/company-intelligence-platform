from company_intel.live_snapshots import SnapshotRequest, refresh_sources, select_snapshot, snapshot_freshness


def test_mpm_pagination_is_deduplicated_and_partial_manifest_is_explicit() -> None:
    request = SnapshotRequest(("mpm", "mpsv"), {"mpm": {}}, "2026-09-14T00:00:00+00:00")
    manifest = refresh_sources({"mpm": lambda _: {"jobs": [{"posting_id": "1"}]}}, request, collected_at=request.requested_at)
    assert manifest.status == "partial"
    assert manifest.sources[0]["payload_sha256"]
    assert manifest.sources[1]["status"] == "unavailable"


def test_snapshot_replay_selection_and_freshness() -> None:
    selected = select_snapshot({"old": {"collected_at": "2026-09-10T00:00:00+00:00"}, "new": {"collected_at": "2026-09-14T00:00:00+00:00"}})
    assert selected["snapshot_id"] == "new"
    assert snapshot_freshness("2026-09-14T00:00:00+00:00", now="2026-09-14T00:01:00+00:00")["fresh"]
