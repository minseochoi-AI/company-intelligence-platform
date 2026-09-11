from datetime import UTC, datetime

from company_intel.exporting import build_export_bundle


def test_export_keeps_evidence_and_exclusion_rows_and_sanitizes_cells(tmp_path):
    bundle = build_export_bundle(
        tmp_path,
        companies=[{"company_id": "US:1", "legal_name": "=unsafe", "country_code": "US"}],
        capabilities=[{"company_id": "US:1", "capability": "financial", "status": "available"}],
        jobs=[],
        requirements=[],
        sources=[{"source_id": "SEC", "source_url": "https://data.sec.gov/example"}],
        exclusions=[{"company_id": "US:1", "reason": "requirement_unavailable"}],
    )

    assert bundle.manifest["format_version"] == "1"
    assert "companies.csv" in bundle.files
    assert bundle.files["companies.csv"].startswith(b"company_id,legal_name,country_code")
    assert b"'=unsafe" in bundle.files["companies.csv"]
    assert "exclusions.csv" in bundle.files


def test_export_separates_unverifiable_and_conflicting_evidence(tmp_path):
    bundle = build_export_bundle(
        tmp_path, companies=[], capabilities=[], jobs=[], requirements=[], sources=[], exclusions=[],
        unverifiable=[{"subject_type": "job", "subject_id": "1", "field": "salary", "reason": "salary_unverifiable"}],
        conflicts=[{"subject_type": "company", "subject_id": "A", "field": "identity", "reason": "identity_conflict"}],
        include_xlsx=False,
    )
    assert "unverifiable.csv" in bundle.files
    assert "conflicts.csv" in bundle.files
    assert bundle.manifest["lineage"].startswith("Each row")


def test_export_serializes_duckdb_style_datetime_values_to_iso8601(tmp_path):
    collected_at = datetime(2026, 9, 11, 14, 2, tzinfo=UTC)
    bundle = build_export_bundle(
        tmp_path,
        companies=[],
        capabilities=[
            {
                "company_id": "DART:00126380",
                "operation_id": "opendart_samsung_financials",
                "capability": "financial",
                "status": "available",
                "available_at": collected_at,
            }
        ],
        jobs=[],
        requirements=[],
        sources=[],
        exclusions=[],
        include_xlsx=False,
    )

    assert b"2026-09-11T14:02:00+00:00" in bundle.files["capabilities.csv"]
