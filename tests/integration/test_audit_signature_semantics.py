import json
from pathlib import Path
from cil_cli.main import main


def test_us_saved_export_and_invalid_extra_dimension(tmp_path, capsys):
    source = (
        Path(__file__).resolve().parents[1] / "research/fixtures/selected-posting.json"
    )
    output = tmp_path / "us.xlsx"
    flags = [
        "export-cluster-jobs",
        "--snapshot",
        str(source),
        "--as-of",
        "2026-10-20T00:00:00Z",
        "--output",
        str(output),
        "--json-output",
    ]
    assert main([*flags, "--signature", "US:GOVERNMENT:ALL:REGULAR:ALL"]) == 0
    assert json.loads(capsys.readouterr().out)["total_matched"] == 1
    assert main([*flags, "--signature", "US:ALL:ALL:ALL:ALL:extra"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "ERROR"
