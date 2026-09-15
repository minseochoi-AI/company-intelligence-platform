import pytest

from company_intel.query_contract import (
    FilterMode,
    FilterVerdict,
    SemanticValue,
    UnknownPolicy,
    combine_verdicts,
    company_search_profile_from_mapping,
    normalize_tree_selection,
)


def test_field_filter_verdicts_preserve_explicit_semantic_axes_and_allocations():
    profile = company_search_profile_from_mapping(
        {
            "countries": ["us", "cz"],
            "job_keywords": ["data"],
            "country_allocation": {"us": 2, "CZ": 1},
            "semantic_filters": {
                "ownership_sector": ["public_institution"],
                "legal_form": ["GLEIF:H1UM"],
                "business_activity": ["SEC:3571"],
            },
            "unknown_policy": "report",
            "require_resolved_identity": True,
        }
    )

    assert profile.countries == ("US", "CZ")
    assert profile.allocation == {"US": 2, "CZ": 1}
    assert profile.semantic_filters() == {
        "ownership_sector": ("public_institution",),
        "legal_form": ("GLEIF:H1UM",),
        "business_activity": ("SEC:3571",),
    }
    assert profile.unknown_policy == UnknownPolicy.REPORT


def test_field_filter_keeps_all_mode_and_provider_namespace_selector_intact():
    profile = company_search_profile_from_mapping(
        {
            "countries": ["CZ"],
            "field_filters": [
                {
                    "field": "legal_form",
                    "values": ["ARES:pravniForma:121", "ARES:pravniForma:111"],
                    "mode": "all",
                }
            ],
        }
    )

    field_filter = profile.filters()[0]
    assert field_filter.mode == FilterMode.ALL
    assert field_filter.values[0] == "ARES:pravniForma:121"


def test_mapping_adapter_rejects_ambiguous_boolean_and_invalid_policy():
    with pytest.raises(ValueError, match="boolean"):
        company_search_profile_from_mapping(
            {"countries": ["US"], "job_keywords": ["data"], "require_resolved_identity": "false"}
        )
    with pytest.raises(ValueError, match="unknown_policy"):
        company_search_profile_from_mapping(
            {"countries": ["US"], "job_keywords": ["data"], "unknown_policy": "maybe"}
        )


def test_semantic_value_selector_retains_its_namespace():
    assert SemanticValue(value="H1UM", namespace="GLEIF").selector == "GLEIF:H1UM"
    assert combine_verdicts((FilterVerdict.MATCH, FilterVerdict.CONFLICT)) == FilterVerdict.CONFLICT


def test_current_and_trend_mode_contracts_are_distinct():
    assert normalize_tree_selection({"purpose": "current_jobs", "selections": {"country": "KR"}}).mode.value == "current_job"
    assert normalize_tree_selection({"purpose": "job_trends", "selections": {}}).mode.value == "job_trend"
