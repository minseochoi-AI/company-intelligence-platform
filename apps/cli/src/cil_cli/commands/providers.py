"""Canonical responsibility owner; migrated from src/company_intel/cli.py."""

from __future__ import annotations
from cil_application.providers.capabilities import BASELINE_API_CATALOG
from cil_application.providers.capabilities import get_cluster_baseline_spec_text
from cil_application.providers.capabilities import resolve_active_providers
from cil_contracts.jobs import CanonicalJobRecord
from cil_contracts.reports import DynamicColumnSpec
from cil_domain.clusters.signature import ClusterSignature
from cil_integrations.providers.job_records import from_cz_mpsv_job_record
from cil_integrations.providers.job_records import from_kr_public_job_record
from cil_integrations.providers.job_records import from_sk_upsvar_record
from cil_integrations.providers.job_schema import JobSchemaContract
from cil_reporting.schema.compiler import DynamicReportSchemaCompiler
from pathlib import Path
from typing import Any, ClassVar
import csv
import json


def _list_api_attributes(source: str, json_output: bool, project_root: Path) -> int:
    source_key = source.lower().replace("-", "_")
    provider_info = {
        "cz_mpsv": {
            "name": "Czech MPSV Job Vacancy Open Data API",
            "provider_key": "CZ_MPSV",
            "sample_path": project_root
            / "artifacts/public-sector-inventory-2026-09-16/czech_current_jobs.csv",
            "notes": "Direct MFCR/MPSV vacancy register with 2,938 vacancies. Contains portal_id, job_url, etc.",
        },
        "kr_alio": {
            "name": "Korean Public Job-ALIO Recruitment Open API",
            "provider_key": "JOB_ALIO",
            "sample_path": project_root
            / "artifacts/public-sector-inventory-2026-09-16/korea_current_jobs.csv",
            "notes": "Ministry of Economy & Finance official public institution job board (423+ entries).",
        },
        "sk_upsvar": {
            "name": "Slovak Central Labour Office ÚPSVaR Open Data API",
            "provider_key": "SK_UPSVAR",
            "sample_path": None,
            "sample_data": {
                "id": "SK-UPSVAR-2026-001",
                "employer": "Železnice Slovenskej republiky (ŽSR)",
                "ico": "31364501",
                "legal_form": "Štátny podnik",
                "entity_type": "국영 철도공기업",
                "title": "Správca IT infraštruktúry a počítačových sietí",
                "isco": "25220",
                "edu": "bakal",
                "sal_min": 1600,
                "sal_max": 2200,
                "curr": "EUR",
                "loc": "Bratislava (SK010)",
                "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-001",
                "desc": "Železničná IT infraštruktúra, správa LAN/WAN sietí a serverov v centre Bratislavy.",
                "closing_at": "2026-11-30",
            },
            "notes": "Official open data vacancy schema from sluzbyzamestnanosti.gov.sk.",
        },
        "us_usajobs": {
            "name": "US Office of Personnel Management USAJOBS Search API",
            "provider_key": "US_USAJOBS",
            "sample_path": None,
            "sample_data": {
                "PositionID": "USA-78910",
                "PositionURI": "https://www.usajobs.gov/job/78910",
                "OrganizationName": "Department of Energy",
                "PositionTitle": "IT Cybersecurity Specialist (INFOSEC)",
                "PositionOfferingType": "Permanent",
                "PositionRemuneration": [
                    {"MinimumRange": 95000, "MaximumRange": 145000}
                ],
                "JobCode": "2210",
                "EducationRequirement": "bachelor",
                "ApplicationCloseDate": "2026-12-15",
                "PositionLocationDisplay": "Washington, DC",
                "UserArea": {
                    "Details": {
                        "JobSummary": "Cybersecurity operations and network defenses."
                    }
                },
            },
            "notes": "Federal OPM REST API for civil service opportunities.",
        },
        "kr_worknet": {
            "name": "Korean MOEL WorkNet Employment Open API",
            "provider_key": "KR_WORKNET",
            "sample_path": None,
            "sample_data": {
                "wantedAuthNo": "K120112609010001",
                "company": "에스케이텔레콤(주)",
                "title": "클라우드 인프라 아키텍트 경력 채용",
                "wantedInfoUrl": "https://www.work.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?wantedAuthNo=K120112609010001",
                "coClcd": "01",
                "empType": "10",
                "salTpNm": "연봉 60,000,000원 이상",
                "closeDt": "2026-11-20",
            },
            "notes": "WorkNet Open API for private sector enterprises and large conglomerates.",
        },
    }
    if source_key not in provider_info:
        valid_keys = ", ".join(provider_info.keys())
        print(
            f"오류: 지원되지 않는 API 원천입니다: '{source}'. 지원 원천: {valid_keys}"
        )
        return 1
    info = provider_info[source_key]
    raw_sample: dict[str, Any] = {}
    if info.get("sample_path") and info["sample_path"].exists():
        with open(info["sample_path"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw_sample = next(reader, {})
    elif info.get("sample_data"):
        raw_sample = dict(info["sample_data"])
    canonical_mappings = {}
    for canon_field, aliases in JobSchemaContract.REQUIRED_CANONICAL_FIELDS.items():
        for alias in aliases:
            canonical_mappings[alias] = canon_field
    attributes_meta = []
    for k, v in raw_sample.items():
        mapped = canonical_mappings.get(k, "-")
        val_str = str(v)
        val_display = val_str[:40] + "..." if len(val_str) > 40 else val_str
        attributes_meta.append(
            {
                "attribute_name": k,
                "mapped_canonical": mapped,
                "data_type": type(v).__name__,
                "sample_value": v,
                "display_value": val_display,
            }
        )
    payload = {
        "source": source_key,
        "name": info["name"],
        "provider_contract": info["provider_key"],
        "attributes_count": len(attributes_meta),
        "attributes": attributes_meta,
        "notes": info["notes"],
        "source_kind": "historical_sample" if info.get("sample_path") else "fixture",
        "coverage": "sample_only_not_all_provider_fields",
    }
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print("=" * 80)
    print(f"  API 원천 속성 메타데이터 감사: {info['name']}")
    print(
        f"  제공자 키: {info['provider_key']} | 총 반환 속성 수: {len(attributes_meta)}개"
    )
    print("=" * 80)
    print(
        f"{'속성 명칭 (Raw Key)':<28} | {'정규화 매핑 (Canonical)':<22} | {'타입':<8} | {'샘플 값 (Sample)'}"
    )
    print("-" * 80)
    for a in attributes_meta:
        print(
            f"{a['attribute_name']:<28} | {a['mapped_canonical']:<22} | {a['data_type']:<8} | {a['sample_value']}"
        )
    print("=" * 80)
    print(f"참고: {info['notes']}")
    return 0


def _cluster_spec(json_output: bool = False) -> int:
    get_cluster_baseline_spec_text()
    if json_output:
        print(json.dumps(BASELINE_API_CATALOG, ensure_ascii=False, indent=2))
        return 0
    print(get_cluster_baseline_spec_text())
    return 0
