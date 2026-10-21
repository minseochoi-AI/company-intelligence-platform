import json
from pathlib import Path

from cil_contracts.jobs import JobSearchProfile
from cil_integrations.providers.job_records import normalize_mpm_jobs, normalize_mpsv_jobs
from cil_application.jobs.search import search_job_dataframes


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
        "employment_types_unverifiable",
        "salary_comparability_unverifiable",
        "country_not_matched",
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
    assert "employment_types_unverifiable" in set(result.exclusions["reason"])


def test_required_language_uses_requirement_evidence_not_posting_language() -> None:
    payload = {"lever": [{
        "id": "lang", "text": "Data Engineer", "country": "US", "categories": {"location": "Remote", "commitment": "Full-time"},
        "language": "en", "lists": [{"text": "Requirements", "content": "<li>Korean required</li>"}],
    }]}
    match = search_job_dataframes(payload, JobSearchProfile(countries=("US",), job_keywords=("data",), required_languages=("korean",)))
    assert list(match.jobs["job_id"]) == ["lang"]


def test_unknown_policy_reports_unverifiable_separately_and_can_explicitly_include() -> None:
    payload = {"greenhouse": {"jobs": [{
        "id": "salary-unknown", "title": "Data Engineer", "location": {"name": "Remote - US"},
        "content": "<li>SQL required</li>",
    }]}}
    profile = JobSearchProfile(
        countries=("US",), job_keywords=("data",), minimum_salary_floor=100_000,
        salary_currency="USD", salary_period="year", unknown_policy="report",
    )
    reported = search_job_dataframes(payload, profile)
    assert list(reported.jobs["job_id"]) == []
    assert "salary_comparability_unverifiable" in set(reported.unverifiable_candidates["reason"])
    included = search_job_dataframes(payload, JobSearchProfile(**{**profile.__dict__, "unknown_policy": "include"}))
    assert list(included.jobs["job_id"]) == ["salary-unknown"]
    assert included.strict_matches.empty


def test_salary_ceiling_uses_the_same_signature_gate_as_salary_floor() -> None:
    payload = {"lever": [{
        "id": "monthly", "text": "Data Engineer", "country": "US", "categories": {"location": "Remote", "commitment": "Full-time"},
        "workplaceType": "remote", "salaryRange": {"currency": "CZK", "interval": "month", "min": 50_000, "max": 70_000},
    }]}
    result = search_job_dataframes(payload, JobSearchProfile(
        countries=("US",), job_keywords=("data",), maximum_salary_ceiling=120_000,
        salary_currency="USD", salary_period="year",
    ))
    assert "salary_comparability_unverifiable" in set(result.unverifiable_candidates["reason"])
    assert result.no_matches.empty


def test_lever_all_locations_and_mpm_institution_type_are_preserved() -> None:
    payload = {
        "lever": [{
            "id": "multi", "text": "Data Engineer", "categories": {"location": "London", "commitment": "Full-time"},
            "allLocations": ["Seattle, United States", "Remote - US"], "workplaceType": "remote",
        }],
        "mpm_public_employment": {"jobs": [{"posting_id": "k1", "institution_name": "기관", "title": "데이터", "type01": "e01", "type02": "g01"}]},
    }
    result = search_job_dataframes({"lever": payload["lever"]}, JobSearchProfile(
        countries=("US",), job_keywords=("data",), locations=("Seattle",),
    ))
    assert list(result.jobs["job_id"]) == ["multi"]
    assert "Seattle, United States" in set(result.locations["location_raw"])
    jobs, _, _ = normalize_mpm_jobs(payload["mpm_public_employment"])
    assert jobs[0]["institution_type_code"] == "e01"
    assert jobs[0]["employment_type_raw"] == "g01"


def test_public_context_is_filterable_without_claiming_legal_form() -> None:
    payload = {"mpm_public_employment": {"jobs": [{"posting_id": "k1", "institution_name": "기관", "title": "데이터", "closing_at": "20990101"}]}}
    result = search_job_dataframes(payload, JobSearchProfile(countries=("KR",), job_keywords=("데이터",), public_contexts=("public_employment_listing",)))
    assert list(result.jobs["job_id"]) == ["k1"]
