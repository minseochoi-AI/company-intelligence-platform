import json
from pathlib import Path
from cil_cli.research import main


def test_requirement_necessity_reaches_final_report(tmp_path):
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import run_research
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    request = ReportRequest.from_dict(
        {
            "purpose": ["selected-posting"],
            "question": "필수 자격",
            "as_of": "2026-10-20T00:00:00Z",
            "profile_ref": "me",
            "subject_refs": [
                {"provider_id": "saved", "posting_id": "P", "revision": "r"}
            ],
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    raw = {
        "source_kind": "fixture",
        "profiles": {
            "me": {
                "licence": {
                    "value": "A",
                    "status": "verified",
                    "evidence_ref": "credential-file",
                    "available_at": "2026-10-19T00:00:00Z",
                }
            }
        },
        "postings": [
            {
                "provider_id": "saved",
                "posting_id": "P",
                "revision": "r",
                "available_at": "2026-10-19T00:00:00Z",
                "cluster_signature": "KR:ALL:ALL:ALL:ALL",
                "requirements": [
                    {
                        "requirement_id": "licence",
                        "necessity": "required",
                        "kind": "observed",
                        "field": "licence",
                        "operator": "eq",
                        "value": "A",
                        "source_id": "posting",
                    }
                ],
            }
        ],
    }
    store = ResearchArtifactStore(tmp_path)
    run_research(
        request, raw, CapabilityRegistry(), store, renderer=render_research_workbook
    )
    rows = json.loads(store.read("tables.json"))["Requirements"]
    assert len(rows) == 1 and rows[0]["verdict"] == "match"


def test_user_filter_unknown_policy_is_applied_and_extra_root_rejected(
    tmp_path, capsys
):
    folder = Path(__file__).resolve().parents[1] / "research/fixtures"
    value = json.loads((folder / "research-request.json").read_text())
    value["field_filters"] = [
        {
            "field_id": "salary_min",
            "operator": "gte",
            "value": 1,
            "unknown_policy": "error",
        }
    ]
    request = tmp_path / "request.json"
    request.write_text(json.dumps(value))
    assert (
        main(
            [
                "validate",
                "--request",
                str(request),
                "--snapshot",
                str(folder / "selected-posting.json"),
            ]
        )
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["selected_postings"] == [] and len(result["exclusions"]) == 4
    value["private_success_probability"] = 0.99
    request.write_text(json.dumps(value))
    assert (
        main(
            [
                "validate",
                "--request",
                str(request),
                "--snapshot",
                str(folder / "selected-posting.json"),
            ]
        )
        == 2
    )
