from company_intel.selection_provenance import bind_selection_run, verify_run_chain


def test_hash_chain_redaction_and_tamper_detection() -> None:
    manifest = bind_selection_run({"purpose": "current_jobs", "email": "person@example.test"}, {"snapshot_id": "s1", "sources": []}, {"jobs": []}).as_dict()
    assert verify_run_chain(manifest)
    assert "email" not in str(manifest["selection"])
    manifest["result_refs"]["jobs"] = "changed"
    assert not verify_run_chain(manifest)
