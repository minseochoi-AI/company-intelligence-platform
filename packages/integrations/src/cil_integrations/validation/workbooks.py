"""Canonical responsibility owner; migrated from src/company_intel/provenance_validator.py."""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import csv
import hashlib
import json
import logging
import openpyxl
import re

logger = logging.getLogger(__name__)


@dataclass
class MatrixProvenanceResult:
    """Audit record for a single matrix or table within a workbook sheet."""

    sheet_name: str
    matrix_title: str
    cell_range: str
    row_count: int
    matched_count: int
    match_rate_pct: float
    provenance_type: str
    authoritative_source: str
    physical_evidence_path: str
    evidence_sha256: str | None
    status: str
    audit_notes: list[str] = field(default_factory=list)


@dataclass
class RowProvenanceRecord:
    """Granular provenance record for an individual row."""

    sheet_name: str
    row_number: int
    primary_key: str
    entity_or_role: str
    metric_or_title: str
    reported_value: Any
    source_api: str
    physical_origin_ref: str
    join_verified: bool
    verification_note: str


@dataclass
class ComprehensiveProvenanceReport:
    """Overall provenance audit report across all sheets and matrices."""

    workbook_path: str
    workbook_sha256: str
    total_matrices_checked: int
    passed_matrices: int
    failed_matrices: int
    total_rows_audited: int
    total_rows_verified: int
    overall_match_rate_pct: float
    matrix_results: list[MatrixProvenanceResult]
    detailed_audit_samples: list[RowProvenanceRecord]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["unverified_matrices"] = sum(
            m.status == "UNVERIFIED" for m in self.matrix_results
        )
        result["status"] = (
            "VERIFIED_ARTIFACT_BINDING"
            if self.matrix_results
            and self.passed_matrices == self.total_matrices_checked
            else "UNVERIFIED"
        )
        return result


class ExcelProvenanceValidator:
    """Verify a sealed artifact binding; unbound workbooks remain UNVERIFIED.

    A matching manifest proves byte lineage, not real-world source accuracy.
    No default operational database or sibling repository is consulted.
    """

    def __init__(
        self,
        excel_path="company-intelligence-occupational-lattice-master.xlsx",
        project_root=None,
        duckdb_path=None,
        artifacts_dir=None,
        raw_structure_path=None,
        atomic_tasks_path=None,
        market_registry_path=None,
        *,
        sealed_bundle=None,
        manifest_sha256=None,
    ):
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.excel_path = Path(excel_path)
        if not self.excel_path.is_absolute():
            self.excel_path = self.project_root / self.excel_path
        self.sealed_bundle = Path(sealed_bundle) if sealed_bundle else None
        self.manifest_sha256 = manifest_sha256

    def verify_all_matrices(self) -> ComprehensiveProvenanceReport:
        data = self.excel_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        verified = False
        note = "No hash-bound source manifest supplied. Cell contents do not establish their own truth."
        if self.sealed_bundle is not None:
            if not self.manifest_sha256:
                raise ValueError("expected manifest hash required")
            from cil_integrations.storage.evidence import ResearchArtifactStore
            from cil_application.research.report_service import verify_sealed_bundle

            manifest = verify_sealed_bundle(
                ResearchArtifactStore(self.sealed_bundle), self.manifest_sha256
            )
            verified = manifest["files"]["research.xlsx"]["sha256"] == digest
            if not verified:
                raise ValueError("workbook does not match sealed manifest")
            note = "Verified sealed workbook bytes and artifact hashes. Source declarations, eligibility and semantic truth require evidence review."
        workbook = openpyxl.load_workbook(
            self.excel_path, read_only=True, data_only=False
        )
        matrices, samples = [], []
        try:
            for sheet in workbook:
                # Header names define fields; no assumed 19/24/30-column layout.
                rows = list(sheet.iter_rows(values_only=True))
                header_index = next(
                    (
                        i
                        for i, row in enumerate(rows[:16])
                        if any(
                            str(c or "").lower()
                            in {"_row_id", "job_id", "posting_id", "isco_08_code"}
                            or "Job ID" in str(c or "")
                            for c in row
                        )
                    ),
                    0,
                )
                headers = [str(c or "") for c in rows[header_index]] if rows else []
                records = [
                    (i + header_index + 2, row)
                    for i, row in enumerate(rows[header_index + 1 :])
                    if any(c is not None for c in row)
                ]
                keys = [
                    i
                    for i, h in enumerate(headers)
                    if h in {"_row_id", "job_id", "posting_id", "ISCO_08_Code"}
                    or "Job ID" in h
                ]
                for row_number, row in records:
                    key = str(row[keys[0]]) if keys else str(row_number)
                    samples.append(
                        RowProvenanceRecord(
                            sheet.title,
                            row_number,
                            key,
                            "",
                            "",
                            list(row),
                            "sealed_saved_bundle" if verified else "unknown",
                            str(self.sealed_bundle or ""),
                            verified,
                            note,
                        )
                    )
                count = len(records)
                matrices.append(
                    MatrixProvenanceResult(
                        sheet.title,
                        "Full data rows",
                        sheet.calculate_dimension(force=True),
                        count,
                        count if verified else 0,
                        100.0 if verified else 0.0,
                        "sealed_artifact_binding" if verified else "unbound",
                        str(self.sealed_bundle or "not_supplied"),
                        str(self.sealed_bundle or ""),
                        self.manifest_sha256,
                        "PASS" if verified else "UNVERIFIED",
                        [note],
                    )
                )
        finally:
            workbook.close()
        total = sum(m.row_count for m in matrices)
        return ComprehensiveProvenanceReport(
            str(self.excel_path),
            digest,
            len(matrices),
            len(matrices) if verified else 0,
            0,
            total,
            total if verified else 0,
            100.0 if verified else 0.0,
            matrices,
            samples,
        )

    def load_authoritative_sources(self) -> None:
        """Legacy method: explicit sealed binding is checked during verification."""
        return None

    def generate_markdown_report(self, report=None) -> str:
        report = report or self.verify_all_matrices()
        lines = [
            "# 엑셀 출력 행렬 전수 물리적 정본 검증 보고서",
            "",
            "검증 범위: 봉인된 파일 바이트와 manifest 연결. 원천의 현실 정확성은 별도 내용 검토 대상.",
            "상태: " + report.to_dict()["status"],
            f"검사 행렬 {report.total_matrices_checked}개 / 연결 검증 통과 {report.passed_matrices}개 / 미검증 {report.to_dict()['unverified_matrices']}개",
            f"전체 검사 행 {report.total_rows_audited}개 / 해시 연결 확인 행 {report.total_rows_verified}개",
            "",
            "| 시트 | 행 | 상태 | 근거 |",
            "|---|---:|---|---|",
        ]
        lines.extend(
            f"| {m.sheet_name} | {m.row_count} | {m.status} | {m.authoritative_source} |"
            for m in report.matrix_results
        )
        return "\n".join(lines) + "\n"

    def _sheet_result(self, name):
        report = self.verify_all_matrices()
        return next(m for m in report.matrix_results if m.sheet_name == name)

    def verify_sheet_00_navigator(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("00_Navigator")

    def verify_sheet_01_master_taxonomy(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("01_Master_Taxonomy")

    def verify_sheet_02_career_lattice_dag(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("02_Career_Lattice_DAG")

    def verify_sheet_03_consultant_value_chain(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("03_Consultant_ValueChain")

    def verify_sheet_04_market_dynamics_roi(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("04_Market_Dynamics_ROI")

    def verify_sheet_05_venture_b2b_saas(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("05_Venture_B2BSaaS")

    def verify_sheet_06_data_dictionary(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("06_Data_Dictionary")

    def verify_sheet_07_time_series_warehouse(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        report = self.verify_all_matrices()
        return next(
            m
            for m in report.matrix_results
            if m.sheet_name == "07_Time_Series_Warehouse"
        ), [
            r
            for r in report.detailed_audit_samples
            if r.sheet_name == "07_Time_Series_Warehouse"
        ]

    def verify_sheet_08_temporal_comparative(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("08_Temporal_Comparative_Table")

    def verify_sheet_09_cross_elasticity_trends(self, wb=None):
        """Compatibility view of this validator's bound workbook, never an arbitrary supplied workbook."""
        return self._sheet_result("09_Cross_Elasticity_Trends")


class PublicSectorJobProvenanceValidator:
    """Compatibility batch adapter; workbook paths are explicit instance inputs."""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root or Path.cwd())

    def _compute_sha256(self, path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def audit_all_workbooks(self, workbooks=None, *, sealed_bindings=None):
        if not workbooks:
            raise ValueError("explicit workbook paths required")
        result = {}
        for selected in workbooks:
            path = Path(selected)
            if not path.is_absolute():
                path = self.project_root / path
            binding = (sealed_bindings or {}).get(str(selected), {})
            result[str(selected)] = ExcelProvenanceValidator(
                path, **binding
            ).verify_all_matrices()
        return result
