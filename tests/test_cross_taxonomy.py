from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from company_intel.job_search import (
    JobSearchProfile,
    normalize_greenhouse_jobs,
    normalize_lever_jobs,
    normalize_mpm_jobs,
    normalize_mpsv_jobs,
    search_job_dataframes,
)
from company_intel.taxonomy import (
    NCS_TO_ISCO_MAP,
    TAXONOMY_AXES,
    resolve_title_to_isco,
    taxonomy_facts_from_record,
)


def test_taxonomy_axes_include_occupation_and_crosswalk() -> None:
    assert "occupation_code" in TAXONOMY_AXES
    assert "occupation_pivot" in TAXONOMY_AXES
    assert "ncs_code" in TAXONOMY_AXES
    assert NCS_TO_ISCO_MAP.get("020101") == "2511"
    assert NCS_TO_ISCO_MAP.get("020201") == "2512"
    assert resolve_title_to_isco("Senior Data Analyst") == "2511"
    assert resolve_title_to_isco("Vývojáři softwaru") == "2512"
    assert resolve_title_to_isco("빅데이터 분석 전문관") == "2511"


def test_mpsv_salary_and_cz_isco_pivot_extraction() -> None:
    # 1. Flat string test
    payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "polozky": [
            {
                "id": "CZ-001",
                "zamestnavatel": {"nazev": "Prague Tech", "ico": "12345678"},
                "pozadovanaProfese": {"cs": "Analytik dat"},
                "profeseCzIsco": "25110",
                "typMzdy": "hod",
                "mesicniMzdaOd": 350.0,
                "mesicniMzdaDo": 500.0,
                "expirace": "2026-12-31",
            }
        ],
    }
    jobs, _, _ = normalize_mpsv_jobs(payload)
    assert len(jobs) == 1
    job = jobs[0]
    assert job["salary_period"] == "hour"
    assert job["occupation_code"] == "25110"
    assert job["occupation_pivot"] == "2511"

    facts = taxonomy_facts_from_record("mpsv_cz", payload["polozky"][0])
    facts_map = {(f.semantic_field, f.namespace): f.value for f in facts}
    assert facts_map.get(("occupation_code", "CZ-ISCO")) == "25110"
    assert facts_map.get(("occupation_pivot", "ISCO:08")) == "2511"

    # 2. Codebook dict test (CZ-ISCO and typMzdy as structured dicts)
    dict_payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "polozky": [
            {
                "id": "CZ-002",
                "zamestnavatel": {"nazev": "Brno Software", "ico": "87654321"},
                "pozadovanaProfese": {"cs": "Softwarový inženýr"},
                "profeseCzIsco": {"id": "25120"},
                "typMzdy": {"id": "hodinova"},
                "mesicniMzdaOd": 400.0,
                "expirace": "2026-12-31",
            }
        ],
    }
    dict_jobs, _, _ = normalize_mpsv_jobs(dict_payload)
    assert len(dict_jobs) == 1
    d_job = dict_jobs[0]
    assert d_job["salary_period"] == "hour"
    assert d_job["occupation_code"] == "25120"
    assert d_job["occupation_pivot"] == "2512"

    d_facts = taxonomy_facts_from_record("mpsv_cz", dict_payload["polozky"][0])
    d_facts_map = {(f.semantic_field, f.namespace): f.value for f in d_facts}
    assert d_facts_map.get(("occupation_code", "CZ-ISCO")) == "25120"
    assert d_facts_map.get(("occupation_pivot", "ISCO:08")) == "2512"


def test_lever_all_locations_and_unspecified_necessity() -> None:
    payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "jobs": [
            {
                "id": "LEV-001",
                "text": "Software Engineer",
                "country": "US",
                "categories": {
                    "location": "San Francisco, CA",
                    "allLocations": ["San Francisco, CA", "New York, NY", "Remote - US"],
                    "commitment": "Full-time",
                },
                "lists": [
                    {
                        "text": "Requirements",
                        "content": "<ul><li>5+ years Python</li><li>SQL proficiency</li></ul>",
                    }
                ],
            }
        ],
    }
    jobs, requirements, _ = normalize_lever_jobs(payload)
    assert len(jobs) == 1
    job = jobs[0]
    assert "New York, NY" in job["_location_candidates"]
    assert "Remote - US" in job["_location_candidates"]
    assert job["occupation_pivot"] == "2512"
    assert len(requirements) >= 2
    # Requirement necessity should include unspecified rather than forcing all to required
    assert any(r["necessity"] == "unspecified" for r in requirements)


def test_mpm_employment_type_and_occupation_pivot() -> None:
    payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "jobs": [
            {
                "idx": "MPM-001",
                "insttname": "한국지능정보사회진흥원",
                "title": "빅데이터 분석 전문직 채용",
                "type01": "g01",
                "type02": "정규직",
                "enddate": "2026-12-31",
            }
        ],
    }
    jobs, _, _ = normalize_mpm_jobs(payload)
    assert len(jobs) == 1
    job = jobs[0]
    assert job["employment_type"] == "permanent"
    assert job["employment_type_raw"] == "정규직"
    assert job["occupation_pivot"] == "2511"


def test_worknet_and_hrdkorea_taxonomy_facts() -> None:
    worknet_rec = {
        "jobCd": "133101",
        "ncsClCd": "02010101",
    }
    facts = taxonomy_facts_from_record("worknet", worknet_rec)
    facts_map = {(f.semantic_field, f.namespace): f.value for f in facts}
    assert facts_map.get(("occupation_code", "KECO")) == "133101"
    assert facts_map.get(("ncs_code", "NCS")) == "02010101"
    assert facts_map.get(("occupation_pivot", "ISCO:08")) == "2511"

    hrdkorea_rec = {
        "ncsSubCd": "02020101",
    }
    hrd_facts = taxonomy_facts_from_record("hrdkorea", hrdkorea_rec)
    hrd_map = {(f.semantic_field, f.namespace): f.value for f in hrd_facts}
    assert hrd_map.get(("ncs_code", "NCS")) == "02020101"
    assert hrd_map.get(("occupation_pivot", "ISCO:08")) == "2512"

    # Also test snake_case keys from probe normalizer
    wn_snake = {"job_cd": "133101", "ncs_cl_cd": "02010101"}
    wn_snake_facts = taxonomy_facts_from_record("worknet", wn_snake)
    wn_s_map = {(f.semantic_field, f.namespace): f.value for f in wn_snake_facts}
    assert wn_s_map.get(("occupation_code", "KECO")) == "133101"
    assert wn_s_map.get(("ncs_code", "NCS")) == "02010101"
    assert wn_s_map.get(("occupation_pivot", "ISCO:08")) == "2511"

    hrd_snake = {"ncs_sub_cd": "02020101"}
    hrd_snake_facts = taxonomy_facts_from_record("hrdkorea", hrd_snake)
    hrd_s_map = {(f.semantic_field, f.namespace): f.value for f in hrd_snake_facts}
    assert hrd_s_map.get(("ncs_code", "NCS")) == "02020101"
    assert hrd_s_map.get(("occupation_pivot", "ISCO:08")) == "2512"


def test_cross_lingual_job_search_by_isco_and_keywords() -> None:
    mpsv_payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "polozky": [
            {
                "id": "CZ-DATA-01",
                "zamestnavatel": {"nazev": "Prague Analytics"},
                "pozadovanaProfese": {"cs": "Analytik dat"},
                "profeseCzIsco": "25110",
                "expirace": "2026-12-31",
            }
        ],
    }
    mpm_payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "jobs": [
            {
                "idx": "KR-DATA-01",
                "insttname": "한국데이터산업진흥원",
                "title": "빅데이터 분석 및 통계 연구원",
                "type02": "정규직",
                "enddate": "2026-12-31",
            }
        ],
    }
    greenhouse_payload = {
        "collected_at": "2026-10-15T00:00:00Z",
        "jobs": [
            {
                "id": "US-DATA-01",
                "title": "Senior Data Analyst",
                "country": "US",
                "location": {"name": "New York, NY"},
                "application_deadline": "2026-12-31",
            }
        ],
    }

    payloads = {
        "mpsv": mpsv_payload,
        "mpm": mpm_payload,
        "greenhouse": greenhouse_payload,
    }

    # 1. Search by ISCO code 2511
    profile_by_isco = JobSearchProfile(
        countries=("CZ", "KR", "US"),
        job_keywords=(),
        isco_codes=("2511",),
        active_only=False,
    )
    result_isco = search_job_dataframes(payloads, profile_by_isco)
    matched_ids = {row["job_id"] for row in result_isco.jobs.to_dict("records")}
    assert "CZ-DATA-01" in matched_ids
    assert "KR-DATA-01" in matched_ids
    assert "US-DATA-01" in matched_ids

    # 2. Search by cross-lingual job keyword
    profile_by_kw = JobSearchProfile(
        countries=("CZ", "KR", "US"),
        job_keywords=("data analyst",),
        active_only=False,
    )
    result_kw = search_job_dataframes(payloads, profile_by_kw)
    matched_kw_ids = {row["job_id"] for row in result_kw.jobs.to_dict("records")}
    # All 3 countries match because their occupation_pivot maps to ISCO 2511!
    assert "US-DATA-01" in matched_kw_ids
    assert "CZ-DATA-01" in matched_kw_ids
    assert "KR-DATA-01" in matched_kw_ids


def test_korean_cli_with_cross_taxonomy_options(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from company_intel.cli import main

    profile_file = tmp_path / "profile.json"
    profile_file.write_text(
        json.dumps({
            "countries": ["KR", "US"],
            "job_keywords": ["engineer"],
            "active_only": False,
        }),
        encoding="utf-8",
    )
    payload_file = tmp_path / "gh.json"
    payload_file.write_text(
        json.dumps({
            "jobs": [
                {
                    "id": "GH-101",
                    "title": "Software Engineer",
                    "country": "US",
                    "location": {"name": "Austin, TX"},
                }
            ]
        }),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    exit_code = main([
        "채용-검색",
        "--프로필", str(profile_file),
        "--원천-응답", f"greenhouse={payload_file}",
        "--출력", str(out_dir),
        "--직업분류-코드", "2512",
    ])
    assert exit_code == 0
    jobs_csv = out_dir / "jobs.csv"
    assert jobs_csv.is_file()
    content = jobs_csv.read_text(encoding="utf-8")
    assert "GH-101" in content
    assert "2512" in content


def test_fastapi_job_search_request_to_domain_with_taxonomy() -> None:
    from company_intel.api import JobSearchRequest

    req = JobSearchRequest(
        payloads={},
        countries=["CZ", "KR"],
        job_keywords=["developer"],
        isco_codes=["2512"],
        ncs_codes=["02020101"],
    )
    profile = req.to_domain()
    assert profile.countries == ("CZ", "KR")
    assert profile.job_keywords == ("developer",)
    assert profile.isco_codes == ("2512",)
    assert profile.ncs_codes == ("02020101",)

