import json

import pytest

from company_intel.interactive import MenuOption, ScriptedSelector, build_interactive_request


def test_arrow_menu_scripted_selection_rejects_disabled_values() -> None:
    selector = ScriptedSelector({"field": ["unknown"]})
    with pytest.raises(ValueError, match="disabled"):
        selector.select("field", "Company type", [MenuOption("unknown", "Unknown", enabled=False)], multiple=True)


def test_interactive_job_search_compiles_saved_snapshot_profile(tmp_path) -> None:
    (tmp_path / "greenhouse-jobs.json").write_text(json.dumps({"jobs": [{
        "id": "1", "title": "Data Engineer", "location": {"name": "Remote - US"},
        "language": "en", "content": "<li>SQL required</li>",
    }]}), encoding="utf-8")
    selector = ScriptedSelector({
        "main-category": "discovery", "category-action": "job-search",
        "job-country_code": ["US"], "job-keywords": "data engineer",
    })
    request = build_interactive_request(selector, tmp_path, tmp_path / "out")
    assert request.command == "job-search"
    assert request.profile["countries"] == ["US"]
    assert request.profile["job_keywords"] == ["data engineer"]
    assert "--payload" in request.argv


def test_interactive_non_file_company_search_compiles_a_profile(tmp_path) -> None:
    selector = ScriptedSelector({
        "main-category": "discovery", "category-action": "company-search",
        "company-countries": "US,KR", "company-keywords": "data engineer",
    })
    request = build_interactive_request(selector, tmp_path, tmp_path / "out")
    assert request.command == "company-search"
    assert request.profile["countries"] == ["US", "KR"]
