import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/flowchart_matrix.py"


def write_fixture(root: Path) -> tuple[Path, Path, Path]:
    evidence = {
        "documents": [{"id": "DOC-1", "source_locator": {"kind": "local_file", "path": "decision.json"}}],
        "claims": [{"id": "CL-1", "evidence_refs": ["DOC-1"]}],
        "decision_ledger": [{"id": "DL-1", "final_rule": "render only approved design", "status": "accepted"}],
    }
    design = {
        "semantic_review": {"status": "approved"},
        "rr_rows": [{"id": "RR-1"}],
        "architecture_boundaries": [{"id": "BD-1"}],
        "flow_units": [{"id": "FLOW-1", "matrix_path": "matrices/one.flowchart-matrix.json", "start_contract": "approved input", "end_contract": "derived Mermaid", "required_claim_refs": ["CL-1"], "required_decision_refs": ["DL-1"], "required_rr_ids": ["RR-1"], "required_boundary_ids": ["BD-1"]}],
        "diagram_views": [{"id": "VIEW-1", "kind": "flowchart", "source_flow_id": "FLOW-1", "orientation": "TD"}],
    }
    matrix = {
        "default_evidence_refs": ["CL-1"],
        "swimlane_matrix": {"lanes": [{"id": "LANE-1", "name": "Agent"}], "phases": [{"id": "PHASE-1", "name": "Validate", "steps_by_lane": {"LANE-1": ["START", "WORK", "END"]}}]},
        "logic_matrix": {"steps": [
            {"id": "START", "phase_id": "PHASE-1", "lane_id": "LANE-1", "type": "start", "implementation_status": "validated", "output": "approved input", "next_step_ids": ["WORK"]},
            {"id": "WORK", "phase_id": "PHASE-1", "lane_id": "LANE-1", "type": "process", "implementation_status": "planned", "output": "derived Mermaid", "next_step_ids": ["END"]},
            {"id": "END", "phase_id": "PHASE-1", "lane_id": "LANE-1", "type": "end", "implementation_status": "planned", "output": "complete"},
        ]},
        "semantic_review": {"status": "approved", "flow_id": "FLOW-1", "claim_refs": ["CL-1"], "decision_refs": ["DL-1"], "rr_ids": ["RR-1"], "boundary_ids": ["BD-1"]},
    }
    evidence_path, design_path, matrix_path = root / "evidence.json", root / "design.json", root / "matrices/one.flowchart-matrix.json"
    matrix_path.parent.mkdir()
    for path, value in ((evidence_path, evidence), (design_path, design), (matrix_path, matrix)):
        path.write_text(json.dumps(value), encoding="utf-8")
    return evidence_path, design_path, matrix_path


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False)


def test_validates_and_compiles(tmp_path: Path) -> None:
    evidence, design, matrix = write_fixture(tmp_path)
    assert run("validate-evidence", str(evidence)).returncode == 0
    assert run("validate-design", str(design), "--evidence", str(evidence)).returncode == 0
    assert run("validate", str(matrix), "--design", str(design), "--evidence", str(evidence)).returncode == 0
    output = tmp_path / "one.mmd"
    assert run("compile-mermaid", str(matrix), "--output", str(output)).returncode == 0
    assert output.read_text(encoding="utf-8").startswith("%% GENERATED")
    assert run("compile-mermaid", str(matrix), "--output", str(output), "--check").returncode == 0
    payload = json.loads(matrix.read_text(encoding="utf-8"))
    payload["logic_matrix"]["steps"][1]["output"] = "changed"
    matrix.write_text(json.dumps(payload), encoding="utf-8")
    assert run("compile-mermaid", str(matrix), "--output", str(output), "--check").returncode == 1


def test_rejects_invalid_matrix(tmp_path: Path) -> None:
    evidence, design, matrix = write_fixture(tmp_path)
    payload = json.loads(matrix.read_text(encoding="utf-8"))
    payload["logic_matrix"]["steps"][1]["type"] = "decision"
    matrix.write_text(json.dumps(payload), encoding="utf-8")
    result = run("validate", str(matrix), "--design", str(design), "--evidence", str(evidence))
    assert result.returncode == 1
    assert "needs a condition" in result.stdout
