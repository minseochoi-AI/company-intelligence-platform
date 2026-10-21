import json
from pathlib import Path
from cil_cli.research import main


def test_canonical_object_order_has_the_same_run_identity_and_bytes(tmp_path):
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import run_research
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    request = ReportRequest.from_dict(
        {
            "purpose": ["financial"],
            "question": "키 순서",
            "as_of": "2026-10-20T00:00:00Z",
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    left = {"source_kind": "fixture", "postings": [], "nested": {"a": 0, "b": False}}
    right = {"nested": {"b": False, "a": 0}, "postings": [], "source_kind": "fixture"}
    stores = [
        ResearchArtifactStore(tmp_path / "left"),
        ResearchArtifactStore(tmp_path / "right"),
    ]
    outputs = [
        run_research(
            request,
            source,
            CapabilityRegistry(),
            store,
            renderer=render_research_workbook,
        )
        for source, store in zip((left, right), stores)
    ]
    assert outputs[0]["run_id"] == outputs[1]["run_id"]
    assert stores[0].read("research.xlsx") == stores[1].read("research.xlsx")


def test_same_saved_inputs_produce_identical_bytes_in_separate_runs(tmp_path, capsys):
    folder = Path(__file__).resolve().parents[1] / "research/fixtures"
    outputs = []
    for name in ("one", "two"):
        directory = tmp_path / name
        assert (
            main(
                [
                    "run",
                    "--request",
                    str(folder / "research-request.json"),
                    "--snapshot",
                    str(folder / "selected-posting.json"),
                    "--output",
                    str(directory),
                ]
            )
            == 0
        )
        result = json.loads(capsys.readouterr().out)
        outputs.append((directory / result["run_id"] / "research.xlsx").read_bytes())
    assert outputs[0] == outputs[1]
