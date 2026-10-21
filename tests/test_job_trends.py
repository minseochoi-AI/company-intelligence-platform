from cil_domain.jobs.trends import aggregate_job_trends, build_posting_lifecycle, evaluate_trend_eligibility


def _snapshot(identifier: str, jobs: list[str]) -> dict:
    return {"snapshot_id": identifier, "collected_at": f"2026-09-0{identifier}T00:00:00Z", "provider": "mpsv", "taxonomy_version": "1", "normalizer_version": "1", "coverage_cohort": "all", "jobs": [{"provider": "mpsv", "job_id": item} for item in jobs]}


def test_single_snapshot_is_ineligible() -> None:
    assert not evaluate_trend_eligibility([_snapshot("1", ["a"])]).eligible


def test_posting_lifecycle_and_metrics() -> None:
    result = aggregate_job_trends([_snapshot("1", ["a"]), _snapshot("2", ["a", "b"])])
    assert result["status"] == "eligible"
    assert result["series"][1]["new_postings"] == 1
    assert {item.job_id for item in build_posting_lifecycle([_snapshot("1", ["a"]), _snapshot("2", ["a", "b"])])} == {"a", "b"}
