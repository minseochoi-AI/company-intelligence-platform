import json

from cil_domain.provenance.manifests import build_run_manifest, verify_manifest
from cil_integrations.storage.manifests import write_run_manifest


def test_run_manifest_redacts_sensitive_values_and_keeps_lineage_hashes(tmp_path):
    secret = "secret-value-must-not-appear"
    manifest = build_run_manifest(
        "job-search",
        {
            "countries": ("US", "CZ"),
            "api_key": secret,
            "nested": {"access_token": secret},
        },
        [
            {
                "semantic_field": "workplace_type",
                "provider": "lever",
                "raw_field": "workplaceType",
                "record_count": 4,
            }
        ],
        [
            {
                "provider": "lever",
                "source_url": f"https://example.test/jobs?serviceKey={secret}&country=US",
                "raw_payload": {"token": secret},
            }
        ],
        {"strict": 2, "unverifiable": 1},
        {"jobs.csv": b"job_id,title\n1,Engineer\n"},
        manifest={"files": [{"name": "jobs.csv"}], "private_key": secret},
        generated_at="2026-09-13T00:00:00+00:00",
    )

    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    assert manifest["schema_version"] == "1.0"
    assert manifest["run_id"].startswith("run-")
    assert manifest["lineage"]["profile_sha256"]
    assert manifest["output_files"][0]["sha256"]
    assert secret not in encoded
    assert "<redacted>" in encoded

    path = write_run_manifest(tmp_path / "run-manifest.json", manifest)
    assert json.loads(path.read_text(encoding="utf-8"))["run_id"] == manifest["run_id"]


def test_v2_manifest_binds_selection_and_snapshot_refs():
    manifest = build_run_manifest("current-jobs", {"countries": ["KR"]}, selection={"purpose": "current_jobs"}, snapshot_ref={"snapshot_id": "s1"}, result_refs={"jobs": "hash"})
    assert manifest["schema_version"] == "2.0"
    assert manifest["snapshot_ref"]["snapshot_id"] == "s1"
    assert verify_manifest(manifest)
