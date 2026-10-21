from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".codex/skills/kr-defensible-venture-discovery"


def _module():
    spec = spec_from_file_location("venture_artifacts", SKILL / "scripts/venture_artifacts.py")
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _opportunity():
    return {
        "schema_version": "1.0.0", "hypothesis_id": "h-1", "revision": 1, "sector": "welfare",
        "problem": "manual inspection", "buyer": "municipality", "user": "caseworker", "payer": "municipality",
        "solution": "retrofit inspection aid", "market_archetype": "unverified-white-space",
        "market_sizing": {"tam": 100, "sam": 30, "som": 3, "unit": "accounts", "formula": "accounts * price", "assumptions": ["annual"]},
        "competitors": [], "substitutes": ["manual process"],
        "barriers": [{"kind": "workflow", "claim": "audit trail", "acquisition_path": "pilot", "cost_time": "3 months", "verification": "paid pilot", "copyability_risk": "platform bundling"}],
        "data_rights": [{"source_ref": "public-1", "acquisition": "API", "analysis": "allowed", "product_use": "allowed", "personal_data": "none", "refresh_cost": "monthly"}],
        "evidence_refs": ["search-1"], "unresolved": [], "experiments": ["five interviews"], "kill_criteria": ["no paid pilot intent"],
    }


def test_market_archetypes_have_distinct_proof_burdens():
    module = _module()
    value = _opportunity()
    module.validate_opportunity(value)
    value["market_archetype"] = "niche"
    with pytest.raises(module.ArtifactError, match="named competitor"):
        module.validate_opportunity(value)
    value["market_archetype"] = "unverified-white-space"
    value["substitutes"] = []
    with pytest.raises(module.ArtifactError, match="substitutes"):
        module.validate_opportunity(value)


def test_gap_detection_includes_unknown_product_rights():
    module = _module()
    value = _opportunity()
    value["data_rights"][0]["product_use"] = "unknown"
    assert "data_rights[0].product_use" in module.opportunity_gaps(value)


def test_session_preserves_barrier_and_reports_all_constraint_gaps():
    module = _module()
    constraints = {
        "time_hours_per_week": None, "budget_krw": None, "location": "KR",
        "risk_tolerance": None, "available_resources": ["programming", "government server"],
        "field_access": None, "hardware_tolerance": None, "regulatory_tolerance": None,
        "sales_horizon_months": None, "desired_barriers": ["physical"], "runway_months": None,
        "hardware_prototype_budget_krw": None, "certifications": [],
        "forbidden_paths": ["head-on enterprise competition"],
    }
    value = {
        "schema_version": "1.0.0", "session_id": "s-1", "revision": 1,
        "mode": "CONFIGURE", "generated_at": "2026-09-15T00:00:00+00:00",
        "founder_constraints": constraints, "target_sectors": ["agriculture", "welfare", "education"],
        "non_goals": [], "hypothesis_refs": [], "evidence_bundle_refs": [], "research_gaps": [],
    }
    calculated = module.session_gaps(value)
    assert "founder_constraints.runway_months" in calculated
    assert "founder_constraints.hardware_prototype_budget_krw" in calculated
    value["research_gaps"] = calculated
    module.validate_session(value)
    value["research_gaps"] = []
    with pytest.raises(module.ArtifactError, match="research_gaps must equal"):
        module.validate_session(value)
    value["research_gaps"] = calculated + ["founder_constraints.fake"]
    with pytest.raises(module.ArtifactError, match="extra"):
        module.validate_session(value)


def test_skill_forbids_no_competitor_blue_ocean_inference():
    text = (ROOT / ".agents/skills/kr-defensible-venture-discovery/SKILL.md").read_text(encoding="utf-8")
    assert "payment_evidence_refs" in text
    assert "kill_criteria" in text
    assert "AI" in text
