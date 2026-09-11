from company_intel.career_requirements import (
    normalize_requirement,
    requirement_dedupe_key,
    verify_requirement,
)


def test_required_and_preferred_requirements_remain_distinct():
    required = normalize_requirement({"text": "정보처리기사", "kind": "required", "source_url": "https://example.test/job"})
    preferred = normalize_requirement({"text": "AWS", "kind": "preferred", "source_url": "https://example.test/job"})

    assert required.status == "required"
    assert preferred.status == "preferred"


def test_missing_detail_is_unavailable_not_an_invented_certificate():
    result = verify_requirement({"title": "Engineer"}, country_code="CZ")

    assert result.availability == "requirement_unavailable"
    assert result.requirements == ()


def test_license_and_certificate_do_not_share_a_deduplication_key():
    assert requirement_dedupe_key(kind="license", label="Electrician", necessity="required", jurisdiction="CZ") != requirement_dedupe_key(kind="certification", label="Electrician", necessity="required", jurisdiction="CZ")
