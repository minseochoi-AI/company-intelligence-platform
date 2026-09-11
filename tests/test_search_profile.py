import pytest

from company_intel.models import SearchProfile
from company_intel.query_contract import FilterVerdict, combine_verdicts
from company_intel.search import rank_candidates, validate_search_profile


def test_profile_requires_explicit_country_and_goal():
    with pytest.raises(ValueError, match="countries"):
        validate_search_profile(SearchProfile(countries=(), job_keywords=("data",)))


def test_ranking_preserves_unresolved_identity_as_an_exclusion():
    profile = SearchProfile(countries=("KR",), job_keywords=("data",), required_capabilities=("job_posting",))
    matches = rank_candidates(
        profile,
        [
                {"entity_id": "KR:1", "country_code": "KR", "name": "Verified", "title": "Data engineer", "capabilities": {"job_posting": "available"}, "identity_status": "resolved"},
            {"entity_id": "KR:2", "country_code": "KR", "name": "Unknown", "capabilities": {"job_posting": "available"}, "identity_status": "unresolved"},
        ],
    )

    assert [match.entity_id for match in matches if match.status == "matched"] == ["KR:1"]
    assert matches[1].exclusion_reason == "identity_unresolved"


def test_five_state_filter_combination_preserves_unknown():
    assert combine_verdicts((FilterVerdict.MATCH, FilterVerdict.UNKNOWN)) == FilterVerdict.UNKNOWN
    assert combine_verdicts((FilterVerdict.MATCH, FilterVerdict.NO_MATCH)) == FilterVerdict.NO_MATCH
