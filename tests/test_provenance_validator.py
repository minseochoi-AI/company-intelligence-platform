"""Physical provenance integration test suite for master occupational lattice Excel.

Directly validates physical joins against disk artifacts, DuckDB tables, and
official taxonomy registries without any mock fixtures or synthetic test stubs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from company_intel.cli import main
from company_intel.provenance_validator import ExcelProvenanceValidator


@pytest.fixture(scope="module")
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def master_excel_path(project_root: Path) -> Path:
    p = project_root / "company-intelligence-occupational-lattice-master.xlsx"
    assert p.exists(), f"Physical master workbook not found at {p}"
    return p


def test_physical_provenance_validator_all_matrices_pass(project_root: Path, master_excel_path: Path) -> None:
    """Verify that all 10 matrices across 10 sheets achieve 100% physical provenance match."""
    validator = ExcelProvenanceValidator(
        excel_path=master_excel_path,
        project_root=project_root,
    )
    report = validator.verify_all_matrices()

    assert report.total_matrices_checked == 10
    assert report.failed_matrices == 0
    assert report.passed_matrices == 10
    assert report.overall_match_rate_pct == 100.0
    assert report.total_rows_audited >= 2800
    assert report.total_rows_verified == report.total_rows_audited


def test_sheet_01_master_taxonomy_physical_join(project_root: Path, master_excel_path: Path) -> None:
    """Verify Sheet 01 physical join with ILO ISCO-08 structure definitions XLSX."""
    validator = ExcelProvenanceValidator(
        excel_path=master_excel_path,
        project_root=project_root,
    )
    validator.load_authoritative_sources()

    import openpyxl
    wb = openpyxl.load_workbook(master_excel_path, data_only=True)
    res = validator.verify_sheet_01_master_taxonomy(wb)
    wb.close()

    assert res.status == "PASS"
    assert res.row_count == 436
    assert res.matched_count == 436
    assert res.match_rate_pct == 100.0
    assert res.evidence_sha256 is not None
    assert Path(res.physical_evidence_path).exists()


def test_sheet_02_career_lattice_dag_physical_join(project_root: Path, master_excel_path: Path) -> None:
    """Verify Sheet 02 1,341 DAG edges connecting valid ILO Level 4 Unit Groups."""
    validator = ExcelProvenanceValidator(
        excel_path=master_excel_path,
        project_root=project_root,
    )
    validator.load_authoritative_sources()

    import openpyxl
    wb = openpyxl.load_workbook(master_excel_path, data_only=True)
    res = validator.verify_sheet_02_career_lattice_dag(wb)
    wb.close()

    assert res.status == "PASS"
    assert res.row_count == 1341
    assert res.matched_count == 1341
    assert res.match_rate_pct == 100.0


def test_sheet_04_market_dynamics_ai_exposure_physical_tasks_join(project_root: Path, master_excel_path: Path) -> None:
    """Verify Sheet 04 AI exposure ratings against 14,489 physical atomic tasks CSV."""
    validator = ExcelProvenanceValidator(
        excel_path=master_excel_path,
        project_root=project_root,
    )
    validator.load_authoritative_sources()

    import openpyxl
    wb = openpyxl.load_workbook(master_excel_path, data_only=True)
    res = validator.verify_sheet_04_market_dynamics_roi(wb)
    wb.close()

    assert res.status == "PASS"
    assert res.row_count == 436
    assert res.matched_count == 436
    assert res.match_rate_pct == 100.0


def test_sheet_07_time_series_warehouse_duckdb_and_raw_payload_join(project_root: Path, master_excel_path: Path) -> None:
    """Verify Sheet 07 joins with physical DuckDB warehouse tables and raw API artifacts."""
    validator = ExcelProvenanceValidator(
        excel_path=master_excel_path,
        project_root=project_root,
    )
    validator.load_authoritative_sources()

    import openpyxl
    wb = openpyxl.load_workbook(master_excel_path, data_only=True)
    res, samples = validator.verify_sheet_07_time_series_warehouse(wb)
    wb.close()

    assert res.status == "PASS"
    assert res.row_count == 73
    assert res.matched_count == 73
    assert res.match_rate_pct == 100.0
    assert len(samples) > 0
    for sample in samples:
        assert sample.join_verified is True
        assert sample.reported_value is not None
        assert sample.source_api in ("OpenDART", "SEC EDGAR", "ARES/MFCR", "워크넷", "Greenhouse/Lever", "MPSV", "PblJobService", "ECOS", "FRED", "CNB")


def test_cli_verify_excel_provenance_command(project_root: Path, master_excel_path: Path) -> None:
    """Verify that CLI verify-excel-provenance command runs end-to-end and returns exit code 0."""
    report_target = project_root / "artifacts" / "test_cli_provenance_report.md"
    try:
        code = main([
            "verify-excel-provenance",
            "--excel-path",
            str(master_excel_path),
            "--report-path",
            str(report_target),
            "--strict",
        ])
        assert code == 0
        assert report_target.exists()
        content = report_target.read_text(encoding="utf-8")
        assert "엑셀 출력 행렬 전수 물리적 정본 검증 보고서" in content
        assert "10개 (100% PASS)" in content
        assert "100.0%" in content
    finally:
        if report_target.exists():
            report_target.unlink()


def test_cli_korean_alias_provenance_command(project_root: Path, master_excel_path: Path) -> None:
    """Verify that Korean alias 엑셀-정본-검증 executes identically."""
    code = main([
        "엑셀-정본-검증",
        "--excel-path",
        str(master_excel_path),
        "--strict",
    ])
    assert code == 0
