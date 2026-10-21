import pytest


def test_observed_snapshot_cannot_promote_explicit_fixture_records():
    from cil_contracts.requests import ReportRequest
    from cil_application.research.request_compiler import compile_request
    from cil_integrations.research.capability_registry import CapabilityRegistry

    request = ReportRequest.from_dict(
        {
            "purpose": ["financial"],
            "question": "출처 혼합 방지",
            "as_of": "2026-10-20T00:00:00Z",
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    result = compile_request(
        request,
        {"source_kind": "observed", "postings": [{"source_kind": "fixture"}]},
        CapabilityRegistry(),
    )
    assert result["status"] == "NEEDS_EVIDENCE"
    assert any(
        g["reason"] == "fixture_cannot_be_promoted_to_observed" for g in result["gaps"]
    )


def test_request_rejects_unconsumed_signature_dimensions_and_fields():
    from cil_contracts.requests import ReportRequest

    request = {
        "purpose": ["selected-posting"],
        "question": "공고 평가",
        "as_of": "2026-10-20T00:00:00+09:00",
    }
    with pytest.raises(ValueError, match="five"):
        ReportRequest.from_dict(
            {**request, "cohort_signature": "KR:ALL:ALL:ALL:ALL:ignored"}
        )
    with pytest.raises(ValueError, match="unknown request"):
        ReportRequest.from_dict({**request, "applicant_success_probability": 0.9})


def test_complete_cohort_does_not_replace_selected_posting_evidence(proof):
    from cil_contracts.requests import ReportRequest
    from cil_application.research.request_compiler import compile_request
    from cil_integrations.research.capability_registry import CapabilityRegistry

    request = ReportRequest.from_dict(
        {
            "purpose": ["selected-posting"],
            "question": "지원 조건 평가",
            "cohort_signature": "KR:PUBLIC_INSTITUTION:SOE_MARKET:REGULAR:ONSITE",
            "as_of": "2026-10-20T00:00:00+09:00",
        }
    )
    result = proof.invoke(
        "SK-D02-contract",
        compile_request,
        request,
        {"postings": [], "source_kind": "fixture"},
        CapabilityRegistry(),
        checks={
            "input": lambda b, a, r, e: b["args"][0].purpose == ("selected-posting",),
            "return": lambda b, a, r, e: e is None and r["status"] == "NEEDS_INPUT",
            "relation": lambda b, a, r, e: (
                not b["args"][0].subject_refs
                and any(g["field"] == "subject_refs" for g in r["gaps"])
            ),
        },
    )
    assert result["status"] == "NEEDS_INPUT"
    assert any(x["field"] == "subject_refs" for x in result["gaps"])
    assert result["selected_skills"] == ["S01", "S02", "S08"]


def test_nested_options_cannot_be_silently_ignored():
    from cil_contracts.requests import ReportRequest

    request = {
        "purpose": ["financial"],
        "question": "재무 비교",
        "as_of": "2026-10-20T00:00:00Z",
    }
    with pytest.raises(ValueError, match="unsupported.*history"):
        ReportRequest.from_dict({**request, "history": {"invented_window": 10}})
    with pytest.raises(ValueError, match="metric"):
        ReportRequest.from_dict(
            {
                **request,
                "metric_specs": [
                    {"metric_id": "hiring_success_probability", "method_version": "1"}
                ],
            }
        )


def test_origin_coverage_and_saved_source_hash_are_verified():
    from cil_contracts.requests import ReportRequest, content_hash
    from cil_application.research.request_compiler import compile_request
    from cil_integrations.research.capability_registry import (
        CapabilityRegistry,
        OperationStatus,
    )

    base = {
        "purpose": ["financial"],
        "question": "과거 비교",
        "as_of": "2026-10-20T00:00:00Z",
        "argument_origins": [{"json_pointer": "/question", "origin": "user_explicit"}],
    }
    registry = CapabilityRegistry(
        [
            OperationStatus(
                "facts", "provider", "1", (), ("revenue",), "entity_period", "local"
            )
        ]
    )
    source = {
        "source_id": "s1",
        "snapshot_hash": content_hash({"revenue": 1}),
        "payload": {"revenue": 999},
    }
    binding = {
        "source_id": "s1",
        "provider_id": "provider",
        "operation_id": "facts",
        "schema_version": "1",
        "snapshot_hash": source["snapshot_hash"],
    }
    result = compile_request(
        ReportRequest.from_dict({**base, "source_bindings": [binding]}),
        {"source_kind": "fixture", "sources": [source]},
        registry,
    )
    reasons = {g["reason"] for g in result["gaps"]}
    assert "bound_payload_hash_mismatch" in reasons
    assert "argument_origin_not_covered" in reasons
