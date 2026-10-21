import pytest


def test_instance_constraints_are_request_fields_not_global_defaults(proof):
    from cil_contracts.requests import ReportRequest

    value = {
        "purpose": ["financial"],
        "question": "기업 비교",
        "as_of": "2026-10-20T00:00:00Z",
    }
    request = proof.invoke(
        "AR-D05-contract",
        ReportRequest.from_dict,
        value,
        checks={
            "input": lambda b, a, r, e: (
                "profile_ref" not in b["args"][0]
                and b["args"][0]["purpose"] == ["financial"]
            ),
            "return": lambda b, a, r, e: (
                e is None and r.cohort_signature == "ALL:ALL:ALL:ALL:ALL"
            ),
            "relation": lambda b, a, r, e: (
                r.subject_refs == ()
                and "profile_ref" not in r.as_dict()
                and r.question == b["args"][0]["question"]
            ),
        },
    )
    assert request.cohort_signature == "ALL:ALL:ALL:ALL:ALL"
    assert request.subject_refs == () and "profile_ref" not in request.as_dict()
    for field in ("degree", "nuclear_only", "energy_only", "six_files"):
        with pytest.raises(ValueError, match="unknown request"):
            ReportRequest.from_dict({**value, field: True})
