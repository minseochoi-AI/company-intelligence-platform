import json
from pathlib import Path

from company_intel.job_search import (
    JobSearchProfile,
    normalize_mpm_jobs,
    normalize_mpsv_jobs,
    search_job_dataframes,
)


def test_provider_semantics_and_hard_filters() -> None:
    payloads = {
        "greenhouse": {
            "collected_at": "2026-09-11T00:00:00Z",
            "jobs": [{
                "id": 1,
                "company_name": "Air",
                "title": "Data Engineer",
                "location": {"name": "Remote - US"},
                "language": "en",
                "absolute_url": "https://jobs.example/1",
                "content": "<ul><li>You have 5+ years of Python experience</li></ul>",
            }],
        },
        "lever": [{
            "id": "l1",
            "company_name": "Music",
            "text": "Data Engineer",
            "country": "US",
            "categories": {"location": "New York", "commitment": "Permanent", "team": "Data"},
            "workplaceType": "remote",
            "salaryRange": {"currency": "USD", "interval": "year", "min": 120000, "max": 150000},
            "hostedUrl": "https://jobs.example/l1",
            "descriptionPlain": "Build data products",
            "lists": [{"text": "Who You Are", "content": "<li>You have SQL and Python experience</li><li>AWS is a plus</li>"}],
        }],
        "mpm_public_employment": {"collected_at": "2026-09-11T00:00:00Z", "data": {"jobs": [{"posting_id": "2", "institution_name": "정부기관", "title": "데이터 분석 공무원", "registered_at": "20080718", "closing_at": "20080718"}]}},
    }
    result = search_job_dataframes(payloads, JobSearchProfile(
        countries=("US",), job_keywords=("data engineer",), workplace_types=("remote",),
        employment_types=("full-time",), languages=(), minimum_salary_floor=100000,
        salary_currency="USD", salary_period="year", required_requirement_terms=("sql",),
    ))
    # Lever's "Permanent" is contractual duration, not verified hours.  It
    # therefore cannot satisfy a full-time filter without a dedicated field.
    assert list(result.jobs["job_id"]) == []
    assert set(result.exclusions["reason"]) >= {
        "employment_type_not_matched_or_unknown",
        "salary_comparability_unverifiable",
        "country_not_matched_or_unknown",
    }
    assert result.metadata["limitations"][1].startswith("Unknown fields are reported separately")
    mpm_jobs, _, _ = normalize_mpm_jobs(payloads["mpm_public_employment"])
    assert mpm_jobs[0]["is_active"] is False


def test_career_overlap_and_mpsv_structured_requirements() -> None:
    lever_jobs = []
    for job_id, country in (("a", "US"), ("b", "CZ")):
        lever_jobs.append({
            "id": job_id, "company_name": f"Company-{job_id}", "text": "Analytics Engineer",
            "country": country, "categories": {"location": "Remote", "commitment": "Permanent"},
            "workplaceType": "remote", "hostedUrl": f"https://jobs.example/{job_id}",
            "lists": [{"text": "Qualifications", "content": "<li>You have SQL and Python experience</li>"}],
        })
    result = search_job_dataframes({"lever": lever_jobs}, JobSearchProfile(countries=("US", "CZ"), job_keywords=("analytics",)))
    sql = result.career_overlap.set_index("normalized_key").loc["skill:sql"]
    assert sql["posting_count"] == 2
    assert sql["company_count"] == 2
    assert sql["country_count"] == 2

    jobs, requirements, _ = normalize_mpsv_jobs({"polozky": [{
        "portalId": 7,
        "pozadovanaProfese": {"cs": "Datový analytik"},
        "zamestnavatel": {"ico": "12345678", "nazev": "CZ Employer"},
        "profeseCzIsco": {"id": "2511"},
        "mistoVykonuPrace": {"adresaText": "Praha"},
        "mesicniMzdaOd": 50000,
        "mesicniMzdaDo": 70000,
        "typMzdy": {"id": "mesicni"},
        "pozadovanaDovednost": [{"dovednost": {"id": "SQL"}, "popis": "SQL"}],
        "pozadovanaJazykovaZnalost": [{"jazyk": {"id": "EN"}, "urovenZnalosti": {"id": "B2"}}],
        "prvniKontaktSeZamestnavatelem": {"komuSeHlasit": {"email": "person@example.test"}},
    }]})
    assert jobs[0]["salary_period"] == "month"
    assert jobs[0]["occupation_system"] == "CZ-ISCO"
    assert {row["requirement_kind"] for row in requirements} == {"skill", "language"}
    assert "person@example.test" not in str(jobs) + str(requirements)


def test_title_language_and_unknown_requirement_semantics_are_separate() -> None:
    fixture = json.loads((Path(__file__).parent / "fixtures/provider_semantic_cases.json").read_text())
    result = search_job_dataframes(fixture, JobSearchProfile(
        countries=("CZ",), job_keywords=("data engineer",), required_languages=("english",),
    ))
    # The phrase exists only in description, so title-scoped search must not
    # promote this Platform Engineer posting to a data-engineer match.
    assert result.metadata["matched_jobs"] == 0
    assert "job_keywords_not_matched" in set(result.exclusions["reason"])

    result = search_job_dataframes(fixture, JobSearchProfile(
        countries=("US",), job_keywords=("data engineer",), employment_types=("full-time",),
    ))
    assert "employment_type_not_matched_or_unknown" in set(result.exclusions["reason"])


def test_required_language_uses_requirement_evidence_not_posting_language() -> None:
    payload = {"lever": [{
        "id": "lang", "text": "Data Engineer", "country": "US", "categories": {"location": "Remote", "commitment": "Full-time"},
        "language": "en", "lists": [{"text": "Requirements", "content": "<li>Korean required</li>"}],
    }]}
    match = search_job_dataframes(payload, JobSearchProfile(countries=("US",), job_keywords=("data",), required_languages=("korean",)))
    assert list(match.jobs["job_id"]) == ["lang"]
