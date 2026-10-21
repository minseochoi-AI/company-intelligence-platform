import importlib.util
from pathlib import Path
import pytest


def interop():
    path = (
        Path(__file__).resolve().parents[2]
        / ".codex/shared/company-intelligence-interop/interop.py"
    )
    spec = importlib.util.spec_from_file_location("research_interop", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v2_evidence_does_not_require_fabricated_confidence_and_v1_still_validates(
    proof,
):
    module = interop()
    value = {
        "schema_version": "2.0.0",
        "bundle_id": "one",
        "generated_at": "2026-10-20T00:00:00Z",
        "producer": "test",
        "subject": "test",
        "sources": [
            {
                "source_id": "s1",
                "locator": "local",
                "observed_at": "2026-10-19T00:00:00Z",
                "content_hash": "sha256:" + "a" * 64,
                "rights_status": "unknown",
            }
        ],
        "claims": [
            {
                "claim_id": "c1",
                "statement": "미확인",
                "source_ids": ["s1"],
                "kind": "unknown",
                "value": None,
                "reason": "not_observed",
            }
        ],
        "redaction_status": "none",
    }
    proof.invoke(
        "SK-D06-contract",
        module.validate_evidence_bundle,
        value,
        checks={
            "input": lambda b, a, r, e: (
                b["args"][0]["schema_version"] == "2.0.0"
                and "confidence" not in b["args"][0]["claims"][0]
            ),
            "return": lambda b, a, r, e: e is None and r is None,
            "relation": lambda b, a, r, e: (
                b["args"][0] == a["args"][0]
                and a["args"][0]["claims"][0]["value"] is None
            ),
        },
    )
    assert "confidence" not in value["claims"][0]
    value["schema_version"] = "3.0.0"
    with pytest.raises(module.ContractError):
        module.validate_evidence_bundle(value)
    module.validate_domain_plan(module._plan("career", "v1"))


def test_v2_domain_budget_requires_explicit_money():
    module = interop()
    value = module._plan("career", "v2")
    value["schema_version"] = "2.0.0"
    value["constraints"].pop("budget_krw")
    value["constraints"]["budget"] = {"amount": 100, "currency": "EUR"}
    module.validate_domain_plan(value)
    value["constraints"]["budget"].pop("currency")
    with pytest.raises(module.ContractError, match="Money"):
        module.validate_domain_plan(value)
