import pytest

from company_intel.models import SearchProfile
from company_intel.query_contract import (
    CompanySearchProfile,
    FilterVerdict,
    combine_verdicts,
    company_search_profile_from_mapping,
)
from company_intel.search import (
    explain_company_evaluation,
    rank_candidate_evaluations,
    rank_candidates,
    validate_search_profile,
)


def test_profile_requires_explicit_country_and_goal():
    with pytest.raises(ValueError, match="countries"):
        validate_search_profile(SearchProfile(countries=(), job_keywords=("data",)))


def test_ranking_preserves_unresolved_identity_as_an_exclusion():
    profile = SearchProfile(countries=("KR",), job_keywords=("data",), required_capabilities=("job_posting",))
    matches = rank_candidates(
        profile,
        [
            {
                "entity_id": "KR:1",
                "country_code": "KR",
                "name": "Verified",
                "title": "Data engineer",
                "capabilities": {"job_posting": "available"},
                "identity_status": "resolved",
            },
            {
                "entity_id": "KR:2",
                "country_code": "KR",
                "name": "Unknown",
                "capabilities": {"job_posting": "available"},
                "identity_status": "unresolved",
            },
        ],
    )

    assert [match.entity_id for match in matches if match.status == "matched"] == ["KR:1"]
    assert matches[1].exclusion_reason == "identity_unresolved"


def test_five_state_filter_combination_preserves_unknown():
    assert combine_verdicts((FilterVerdict.MATCH, FilterVerdict.UNKNOWN)) == FilterVerdict.UNKNOWN
    assert combine_verdicts((FilterVerdict.MATCH, FilterVerdict.NO_MATCH)) == FilterVerdict.NO_MATCH


def test_company_taxonomy_filters_keep_provider_namespaces_distinct():
    profile = company_search_profile_from_mapping(
        {
            "countries": ["US"],
            "semantic_filters": {"legal_form": ["GLEIF:H1UM"]},
        }
    )
    evaluations = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "US:gleif",
                "country_code": "US",
                "name": "GLEIF form",
                "identity_status": "resolved",
                "taxonomy": {"legal_form": {"namespace": "GLEIF", "code": "H1UM"}},
            },
            {
                "entity_id": "US:ares",
                "country_code": "US",
                "name": "ARES form",
                "identity_status": "resolved",
                "taxonomy": {"legal_form": {"namespace": "ARES", "code": "H1UM"}},
            },
            {
                "entity_id": "US:missing",
                "country_code": "US",
                "name": "No form",
                "identity_status": "resolved",
            },
        ],
    )

    assert {item.entity_id: item.verdict for item in evaluations} == {
        "US:gleif": FilterVerdict.MATCH,
        "US:ares": FilterVerdict.NO_MATCH,
        "US:missing": FilterVerdict.UNKNOWN,
    }
    assert explain_company_evaluation(evaluations[0])["field_verdicts"][-1]["verdict"] == "match"


def test_unqualified_namespaced_taxonomy_value_is_a_conflict_not_a_match():
    profile = CompanySearchProfile(countries=("US",), legal_forms=("H1UM",))
    evaluation = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "US:gleif",
                "country_code": "US",
                "name": "GLEIF form",
                "identity_status": "resolved",
                "taxonomy": {"legal_form": {"namespace": "GLEIF", "code": "H1UM"}},
            }
        ],
    )[0]

    assert evaluation.verdict == FilterVerdict.CONFLICT
    assert evaluation.reason == "legal_form_namespace_required"


def test_namespace_with_colons_matches_against_the_observed_namespace_prefix():
    profile = company_search_profile_from_mapping(
        {
            "countries": ["CZ"],
            "field_filters": [
                {
                    "field": "legal_form",
                    "values": ["ARES:pravniForma:121"],
                    "mode": "all",
                }
            ],
        }
    )
    evaluation = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "CZ:1",
                "country_code": "CZ",
                "name": "Czech form",
                "identity_status": "resolved",
                "taxonomy": {
                    "legal_form": {"namespace": "ARES:pravniForma", "code": "121"}
                },
            }
        ],
    )[0]

    assert evaluation.verdict == FilterVerdict.MATCH


def test_all_mode_requires_every_selected_value_in_the_same_semantic_field():
    profile = company_search_profile_from_mapping(
        {
            "countries": ["CZ"],
            "field_filters": [
                {
                    "field": "business_activity",
                    "values": ["CZ-NACE:6201", "CZ-NACE:6202"],
                    "mode": "all",
                }
            ],
        }
    )
    evaluations = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "CZ:both",
                "country_code": "CZ",
                "name": "Both activities",
                "identity_status": "resolved",
                "taxonomy": {
                    "business_activity": [
                        {"namespace": "CZ-NACE", "code": "6201"},
                        {"namespace": "CZ-NACE", "code": "6202"},
                    ]
                },
            },
            {
                "entity_id": "CZ:one",
                "country_code": "CZ",
                "name": "One activity",
                "identity_status": "resolved",
                "taxonomy": {"business_activity": {"namespace": "CZ-NACE", "code": "6201"}},
            },
        ],
    )

    assert {item.entity_id: item.verdict for item in evaluations} == {
        "CZ:both": FilterVerdict.MATCH,
        "CZ:one": FilterVerdict.NO_MATCH,
    }


def test_legacy_job_only_filter_is_explained_as_not_applicable_to_company_search():
    profile = SearchProfile(countries=("US",), job_keywords=("data",), languages=("korean",))
    evaluation = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "US:1",
                "country_code": "US",
                "name": "Data company",
                "identity_status": "resolved",
            }
        ],
    )[0]

    explanation = explain_company_evaluation(evaluation)
    assert explanation["status"] == "matched"
    assert explanation["field_verdicts"][-1] == {
        "field": "languages",
        "verdict": "not_applicable",
        "expected": ["korean"],
        "mode": "any",
        "observed": [],
        "reason": "languages_requires_job_search",
    }


def test_country_allocation():
    profile = company_search_profile_from_mapping(
        {"countries": ["US"], "job_keywords": ["data"], "country_allocation": {"US": 1}}
    )
    evaluations = rank_candidate_evaluations(
        profile,
        [
            {
                "entity_id": "US:1",
                "country_code": "US",
                "name": "Data company",
                "identity_status": "resolved",
                "evidence_urls": ["https://example.test/1"],
            },
            {
                "entity_id": "US:2",
                "country_code": "US",
                "name": "Data company two",
                "identity_status": "resolved",
            },
        ],
    )

    assert evaluations[0].entity_id == "US:1"
    assert evaluations[0].verdict == FilterVerdict.MATCH
    assert evaluations[1].verdict == FilterVerdict.NO_MATCH
    assert evaluations[1].reason == "country_allocation_reached"
