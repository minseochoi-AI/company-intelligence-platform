from datetime import UTC, datetime

from company_intel.exporting import build_export_bundle
from company_intel.run_manifest import build_run_manifest


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


def test_verdict_and_lineage_export_keeps_tables_and_redacts_sensitive_values(tmp_path):
    secret = "do-not-export"
    run_manifest = build_run_manifest(
        "job-search",
        {"countries": ["US"], "api_key": secret},
        [{"semantic_field": "country_code", "provider": "lever", "raw_field": "country"}],
        [{"provider": "lever", "source_url": f"https://example.test/jobs?access_token={secret}"}],
        {"strict": 1, "no_match": 1, "unverifiable": 0, "conflict": 0},
        {"jobs.csv": b"job_id,title\n1,Engineer\n"},
        generated_at="2026-09-13T00:00:00+00:00",
    )
    bundle = build_export_bundle(
        tmp_path,
        companies=[],
        capabilities=[],
        jobs=[],
        requirements=[],
        sources=[],
        exclusions=[],
        strict_matches=[
            {
                "subject_type": "job",
                "subject_id": "1",
                "match_status": "strict",
                "source_url": f"https://example.test/job?api_key={secret}",
            }
        ],
        no_matches=[{"subject_type": "job", "subject_id": "2", "reason": "country_no_match"}],
        facets=[
            {
                "semantic_field": "country_code",
                "scope": "job",
                "normalized_value": "US",
                "display_label": "United States",
                "vocabulary_namespace": "ISO-3166-1",
                "provider": "lever",
                "raw_field": "country",
                "record_count": 1,
                "coverage_ratio": 1.0,
                "filterability": "filter_and_sort",
                "sortability": "supported",
                "comparability_requirements": "same_scope",
                "evidence_status": "observed",
            }
        ],
        run_manifest=run_manifest,
        metadata={"access_token": secret},
        include_xlsx=False,
    )

    assert {
        "locations.csv",
        "strict_matches.csv",
        "no_matches.csv",
        "unverifiable_candidates.csv",
        "facets.csv",
        "run_manifest.csv",
        "run_manifest.json",
    } <= set(bundle.files)
    assert bundle.manifest["metadata"]["run_id"] == run_manifest["run_id"]
    assert secret.encode() not in bundle.files["run_manifest.json"]
    assert secret.encode() not in bundle.files["manifest.json"]
    assert secret.encode() not in bundle.files["strict_matches.csv"]
