from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from company_intel.run_manifest import build_run_manifest, write_run_manifest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".codex/skills/company-intelligence-analysis"


def _module():
    spec = spec_from_file_location("verify_cil_artifact", SKILL / "scripts/verify_cil_artifact.py")
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_has_specific_boundaries_and_valid_metadata():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "thin evidence orchestrator" in text
    assert "company-intelligence-career-research" in text
    assert "kr-defensible-venture-discovery" in text
    metadata = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
    assert "$company-intelligence-analysis" in metadata
    assert "allow_implicit_invocation: true" in metadata


def test_verify_cil_manifest_accepts_valid_and_rejects_tamper(tmp_path):
    manifest = build_run_manifest("test", profile={"country": "KR"}, generated_at="2026-09-15T00:00:00+00:00")
    path = tmp_path / "run-manifest.json"
    write_run_manifest(path, manifest)
    verify = _module()
    assert verify.verify(path)[0]
    manifest["profile"]["country"] = "US"
    write_run_manifest(path, manifest)
    assert not verify.verify(path)[0]
