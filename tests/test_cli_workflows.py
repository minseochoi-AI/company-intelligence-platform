import json
from pathlib import Path

from company_intel.api import JobSearchRequest
from company_intel.cli import main
from company_intel.job_search import JobSearchProfile


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_job_search_workflow_and_unverifiable_result(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = _write(tmp_path / "jobs.json", {"jobs": [{"id": "1", "title": "Data Engineer", "location": {"name": "Remote - US"}, "content": "<li>SQL required</li>"}]})
    profile = _write(tmp_path / "profile.json", {"countries": ["US"], "job_keywords": ["data"], "required_requirement_terms": ["sql"]})
    assert main(["job-search", "--profile", str(profile), "--payload", f"greenhouse={payload}", "--output", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "jobs.csv").is_file()
    assert "matched_jobs" in capsys.readouterr().out


def test_screen_and_export_workflow(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    profile = _write(tmp_path / "screen.json", {"countries": ["US"], "industries": ["software"], "size_buckets": ["L"], "metrics": {"growth": 1}, "minimum_peer_size": 1})
    rows = _write(tmp_path / "rows.json", [{"entity_id": "A", "country": "US", "industry": "software", "size_bucket": "L", "growth": 1}])
    assert main(["screen", "--profile", str(profile), "--rows", str(rows)]) == 0
    tables = _write(tmp_path / "tables.json", {"companies": [{"company_id": "A", "legal_name": "A", "country_code": "US"}]})
    assert main(["export", "--tables", str(tables), "--output", str(tmp_path / "export"), "--no-xlsx"]) == 0
    assert (tmp_path / "export" / "manifest.json").is_file()
    assert capsys.readouterr().out


def test_cli_and_api_job_profile_use_the_same_domain_fields():
    request = JobSearchRequest(payloads={}, countries=["US"], job_keywords=["data"], required_languages=["korean"], salary_basis="gross")
    assert request.to_domain() == JobSearchProfile(countries=("US",), job_keywords=("data",), required_languages=("korean",), salary_basis="gross")
