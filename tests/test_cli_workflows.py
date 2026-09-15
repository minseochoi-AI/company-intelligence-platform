import json
from pathlib import Path

import pytest

from company_intel.api import JobSearchRequest
from company_intel.cli import main
from company_intel.cli_guide import COMMAND_GUIDES
from company_intel.job_search import JobSearchProfile


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_job_search_workflow_and_unverifiable_result(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = _write(
        tmp_path / "jobs.json",
        {
            "jobs": [
                {
                    "id": "1",
                    "title": "Data Engineer",
                    "location": {"name": "Remote - US"},
                    "content": "<li>SQL required</li>",
                }
            ]
        },
    )
    profile = _write(
        tmp_path / "profile.json",
        {"countries": ["US"], "job_keywords": ["data"], "required_requirement_terms": ["sql"]},
    )
    assert (
        main(
            [
                "job-search",
                "--profile",
                str(profile),
                "--payload",
                f"greenhouse={payload}",
                "--output",
                str(tmp_path / "out"),
            ]
        )
        == 0
    )
    assert (tmp_path / "out" / "jobs.csv").is_file()
    assert "matched_jobs" in capsys.readouterr().out


def test_screen_and_export_workflow(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    profile = _write(
        tmp_path / "screen.json",
        {
            "countries": ["US"],
            "industries": ["software"],
            "size_buckets": ["L"],
            "metrics": {"growth": 1},
            "minimum_peer_size": 1,
        },
    )
    rows = _write(
        tmp_path / "rows.json",
        [{"entity_id": "A", "country": "US", "industry": "software", "size_bucket": "L", "growth": 1}],
    )
    assert main(["screen", "--profile", str(profile), "--rows", str(rows)]) == 0
    tables = _write(
        tmp_path / "tables.json",
        {"companies": [{"company_id": "A", "legal_name": "A", "country_code": "US"}]},
    )
    assert main(["export", "--tables", str(tables), "--output", str(tmp_path / "export"), "--no-xlsx"]) == 0
    assert (tmp_path / "export" / "manifest.json").is_file()
    assert capsys.readouterr().out


def test_cli_and_api_job_profile_use_the_same_domain_fields():
    request = JobSearchRequest(
        payloads={},
        countries=["US"],
        job_keywords=["data"],
        required_languages=["korean"],
        posting_languages=["english"],
        business_units=["data"],
        salary_basis="gross",
    )
    assert request.to_domain() == JobSearchProfile(
        countries=("US",),
        job_keywords=("data",),
        required_languages=("korean",),
        posting_languages=("english",),
        business_units=("data",),
        salary_basis="gross",
    )


def test_interactive_scripted_preview_and_non_tty_guidance(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write(
        tmp_path / "greenhouse-jobs.json",
        {
            "jobs": [
                {
                    "id": "1",
                    "title": "Data Engineer",
                    "location": {"name": "Remote - US"},
                    "content": "<li>SQL required</li>",
                }
            ]
        },
    )
    script = _write(
        tmp_path / "interactive.json",
        {
            "main-category": "discovery",
            "category-action": "job-search",
            "job-country_code": ["US"],
            "job-keywords": "data engineer",
        },
    )
    assert (
        main(
            [
                "interactive",
                "--data-dir",
                str(tmp_path),
                "--output",
                str(tmp_path / "out"),
                "--script",
                str(script),
                "--dry-run",
            ]
        )
        == 0
    )
    assert (tmp_path / "out" / "job-search-profile.json").is_file()
    assert "job-search" in capsys.readouterr().out
    assert main(["interactive"]) == 1
    assert "tty_required" in capsys.readouterr().out


def test_current_jobs_cli_workflow(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = _write(
        tmp_path / "mpm.json",
        {
            "jobs": [
                {"posting_id": "1", "institution_name": "기관", "title": "데이터", "closing_at": "20990101"}
            ]
        },
    )
    profile = _write(tmp_path / "profile.json", {"countries": ["KR"], "job_keywords": ["데이터"]})
    assert (
        main(
            [
                "current-jobs",
                "--profile",
                str(profile),
                "--payload",
                f"mpm_public_employment={payload}",
                "--output",
                str(tmp_path / "current"),
            ]
        )
        == 0
    )
    assert (tmp_path / "current" / "current-jobs-result.json").is_file()


def test_korean_command_and_option_aliases_execute_the_same_job_search(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = _write(
        tmp_path / "jobs.json",
        {"jobs": [{"id": "1", "title": "Data Engineer", "location": {"name": "Remote - US"}}]},
    )
    profile = _write(tmp_path / "profile.json", {"countries": ["US"], "job_keywords": ["data"]})

    assert (
        main(
            [
                "채용-검색",
                "--프로필",
                str(profile),
                "--원천-응답",
                f"greenhouse={payload}",
                "--출력",
                str(tmp_path / "out"),
            ]
        )
        == 0
    )
    assert (tmp_path / "out" / "jobs.csv").is_file()

    assert main(["사용-안내", "--명령", "채용-검색"]) == 0
    guide = capsys.readouterr().out
    assert '"한글_명령": "채용-검색"' in guide
    assert '"호환_영문_옵션": "--profile"' in guide


def test_korean_help_exposes_localized_usage_and_english_compatibility(capsys):
    with pytest.raises(SystemExit) as result:
        main(["채용-검색", "--도움말"])

    assert result.value.code == 0
    help_text = capsys.readouterr().out
    assert "사용법:" in help_text
    assert "--프로필" in help_text
    assert "--profile" in help_text
    assert "공급자=응답.json" in help_text


def test_every_cli_command_has_a_runnable_korean_help_surface(capsys):
    for guide in COMMAND_GUIDES:
        with pytest.raises(SystemExit) as result:
            main([guide.korean_name, "--도움말"])
        assert result.value.code == 0
        assert guide.korean_name in capsys.readouterr().out
