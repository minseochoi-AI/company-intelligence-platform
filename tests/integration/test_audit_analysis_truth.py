import json
from pathlib import Path
from cil_cli.main import main


def test_unavailable_analysis_does_not_publish_or_create_a_workbook(tmp_path, capsys):
    output = tmp_path / "should-not-exist.xlsx"
    assert (
        main(["temporal-analytics", "--export-excel", str(output), "--publish-notion"])
        == 2
    )
    assert json.loads(capsys.readouterr().out)["status"] == "NEEDS_EVIDENCE"
    assert not output.exists()
