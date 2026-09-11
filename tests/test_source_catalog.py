import json
from pathlib import Path

from company_intel.config import Settings
from company_intel.connectors import build_probes
from company_intel.connectors.registry import source_health
from company_intel.provider_clusters import ProviderDisposition, classify_operation
from company_intel.source_catalog import evaluate_activation, load_source_catalog, validate_atomic_contract
from company_intel.validation import SemanticFieldCheck


def test_catalog_declares_every_registered_atomic_probe():
    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")
    probes = build_probes(Settings.from_env(root))

    assert len(catalog.operations) == 28
    assert {item.operation_id for item in catalog.operations} == {probe.id for probe in probes}
    assert validate_atomic_contract(catalog, {probe.id for probe in probes}) == []


def test_activation_never_exposes_a_secret_value():
    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")
    keyed = next(item for item in catalog.operations if item.secret_env == "MPM_PUBLIC_EMPLOYMENT_API_KEY")

    health = evaluate_activation(keyed, {"MPM_PUBLIC_EMPLOYMENT_API_KEY": "not-for-output"})

    assert health.status == "ready"
    assert "not-for-output" not in health.detail


def test_sec_placeholder_and_context_sources_are_not_false_green():
    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")
    sec = catalog.by_id("sec_submissions_apple")
    alio = catalog.by_id("alioplus_facility")

    assert evaluate_activation(sec, {"SEC_USER_AGENT": "company-intelligence your-real-email@example.com"}).status == "waiting-configuration"
    assert evaluate_activation(alio, {"ALIO_PLUS_FACILITY_API_KEY": "configured"}).status == "ready-with-http-boundary"


def test_semantic_field_check_rejects_empty_values():
    assert SemanticFieldCheck.present(0) is True
    assert SemanticFieldCheck.present(None) is False
    assert SemanticFieldCheck.present([]) is False


def test_provider_cluster_keeps_context_and_proxy_out_of_production():
    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")
    assert classify_operation(catalog.by_id("alioplus_facility")).disposition == ProviderDisposition.CONTEXT_ONLY
    assert classify_operation(catalog.by_id("github_microsoft")).disposition == ProviderDisposition.PROXY_ONLY
    assert classify_operation(catalog.by_id("greenhouse_airtable")).disposition == ProviderDisposition.METADATA_ONLY
    assert classify_operation(catalog.by_id("alioplus_organization")).disposition == ProviderDisposition.CONTEXT_ONLY
    assert classify_operation(catalog.by_id("imf_czech_growth")).disposition == ProviderDisposition.REJECTED


def test_provider_status_keeps_catalog_activation_and_live_probe_result_distinct(tmp_path):
    root = Path(__file__).resolve().parents[1]
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "validation_results.json").write_text(
        json.dumps(
            {"results": [{"id": "bea_dataset_catalog", "status": "provider_error", "http_status": 200, "provider_error": "inactive key", "collected_at": "2026-09-11T00:00:00Z"}]}
        ),
        encoding="utf-8",
    )

    health = source_health(Settings(root, artifact_dir, f"duckdb:///{tmp_path / 'warehouse.duckdb'}", "test@example.com"))

    assert health["bea_dataset_catalog"]["activation"] == "ready"
    assert health["bea_dataset_catalog"]["last_probe"] == {
        "status": "provider_error",
        "http_status": 200,
        "collected_at": "2026-09-11T00:00:00Z",
        "detail": "inactive key",
    }
