from pathlib import Path

from company_intel.config import Settings
from company_intel.models import SearchProfile
from company_intel.search import rank_candidates
from company_intel.warehouse import Warehouse


def test_open_dart_source_identifier_makes_ingested_entity_searchable(tmp_path):
    root = Path(__file__).resolve().parents[1]
    settings = Settings(
        project_root=root,
        artifact_dir=tmp_path / "artifacts",
        database_url=f"duckdb:///{tmp_path / 'company-intelligence.duckdb'}",
        sec_user_agent="test@example.com",
    )
    warehouse = Warehouse(settings)
    warehouse.initialize()
    warehouse.ingest_normalized_artifacts()

    candidates = warehouse.search_candidates(("KR",))
    assert candidates == [
        {
            "entity_id": "DART:00126380",
            "country_code": "KR",
            "industry_code": None,
            "name": "삼성전자",
            "capabilities": {},
            "evidence_urls": [],
            "identity_status": "resolved",
        }
    ]
    matches = rank_candidates(SearchProfile(countries=("KR",), job_keywords=("삼성",)), candidates)
    assert matches[0].status == "matched"
