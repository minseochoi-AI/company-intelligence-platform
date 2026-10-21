from cil_application.jobs.current import execute_current_job_search
from cil_contracts.jobs import JobSearchProfile


def test_denominator_chain_and_mpm_unknown_fields() -> None:
    payloads = {"mpm_public_employment": {"collected_at": "2026-09-14T00:00:00Z", "jobs": [{"posting_id": "1", "institution_name": "기관", "title": "데이터", "closing_at": "20990101"}]}}
    result = execute_current_job_search(payloads, JobSearchProfile(countries=("KR",), job_keywords=("데이터",), required_requirement_terms=("sql",)), snapshot_id="s1")
    assert result.denominators.normalized == 1
    assert result.denominators.unverifiable == 1
    assert result.snapshot_id == "s1"
