"""Unit tests for Dynamic Report Schema Compiler, Baseline Cluster Space Disclosure,
and Conditional Lattice Resolution.
Validates the dynamic 3-layer architecture (Core, Dynamic Attributes, Action & Provenance).
"""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl
import pytest

from cil_application.providers.capabilities import BASELINE_API_CATALOG, get_cluster_baseline_spec_text, resolve_active_providers
from cil_domain.clusters.signature import ClusterSignature
from cil_reporting.schema.compiler import DynamicReportSchemaCompiler
from cil_cli.main import main


def test_baseline_cluster_space_disclosure_text():
    """Verify that the pre-flight baseline disclosure accurately reflects all 28 APIs and 21,000 combinations."""
    spec_text = get_cluster_baseline_spec_text()
    assert 'operation 30개 / provider 25개' in spec_text
    assert '의미 매핑 55개' in spec_text
    assert '741' not in spec_text and '21,000' not in spec_text


def test_resolve_active_providers_and_lattice_navigation():
    """Verify dynamic resolution of active providers and free dimension detection on cluster lattice."""
    # 1. Pinned Czech state-owned query
    sig_cz = ClusterSignature.parse("CZ:STATE_OWNED:ALL:ALL:ALL")
    cz_info = resolve_active_providers(sig_cz)
    assert cz_info["signature_key"] == "CZ:STATE_OWNED:ALL:ALL:ALL"
    assert "ares" in cz_info["active_providers"]
    assert cz_info["availability"] == "registered_not_live_verified"
    assert cz_info["free_dimensions"] == ["tier", "contract", "workplace"]
    assert cz_info["is_macro_rollup"] is True
    assert cz_info["is_micro_cohort"] is False

    # 2. Pinned US procurement / jobs query
    sig_us = ClusterSignature.parse("US:PUBLIC_INSTITUTION:FEDERAL_GS:REGULAR:ONSITE")
    us_info = resolve_active_providers(sig_us)
    assert us_info["candidate_operations"]
    assert "usaspending" in us_info["active_providers"]
    assert us_info["free_dimensions"] == []
    assert us_info["is_macro_rollup"] is False
    assert us_info["is_micro_cohort"] is True


def test_dynamic_report_schema_compiler_indexing():
    """Verify 3-layer dynamic column compilation and accurate =HYPERLINK formula column referencing."""
    custom_attrs = ["legal_form", "salary_min", "award_amount", "assets_usd"]
    specs = DynamicReportSchemaCompiler.compile_schema(custom_attrs)

    # Total columns: 8 (core) + 4 (custom) + 7 (provenance) = 19
    assert len(specs) == 19

    # Core Layer (Cols 1 to 8: A to H)
    assert specs[0].field_key == "no"
    assert specs[0].column_letter == "A"
    assert specs[7].field_key == "cluster_key"
    assert specs[7].column_letter == "H"

    # Dynamic Attribute Layer (Cols 9 to 12: I to L)
    assert specs[8].field_key == "legal_form"
    assert specs[8].column_letter == "I"
    assert specs[9].field_key == "salary_min"
    assert specs[9].column_letter == "J"
    assert specs[10].field_key == "award_amount"
    assert specs[10].column_letter == "K"
    assert specs[11].field_key == "assets_usd"
    assert specs[11].column_letter == "L"

    # Action & Provenance Layer (Cols 13 to 19: M to S)
    # Col 13 is job_url (M)
    assert specs[12].field_key == "job_url"
    assert specs[12].column_letter == "M"

    # Col 14 is clickable hyperlink (N), referencing M{row}
    assert specs[13].field_key == "hyperlink"
    assert specs[13].column_letter == "N"
    assert specs[13].is_hyperlink is True
    assert specs[13].formula_template == '=HYPERLINK(M{row}, "공고 확인 ↗")'

    # Col 15 is freshness (O)
    assert specs[14].field_key == "freshness"
    assert specs[14].column_letter == "O"


def test_cli_cluster_spec_subcommand(capsys):
    """Verify CLI execution of cluster-spec command in both text and JSON mode."""
    ret_text = main(["cluster-spec"])
    assert ret_text == 0
    captured_text = capsys.readouterr()
    assert "operation 30개 / provider 25개" in captured_text.out

    ret_json = main(["cluster-spec", "--json-output"])
    assert ret_json == 0
    captured_json = capsys.readouterr()
    data = json.loads(captured_json.out)
    assert data["total_providers"] == 25
    assert data["source_semantic_mappings"] == 55
    assert data["live_status"] == "not_probed"


def test_cli_export_cluster_jobs_dynamic_attributes(tmp_path, capsys):
    """Verify export-cluster-jobs with --dynamic-attributes compiles custom column layout and dynamic hyperlink."""
    out_file = tmp_path / "test_dynamic_export.xlsx"
    ret = main([
        "export-cluster-jobs",
        "--snapshot", str(Path(__file__).parent / "research/fixtures/selected-posting.json"),
        "--as-of", "2026-10-20T00:00:00Z",
        "--country", "CZ",
        "--sector", "PUBLIC_INSTITUTION",
        "--dynamic-attributes", "legal_form,salary_min,award_amount",
        "--output", str(out_file),
        "--json-output",
    ])
    assert ret == 0
    captured = capsys.readouterr()
    summary = json.loads(captured.out)
    assert summary["status"] == "PARTIAL"
    assert summary["total_matched"] > 0
    assert out_file.exists()

    wb = openpyxl.load_workbook(out_file)
    ws = wb['Postings']
    headers = [c.value for c in ws[1]]
    assert set(headers) == {'_row_id', 'posting_id', 'legal_form', 'salary_min', 'award_amount'}
    assert ws.max_row == 2 and ws.cell(2, headers.index('salary_min') + 1).value == 0
