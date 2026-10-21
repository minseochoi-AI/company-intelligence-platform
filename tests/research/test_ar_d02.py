import pytest


def test_listing_size_and_nonprofit_type_do_not_establish_private_or_public_ownership():
    from cil_integrations.providers.job_records import (
        from_kr_opendart,
        from_kr_worknet,
        from_cz_ares,
        from_us_sec_or_usaspending,
    )

    assert from_kr_opendart("Y").sector == "UNKNOWN"
    assert from_kr_worknet("01").sector == "UNKNOWN"
    assert from_cz_ares("112").sector == "UNKNOWN"
    assert from_us_sec_or_usaspending("higher_education").sector == "UNKNOWN"


def test_non_regular_and_new_api_values_survive_normalization(proof):
    from cil_integrations.providers.job_records import from_kr_public_job_record

    raw = {
        "idx": "one",
        "url": "https://example.test/one",
        "insttNm": "Example",
        "title": "Role",
        "employment_type": "비정규직",
        "salary_min": 0,
        "description": "x" * 500,
        "new_api_field": {"flag": False},
    }
    row = proof.invoke(
        "AR-D02-contract",
        from_kr_public_job_record,
        raw,
        checks={
            "input": lambda b, a, r, e: (
                b["args"][0]["employment_type"] == "비정규직"
                and b["args"][0]["salary_min"] == 0
            ),
            "return": lambda b, a, r, e: (
                e is None and r.cluster_signature.contract == "NON_REGULAR"
            ),
            "relation": lambda b, a, r, e: (
                r.salary_min == 0
                and r.description == b["args"][0]["description"]
                and r.to_dict()["raw_attributes"]["new_api_field"]
                == b["args"][0]["new_api_field"]
            ),
        },
    )
    assert row.cluster_signature.contract == "NON_REGULAR"
    assert row.salary_min == 0 and len(row.description) == 500
    assert row.to_dict()["raw_attributes"]["new_api_field"] == {"flag": False}


def test_signature_query_does_not_treat_unknown_record_as_wildcard():
    from cil_domain.clusters.signature import ClusterSignature

    query = ClusterSignature.parse("KR:STATE_OWNED:ALL:REGULAR:ALL")
    assert not query.matches(ClusterSignature.parse("KR:ALL:ALL:REGULAR:ALL"))
    with pytest.raises(ValueError, match="five"):
        ClusterSignature.parse("KR:ALL:ALL:ALL:ALL:ignored")


def test_text_false_and_employer_address_do_not_establish_job_identity():
    from cil_integrations.providers.job_records import from_cz_mpsv_job_record

    row = from_cz_mpsv_job_record(
        {
            "job_id": "one",
            "job_url": "https://example.test/one",
            "employer_name": "Example",
            "job_title": "Role",
            "public_administration_flag": "False",
            "employer_address": "Prague",
        }
    )
    assert row.cluster_signature.sector == "UNKNOWN"
    assert row.location == "unknown"
    assert row.education_level == "unknown"
