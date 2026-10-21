import json
from cil_integrations.storage.taxonomy_sources import load_taxonomy_sources
from cil_reporting.xlsx.occupations import build_occupational_lattice_workbook
from cil_integrations.validation.workbooks import ExcelProvenanceValidator


def test_explicit_taxonomy_loader_and_render_do_not_certify_measurements(tmp_path):
    source = tmp_path / "taxonomy.json"
    source.write_text(
        json.dumps(
            {
                "schema_version": "taxonomy-input-v1",
                "source_id": "fixture",
                "taxonomy": [
                    {
                        "code": "2512",
                        "title_en": "Software developers",
                        "description": "",
                        "tasks": "",
                        "examples": "",
                        "related_codes": [],
                        "major": "2",
                        "submajor": "25",
                        "minor": "251",
                    }
                ],
            }
        )
    )
    graph = load_taxonomy_sources(source).build_deterministic_macro_graph()
    output = build_occupational_lattice_workbook(
        tmp_path / "taxonomy.xlsx", graph=graph
    )
    report = ExcelProvenanceValidator(output).verify_all_matrices()
    assert report.passed_matrices == 0 and report.to_dict()["status"] == "UNVERIFIED"
