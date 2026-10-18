import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/flowchart_matrix.py"
MMDC = ROOT / "tools/mermaid-renderer/node_modules/.bin/mmdc"
MERMAID_CONFIG = ROOT / "tools/mermaid-renderer/mermaid.config.json"
PUPPETEER_CONFIG = ROOT / "tools/mermaid-renderer/puppeteer.local.json"


def fixture(root: Path) -> tuple[Path, Path, Path]:
    module_path = ROOT / "tests/tools/test_flowchart_matrix.py"
    spec = importlib.util.spec_from_file_location("flowchart_fixture", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_fixture(root)


def build(evidence: Path, design: Path, output_dir: Path, review: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(TOOL), "build", "--evidence", str(evidence), "--design", str(design), "--output-dir", str(output_dir), "--review-packet", str(review), "--mmdc", str(MMDC), "--mermaid-config", str(MERMAID_CONFIG), "--puppeteer-config", str(PUPPETEER_CONFIG)]
    if check:
        command.append("--check")
    return subprocess.run(command, text=True, capture_output=True, check=False)


def test_renders_svg_and_png_with_byte_freshness(tmp_path: Path) -> None:
    assert MMDC.is_file()
    evidence, design, _ = fixture(tmp_path)
    first, second = tmp_path / "first", tmp_path / "second"
    assert build(evidence, design, first, tmp_path / "review-a.md").returncode == 0
    assert build(evidence, design, second, tmp_path / "review-b.md").returncode == 0
    for suffix, signature in (("svg", b"<svg"), ("png", b"\x89PNG\r\n\x1a\n")):
        left, right = first / f"VIEW-1.{suffix}", second / f"VIEW-1.{suffix}"
        assert left.read_bytes().lstrip().startswith(signature)
        assert left.read_bytes() == right.read_bytes()
    assert build(evidence, design, first, tmp_path / "review-a.md", check=True).returncode == 0
    payload = json.loads((tmp_path / "matrices/one.flowchart-matrix.json").read_text(encoding="utf-8"))
    payload["logic_matrix"]["steps"][1]["output"] = "changed"
    (tmp_path / "matrices/one.flowchart-matrix.json").write_text(json.dumps(payload), encoding="utf-8")
    assert build(evidence, design, first, tmp_path / "review-a.md", check=True).returncode != 0


def test_rejects_invalid_mermaid_source(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.mmd"
    invalid.write_text("flowchart TD\n  A -->", encoding="utf-8")
    result = subprocess.run([str(MMDC), "-i", str(invalid), "-o", str(tmp_path / "invalid.svg"), "-c", str(MERMAID_CONFIG), "-p", str(PUPPETEER_CONFIG)], text=True, capture_output=True, check=False)
    assert result.returncode != 0
