import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".codex/shared/company-intelligence-interop/interop.py"


def _module():
    spec = spec_from_file_location("company_intel_interop", MODULE_PATH)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_pair(root: Path, kind: str, *, missing_budget: bool = False):
    interop = _module()
    plan = interop._plan(kind, f"{kind}-plan")
    if missing_budget:
        plan["constraints"]["budget_krw"] = None
    plan_path = root / f"{kind}.json"
    plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
    ref = {"schema_version": "1.0.0", "plan_kind": kind, "plan_id": f"{kind}-plan", "revision": 1, "path": plan_path.name, "sha256": interop.digest(plan_path), "generated_at": "2026-09-15T00:00:00+00:00", "evidence_bundle_refs": []}
    ref_path = root / f"{kind}-ref.json"
    ref_path.write_text(json.dumps(ref) + "\n", encoding="utf-8")
    return ref_path, plan_path


def test_dual_path_comparison_is_neutral_and_reports_missing_axes(tmp_path):
    interop = _module()
    career_ref, _ = _write_pair(tmp_path, "career")
    venture_ref, _ = _write_pair(tmp_path, "venture", missing_budget=True)
    result = interop.compare(career_ref, venture_ref)
    assert result["decision"] == "human-required"
    assert result["status"] == "partial"
    assert "budget_krw" in result["unresolved_axes"]
    assert result["career_plan_ref"]["path"] == "career-ref.json"
    assert result["career_plan_ref"]["sha256"].startswith("sha256:")
    interop.validate_dual_path_comparison(result)


def test_comparison_rejects_invalid_time_and_axis_rows(tmp_path):
    interop = _module()
    career_ref, _ = _write_pair(tmp_path, "career")
    venture_ref, _ = _write_pair(tmp_path, "venture")
    result = interop.compare(career_ref, venture_ref)
    result["generated_at"] = "not-a-date"
    with pytest.raises(interop.ContractError, match="ISO-8601"):
        interop.validate_dual_path_comparison(result)
    result = interop.compare(career_ref, venture_ref)
    result["axes"][0] = "bad-row"
    with pytest.raises(interop.ContractError, match="object"):
        interop.validate_dual_path_comparison(result)


def test_comparison_file_rejects_tampered_hash_and_parent_traversal(tmp_path):
    interop = _module()
    career_ref, _ = _write_pair(tmp_path, "career")
    venture_ref, _ = _write_pair(tmp_path, "venture")
    result = interop.compare(career_ref, venture_ref)
    comparison = tmp_path / "comparison.json"
    comparison.write_text(json.dumps(result), encoding="utf-8")
    interop.verify_dual_path_comparison_refs(result, comparison)
    result["career_plan_ref"]["sha256"] = "sha256:" + "0" * 64
    with pytest.raises(interop.ContractError, match="does not match"):
        interop.verify_dual_path_comparison_refs(result, comparison)
    result["career_plan_ref"]["path"] = "../career-ref.json"
    with pytest.raises(interop.ContractError, match="traverse"):
        interop.verify_dual_path_comparison_refs(result, comparison)


def test_domain_plan_ref_rejects_tamper_and_path_traversal(tmp_path):
    interop = _module()
    ref_path, plan_path = _write_pair(tmp_path, "career")
    plan_path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(interop.ContractError, match="sha256"):
        interop.verify_domain_plan_ref(ref_path)
    ref = json.loads(ref_path.read_text())
    ref["path"] = "../outside.json"
    ref_path.write_text(json.dumps(ref), encoding="utf-8")
    with pytest.raises(interop.ContractError, match="traverse"):
        interop.verify_domain_plan_ref(ref_path)


def test_shared_package_is_not_a_fourth_skill():
    assert not (ROOT / ".codex/shared/company-intelligence-interop/SKILL.md").exists()
    boundaries = (ROOT / ".codex/shared/company-intelligence-interop/BOUNDARIES.md").read_text()
    assert "non-skill contract package" in boundaries
