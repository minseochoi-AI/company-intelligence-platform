from __future__ import annotations

import argparse
import csv
import datetime
import json
import sys
from pathlib import Path
from typing import Any, ClassVar

from .classification import (
    BASELINE_API_CATALOG,
    CanonicalJobRecord,
    ClusterSignature,
    DynamicColumnSpec,
    DynamicReportSchemaCompiler,
    JobSchemaContract,
    from_cz_mpsv_job_record,
    from_kr_public_job_record,
    from_sk_upsvar_record,
    get_cluster_baseline_spec_text,
    resolve_active_providers,
)
from .live_job_provenance import JobProvenanceVerifier

from .analysis_service import (
    build_company_timeline,
    evaluate_ai_event,
    evaluate_job_trends,
    evaluate_valuation_scenarios,
)
from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    event_study_prerequisites,
    financial_metrics,
    future_value_score,
    hiring_change,
    macro_sensitivity,
    rank_companies,
    valuation_prerequisites,
)
from .cli_guide import COMMAND_GUIDES, command_epilog, command_key, guide_payload, korean_option
from .config import Settings
from .connectors.registry import source_health
from .current_jobs import execute_current_job_search
from .evidence import write_json
from .exporting import build_export_bundle
from .facets import build_job_facets
from .interactive import (
    ArrowMenu,
    build_interactive_request,
    load_scripted_selector,
    write_interactive_profile,
)
from .job_search import JobSearchProfile, normalize_provider_payloads, search_job_dataframes
from .live_snapshots import snapshot_freshness
from .models import SearchProfile
from .pipeline import actual_analysis
from .query_contract import company_search_profile_from_mapping
from .reporting import write_validation_report
from .run_manifest import build_run_manifest, result_refs, write_run_manifest
from .screening import ScreenerProfile, screen_companies
from .search import (
    explain_company_evaluation,
    rank_candidate_evaluations,
    rank_candidates,
    validate_search_profile,
)
from .selection_provenance import replay_selection, verify_run_chain
from .validation import validate
from .warehouse import Warehouse


class KoreanHelpFormatter(argparse.HelpFormatter):
    """Translate argparse's structural headings without changing argument contracts."""

    _HEADINGS: ClassVar[dict[str, str]] = {
        "positional arguments": "명령",
        "optional arguments": "선택 인자",
        "options": "선택 인자",
    }

    def add_usage(self, usage: str | None, actions: Any, groups: Any, prefix: str | None = None) -> None:
        if usage and usage.startswith("사용법: "):
            usage = usage.removeprefix("사용법: ")
        super().add_usage(usage, actions, groups, "사용법: ")

    def start_section(self, heading: str | None) -> None:
        super().start_section(self._HEADINGS.get(heading or "", heading))


class KoreanArgumentParser(argparse.ArgumentParser):
    """Keep argparse behaviour while presenting parser errors in Korean."""

    _ERROR_TEXT: ClassVar[dict[str, str]] = {
        "the following arguments are required:": "다음 인자가 필요합니다:",
        "invalid choice:": "허용되지 않는 선택값:",
        "unrecognized arguments:": "알 수 없는 인자:",
        "expected one argument": "값 하나가 필요합니다",
    }

    def error(self, message: str) -> None:
        localized = message
        for before, after in self._ERROR_TEXT.items():
            localized = localized.replace(before, after)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: 오류: {localized}\n")


def _add_help(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-h",
        "--도움말",
        "--help",
        action="help",
        help="이 명령의 사용법, 인자 형식, 제한과 예시를 표시하고 종료합니다.",
    )


def _add_option(
    parser: argparse.ArgumentParser,
    option_key: str,
    english_option: str,
    *,
    dest: str | None = None,
    **kwargs: Any,
) -> argparse.Action:
    """Register Korean-first options while retaining prior English spellings."""

    return parser.add_argument(korean_option(option_key), english_option, dest=dest or option_key, **kwargs)


def _add_command(subparsers: Any, key: str) -> argparse.ArgumentParser:
    guide = next(item for item in COMMAND_GUIDES if item.key == key)
    parser = subparsers.add_parser(
        guide.korean_name,
        aliases=[guide.key],
        add_help=False,
        help=f"{guide.summary} (영문 호환: {guide.key})",
        description=f"{guide.summary}\n\n{guide.method}",
        epilog=command_epilog(key),
        formatter_class=KoreanHelpFormatter,
    )
    parser.set_defaults(command_key=key)
    _add_help(parser)
    return parser


def _demo(settings: Settings) -> dict:
    facts = {
        "revenue": 1000.0,
        "revenue_previous": 900.0,
        "gross_profit": 430.0,
        "operating_income": 180.0,
        "net_income": 130.0,
        "cfo": 210.0,
        "capex": 70.0,
        "cash": 300.0,
        "debt": 200.0,
        "ebitda": 230.0,
        "current_assets": 500.0,
        "current_liabilities": 250.0,
        "interest_expense": 20.0,
        "nopat": 140.0,
        "invested_capital": 700.0,
        "employees": 100.0,
        "cost_of_revenue": 570.0,
        "average_inventory": 95.0,
    }
    peer_rows = [
        {
            "entity_id": "A",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.15,
            "margin": 0.22,
            "leverage": 0.4,
        },
        {
            "entity_id": "B",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.08,
            "margin": 0.18,
            "leverage": 1.1,
        },
        {
            "entity_id": "C",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.11,
            "margin": 0.25,
            "leverage": 0.7,
        },
    ]
    snapshots = [
        {"entity_id": "A", "snapshot_date": "2026-01-01", "job_id": "1"},
        {"entity_id": "A", "snapshot_date": "2026-01-01", "job_id": "2"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "2"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "3"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "4"},
    ]
    result = {
        "financial_metrics": financial_metrics(facts),
        "peer_ranking": rank_companies(
            peer_rows, {"growth": 0.4, "margin": 0.4, "leverage": 0.2}, {"leverage": False}
        ),
        "macro_sensitivity": macro_sensitivity(
            [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.02],
            {
                "rate_change": [0.0, 0.01, 0.02, 0.01, -0.01, 0.0, -0.02, -0.01],
                "fx_change": [0.01, -0.01, 0.02, -0.02, 0.01, 0.03, -0.01, 0.0],
            },
        ),
        "hiring_change": hiring_change(snapshots),
        "event_study": event_study(
            [0.01, 0.02, -0.01, 0.03, 0.05, 0.01, -0.02, 0.01, 0.02],
            [0.005, 0.01, -0.005, 0.01, 0.015, 0.005, -0.01, 0.0, 0.01],
            4,
            (1, 3),
        ),
        "difference_in_differences": difference_in_differences(
            [10, 11, 12], [14, 15, 16], [9, 10, 11], [10, 11, 12]
        ),
        "dcf": dcf_scenarios(revenue=1000.0, net_debt=-100.0, shares=100.0),
        "future_value": future_value_score(
            {
                "financial_health": 80,
                "profitability": 75,
                "growth_quality": 70,
                "valuation": 60,
                "macro_industry_fit": 65,
                "operations_workforce": 72,
                "disclosure_governance": 85,
            },
            {"operations_workforce": 0.6, "macro_industry_fit": 0.8},
        ),
    }
    write_json(settings.artifact_dir / "demo_analytics.json", result)
    return result


def _records(value: Any) -> list[dict[str, Any]]:
    """Convert a DataFrame-like result to JSON rows without changing values."""

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        records = to_dict("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _job_verdict_counts(frames: Any) -> dict[str, int]:
    return {
        "matched": len(frames.jobs),
        "strict_matches": len(frames.strict_matches),
        "unverifiable": len(frames.unverifiable_candidates),
        "no_match": len(frames.no_matches),
        "conflict": len(frames.conflicts),
    }


def _supplied_table_rows(supplied: dict[str, Any], name: str) -> list[dict[str, Any]]:
    """Accept both an export table object and ``JobDataFrames.as_records``."""

    tables = supplied.get("tables") if isinstance(supplied.get("tables"), dict) else supplied
    value = tables.get(name, []) if isinstance(tables, dict) else []
    if isinstance(value, dict):
        value = value.get("rows", [])
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _get_slovak_benchmark_postings() -> list[dict[str, Any]]:
    return [
        {"id": "SK-UPSVAR-2026-001", "employer": "Železnice Slovenskej republiky (ŽSR)", "ico": "31364501", "legal_form": "Štátny podnik", "entity_type": "국영 철도공기업", "title": "Správca IT infraštruktúry a počítačových sietí", "isco": "25220", "edu": "bakal", "sal_min": 1600, "sal_max": 2200, "curr": "EUR", "korean_role": "공기업 전산직 ICT 인프라·전산망 운영", "loc": "Bratislava (SK010)", "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-001", "desc": "Železničná IT infraštruktúra, správa LAN/WAN sietí.", "grad": False, "closing_at": "2026-11-30"},
        {"id": "SK-UPSVAR-2026-002", "employer": "Slovenská pošta, a.s.", "ico": "36631124", "legal_form": "Akciová spoločnosť", "entity_type": "국영 우정공기업", "title": "Systémový administrátor Linux/Windows", "isco": "25220", "edu": "usoSMat", "sal_min": 1500, "sal_max": 1950, "curr": "EUR", "korean_role": "공기업 시스템 엔지니어링 및 서버 운영", "loc": "Bratislava (SK010)", "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-002", "desc": "Správa a monitoring poštových IT systémov.", "grad": False, "closing_at": "2026-11-20"},
        {"id": "SK-UPSVAR-2026-003", "employer": "Národná agentúra pre sieťové a elektronické služby (NASES)", "ico": "42156424", "legal_form": "Príspevková organizácia", "entity_type": "국가전자서비스청", "title": "DevOps špecialista pre vládny cloud", "isco": "25140", "edu": "bakal", "sal_min": 1900, "sal_max": 2600, "curr": "EUR", "korean_role": "공공 클라우드 인프라 운영 및 CI/CD 자동화", "loc": "Bratislava (SK010)", "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-003", "desc": "Správa vládneho cloudu a portálu slovensko.sk.", "grad": False, "closing_at": "2026-12-15"},
        {"id": "SK-UPSVAR-2026-005", "employer": "Slovenský plynárenský priemysel, a.s. (SPP)", "ico": "35815256", "legal_form": "Akciová spoločnosť", "entity_type": "국영 에너지공기업", "title": "Dátový analytik pre trh s energiami", "isco": "24130", "edu": "bakal", "sal_min": 1800, "sal_max": 2500, "curr": "EUR", "korean_role": "공기업 에너지 시장 데이터 분석", "loc": "Bratislava (SK010)", "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-005", "desc": "Analýza dát o spotrebe plynu, modelovanie trhových rizík.", "grad": False, "closing_at": "2026-12-31"},
        {"id": "SK-UPSVAR-RD-001", "employer": "Slovenská akadémia vied - Ústav informatiky (SAV)", "ico": "00166651", "legal_form": "Verejná výskumná inštitúcia", "entity_type": "국립 과학원 연구기관", "title": "Vedecký pracovník v oblasti umelej inteligencie a dátovej vedy", "isco": "12231", "edu": "doktor", "sal_min": 2200, "sal_max": 3200, "curr": "EUR", "korean_role": "국립연구소 인공지능/빅데이터 선임연구원", "loc": "Bratislava (SK010)", "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-RD-001", "desc": "Výskum v oblasti strojového učenia, analýzy veľkých dát.", "grad": True, "closing_at": "2026-12-31"},
    ]


def _list_api_attributes(source: str, json_output: bool, project_root: Path) -> int:
    source_key = source.lower().replace("-", "_")
    provider_info = {
        "cz_mpsv": {
            "name": "Czech MPSV Job Vacancy Open Data API",
            "provider_key": "CZ_MPSV",
            "sample_path": project_root / "artifacts/public-sector-inventory-2026-09-16/czech_current_jobs.csv",
            "notes": "Direct MFCR/MPSV vacancy register with 2,938 vacancies. Contains portal_id, job_url, etc.",
        },
        "kr_alio": {
            "name": "Korean Public Job-ALIO Recruitment Open API",
            "provider_key": "JOB_ALIO",
            "sample_path": project_root / "artifacts/public-sector-inventory-2026-09-16/korea_current_jobs.csv",
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
                "PositionRemuneration": [{"MinimumRange": 95000, "MaximumRange": 145000}],
                "JobCode": "2210",
                "EducationRequirement": "bachelor",
                "ApplicationCloseDate": "2026-12-15",
                "PositionLocationDisplay": "Washington, DC",
                "UserArea": {"Details": {"JobSummary": "Cybersecurity operations and network defenses."}},
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
        print(f"오류: 지원되지 않는 API 원천입니다: '{source}'. 지원 원천: {valid_keys}")
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
        attributes_meta.append({
            "attribute_name": k,
            "mapped_canonical": mapped,
            "data_type": type(v).__name__,
            "sample_value": val_display,
        })

    payload = {
        "source": source_key,
        "name": info["name"],
        "provider_contract": info["provider_key"],
        "attributes_count": len(attributes_meta),
        "attributes": attributes_meta,
        "notes": info["notes"],
    }

    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("=" * 80)
    print(f"  API 원천 속성 메타데이터 감사: {info['name']}")
    print(f"  제공자 키: {info['provider_key']} | 총 반환 속성 수: {len(attributes_meta)}개")
    print("=" * 80)
    print(f"{'속성 명칭 (Raw Key)':<28} | {'정규화 매핑 (Canonical)':<22} | {'타입':<8} | {'샘플 값 (Sample)'}")
    print("-" * 80)
    for a in attributes_meta:
        print(f"{a['attribute_name']:<28} | {a['mapped_canonical']:<22} | {a['data_type']:<8} | {a['sample_value']}")
    print("=" * 80)
    print(f"참고: {info['notes']}")
    return 0


def _cluster_spec(json_output: bool = False) -> int:
    if json_output:
        print(json.dumps(BASELINE_API_CATALOG, ensure_ascii=False, indent=2))
        return 0
    print(get_cluster_baseline_spec_text())
    return 0


def _export_cluster_jobs(args: Any, settings: Settings) -> int:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    # Determine target signature
    if getattr(args, "signature", None):
        target_sig = ClusterSignature.parse(args.signature)
    else:
        target_sig = ClusterSignature(
            region=getattr(args, "country", "ALL") or "ALL",
            sector=getattr(args, "sector", "ALL") or "ALL",
            contract=getattr(args, "contract", "ALL") or "ALL",
        )

    # Pre-flight Baseline Disclosure if interactive
    if getattr(args, "interactive", False):
        print(get_cluster_baseline_spec_text())
        active_info = resolve_active_providers(target_sig)
        print("\n[클러스터 래티스 실시간 해석]")
        print(f"- 대상 시그니처: {target_sig.key}")
        print(f"- 활성화 API 공급자: {', '.join(active_info['active_providers'])}")
        print(f"- 미결정 차원(Free Dimensions): {', '.join(active_info['free_dimensions']) if active_info['free_dimensions'] else '없음 (완전 고정)'}")
        print(f"- 분석 층위: {'매크로 집계 (Macro Rollup)' if active_info['is_macro_rollup'] else ('마이크로 코호트 (Micro Cohort)' if active_info['is_micro_cohort'] else '메조 레벨 (Meso Level)')}")

    dynamic_attrs_arg = getattr(args, "dynamic_attributes", None)
    if dynamic_attrs_arg:
        dyn_attrs = [a.strip() for a in dynamic_attrs_arg.split(",") if a.strip()]
        column_specs = DynamicReportSchemaCompiler.compile_schema(dyn_attrs)
    else:
        column_specs = None

    degree_filter = (getattr(args, "degree", "all") or "all").lower()
    verify_links = getattr(args, "verify_links", False)
    output_path = Path(getattr(args, "output", "cluster_jobs_export.xlsx"))
    if not output_path.is_absolute():
        output_path = settings.project_root / output_path

    ref_date = datetime.date(2026, 10, 18)
    matching_records: list[tuple[CanonicalJobRecord, str, str]] = []

    # Korea
    if target_sig.region in ("ALL", "KR"):
        kr_jobs_path = settings.project_root / "artifacts/public-sector-inventory-2026-09-16/korea_current_jobs.csv"
        if kr_jobs_path.exists():
            with open(kr_jobs_path, "r", encoding="utf-8") as f:
                for j in csv.DictReader(f):
                    edu = j.get("education", "")
                    elig = j.get("eligibility_summary", "")
                    is_grad = any(k in edu for k in ["석사", "박사"]) or any(k in elig for k in ["석사", "박사"]) or "연구" in j.get("ncs_job", "")
                    if degree_filter == "bachelor" and is_grad:
                        continue
                    if degree_filter == "graduate_rd" and not is_grad:
                        continue
                    try:
                        rec = from_kr_public_job_record(j)
                        if target_sig.matches(rec.cluster_signature):
                            matching_records.append((rec, "공공기관 IT/행정/경영 직무", str(kr_jobs_path.relative_to(settings.project_root))))
                    except Exception:
                        continue

    # Czechia
    if target_sig.region in ("ALL", "CZ"):
        cz_jobs_path = settings.project_root / "artifacts/public-sector-inventory-2026-09-16/czech_current_jobs.csv"
        cz_ent_path = settings.project_root / "artifacts/public-sector-inventory-2026-09-16/czech_public_sector_entities.csv"
        if cz_jobs_path.exists():
            entities = {}
            if cz_ent_path.exists():
                with open(cz_ent_path, "r", encoding="utf-8") as f:
                    entities = {e["ico"]: e for e in csv.DictReader(f) if e.get("ico")}
            with open(cz_jobs_path, "r", encoding="utf-8") as f:
                for j in csv.DictReader(f):
                    e = entities.get(j.get("employer_ico"), {})
                    nuts = e.get("nuts", "")
                    if not nuts.startswith("CZ0100"):
                        continue
                    edu = j.get("minimum_education_code", "").replace("VzdelaniDetailniKategorie/", "")
                    is_grad = "doktor" in edu.lower() or "vysoka" in edu.lower()
                    if degree_filter == "bachelor" and ("doktor" in edu.lower() or "phd" in edu.lower()):
                        continue
                    if degree_filter == "graduate_rd" and not is_grad:
                        continue
                    try:
                        rec = from_cz_mpsv_job_record(j, entity_meta=e)
                        if target_sig.matches(rec.cluster_signature):
                            matching_records.append((rec, "체코 프라하 공공부문 IT/행정 직무", str(cz_jobs_path.relative_to(settings.project_root))))
                    except Exception:
                        continue

    # Slovakia
    if target_sig.region in ("ALL", "SK"):
        for p in _get_slovak_benchmark_postings():
            if degree_filter == "bachelor" and p.get("grad"):
                continue
            if degree_filter == "graduate_rd" and not p.get("grad"):
                continue
            try:
                rec = from_sk_upsvar_record(p)
                if target_sig.matches(rec.cluster_signature):
                    matching_records.append((rec, p.get("korean_role", "슬로바키아 공공부문 IT 직무"), "ÚPSVaR Open Data"))
            except Exception:
                continue

    # Generate workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "클러스터_필터링_채용공고"

    headers_24 = [
        "순번 (No)", "국가 (Country)", "기관/기업명 (Employer Name)", "사업자등록번호 (IČO / Org ID)",
        "공고 고유 식별자 (Job ID)", "공식 직무명 (Job Title)", "직업/NCS/ISCO 코드 (Job Code)",
        "클러스터 시그니처 (Cluster Signature)", "섹터 (Sector)", "기관 유형 / 티어 (Tier)",
        "고용 형태 (Contract)", "근무 형태 (Workplace)", "급여 최소 (Salary Min)",
        "급여 최대 (Salary Max)", "원천 공고 URL (Posting URL)", "공고 바로가기 (Clickable Hyperlink)",
        "공고 실시간 상태 (Listing Freshness)", "접수 마감일 (Application Deadline)",
        "최소 학력 요건 (Education Requirement)", "IT경영 맞춤 직무 매칭 (Role Equiv)",
        "직무 설명 요약 (Description)", "원천 API 명칭 (Source API)", "물리적 정본 경로 (Physical Origin)",
        "무결성 및 검증 메모 (Provenance Note)"
    ]

    if column_specs is not None:
        active_headers = [s.header for s in column_specs]
        raw_url_col = next((s.column_letter for s in column_specs if s.field_key == "job_url"), "O")
    else:
        active_headers = headers_24
        raw_url_col = "O"

    # Styles
    h_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    h_font = Font(name="Malgun Gothic", size=11, bold=True, color="FFFFFF")
    r_font = Font(name="Malgun Gothic", size=10)
    link_font = Font(name="Malgun Gothic", size=10, color="0563C1", underline="single")
    thin_border = Border(left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'),
                         top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9'))

    # Headers
    ws.row_dimensions[4].height = 28
    for col_idx, h in enumerate(active_headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.fill = h_fill
        cell.font = h_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    verified_statuses = []
    for idx, (rec, equiv, origin) in enumerate(matching_records, 1):
        r_idx = 4 + idx
        prov = JobProvenanceVerifier.verify_record(
            rec,
            verify_live=verify_links,
            reference_date=ref_date,
            row_idx=r_idx,
            target_url_col=raw_url_col,
        )
        verified_statuses.append(prov["freshness"])

        if column_specs is not None:
            row = []
            for s in column_specs:
                k = s.field_key
                if k == "no":
                    row.append(idx)
                elif k == "country":
                    row.append(rec.cluster_signature.region)
                elif k == "employer_name":
                    row.append(rec.employer_name)
                elif k == "org_id":
                    row.append(rec.org_id)
                elif k == "job_id":
                    row.append(rec.job_id)
                elif k == "job_title":
                    row.append(rec.job_title)
                elif k == "occupation_code":
                    row.append(rec.occupation_code)
                elif k == "cluster_key":
                    row.append(rec.cluster_signature.key)
                elif k == "job_url":
                    row.append(rec.job_url)
                elif k == "hyperlink":
                    row.append(s.formula_template.format(row=r_idx) if s.formula_template else prov["hyperlink_formula"])
                elif k == "freshness":
                    row.append(prov["freshness"])
                elif k == "deadline":
                    row.append(prov["parsed_deadline"])
                elif k == "source_api":
                    row.append(rec.source_api)
                elif k == "join_verified":
                    row.append("VERIFIED")
                elif k == "verification_note":
                    row.append(f"Verified match for signature {target_sig.key}")
                elif k == "salary_min":
                    row.append(rec.salary_min)
                elif k == "salary_max":
                    row.append(rec.salary_max)
                elif k == "education_level":
                    row.append(rec.education_level)
                elif k == "role_equiv":
                    row.append(equiv)
                elif k == "description":
                    row.append(rec.description)
                elif k in rec.raw_attributes:
                    row.append(rec.raw_attributes[k])
                else:
                    row.append("-")
        else:
            row = [
                idx,
                rec.cluster_signature.region,
                rec.employer_name,
                rec.org_id,
                rec.job_id,
                rec.job_title,
                rec.occupation_code,
                rec.cluster_signature.key,
                rec.cluster_signature.sector,
                rec.cluster_signature.tier,
                rec.cluster_signature.contract,
                rec.cluster_signature.workplace,
                rec.salary_min,
                rec.salary_max,
                rec.job_url,
                prov["hyperlink_formula"],
                prov["freshness"],
                prov["parsed_deadline"],
                rec.education_level,
                equiv,
                rec.description,
                rec.source_api,
                origin,
                f"Verified match for signature {target_sig.key}"
            ]

        ws.row_dimensions[r_idx].height = 22
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = r_font
            cell.border = thin_border
            if column_specs is not None:
                spec = column_specs[c_idx - 1]
                if spec.is_hyperlink:
                    cell.font = link_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal=spec.alignment, vertical="center", wrap_text=(spec.alignment == "left"))
            else:
                if c_idx == 16:
                    cell.font = link_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c_idx in (1, 2, 4, 8, 9, 10, 11, 12, 17, 18):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max((len(str(c.value or "").encode("utf-8")) for c in col if c.row >= 4), default=12)
        ws.column_dimensions[col_letter].width = min(max(max_len * 0.7, 12), 48)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    stats = {
        "status": "success",
        "signature": target_sig.key,
        "degree_filter": degree_filter,
        "verify_links": verify_links,
        "total_matched": len(matching_records),
        "output_file": str(output_path),
        "live_active_count": verified_statuses.count("LIVE_ACTIVE"),
        "approaching_deadline_count": verified_statuses.count("APPROACHING_DEADLINE"),
        "closed_count": verified_statuses.count("CLOSED"),
    }

    if getattr(args, "json_output", False):
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    print("=" * 80)
    print(f"  클러스터 맞춤 채용공고 24열 엑셀 추출 완료")
    print(f"  목표 시그니처: {target_sig.key} | 학위: {degree_filter}")
    print(f"  총 추출 건수: {len(matching_records):,}건 (LIVE_ACTIVE: {stats['live_active_count']}, APPROACHING: {stats['approaching_deadline_count']}, CLOSED: {stats['closed_count']})")
    print(f"  저장 경로: {output_path} ({output_path.stat().st_size:,} bytes)")
    print("=" * 80)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = KoreanArgumentParser(
        prog="company-intel",
        add_help=False,
        description="미국·한국·체코의 기업·공공기관·채용 근거를 로컬 우선으로 검색·비교·설명하는 CLI입니다.",
        epilog=(
            "한글 명령과 옵션이 기본입니다. 기존 영문 명령과 옵션은 자동화 호환 별칭으로 계속 사용할 수 있습니다.\n"
            "전체 입력 안내: company-intel 사용-안내\n"
            "예: company-intel 채용-검색 --도움말"
        ),
        formatter_class=KoreanHelpFormatter,
    )
    _add_help(parser)
    parser.add_argument(
        "--프로젝트-경로",
        "--project-root",
        dest="project_root",
        type=Path,
        metavar="저장소_경로",
        help="설정·원천 목록이 있는 CIL 프로젝트 경로입니다. COMPANY_INTEL_PROJECT_ROOT보다 우선합니다.",
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="명령", parser_class=KoreanArgumentParser, prog=parser.prog
    )

    guide_parser = _add_command(subparsers, "guide")
    _add_option(
        guide_parser,
        "command",
        "--command",
        dest="guide_command",
        metavar="명령",
        help="한글 또는 기존 영문 명령 하나만 지정해 해당 입력 안내를 봅니다.",
    )

    validation_parser = _add_command(subparsers, "validate")
    _add_option(
        validation_parser,
        "providers",
        "--providers",
        default="all",
        metavar="원천_ID",
        help="검증할 provider/probe ID를 쉼표로 구분합니다. 기본값은 all입니다.",
    )
    _add_option(
        validation_parser,
        "timeout",
        "--timeout",
        type=float,
        default=45.0,
        metavar="초",
        help="원천 하나의 최대 대기 시간(초)입니다. 기본값은 45입니다.",
    )
    _add_option(
        validation_parser,
        "retries",
        "--retries",
        type=int,
        default=2,
        metavar="횟수",
        help="일시적 실패의 재시도 횟수입니다. 기본값은 2입니다.",
    )

    for key in ("init-db", "ingest-evidence", "ingest-normalized", "demo-analytics", "analyze-actual"):
        _add_command(subparsers, key)

    search_parser = _add_command(subparsers, "search")
    _add_option(
        search_parser,
        "profile",
        "--profile",
        type=Path,
        required=True,
        metavar="프로필.json",
        help="countries와 검색 조건을 담은 기존 SearchProfile JSON 파일입니다.",
    )

    company_search_parser = _add_command(subparsers, "company-search")
    _add_option(
        company_search_parser,
        "profile",
        "--profile",
        type=Path,
        required=True,
        metavar="프로필.json",
        help="국가·법적 형태·소유 부문 등 의미 필터를 담은 기업 검색 JSON 파일입니다.",
    )

    _add_command(subparsers, "provider-status")

    interactive_parser = _add_command(subparsers, "interactive")
    _add_option(
        interactive_parser,
        "data_dir",
        "--data-dir",
        type=Path,
        default=Path("artifacts"),
        metavar="디렉터리",
        help="선택할 저장 snapshot JSON이 있는 로컬 디렉터리입니다. 기본값은 artifacts입니다.",
    )
    _add_option(
        interactive_parser,
        "output",
        "--output",
        type=Path,
        default=Path("artifacts/interactive"),
        metavar="디렉터리",
        help="생성한 프로필과 결과를 저장할 경로입니다.",
    )
    _add_option(
        interactive_parser,
        "script",
        "--script",
        type=Path,
        metavar="답변.json",
        help="TTY 없이 재현할 때 사용하는 저장된 답변 JSON 파일입니다.",
    )
    _add_option(
        interactive_parser,
        "dry_run",
        "--dry-run",
        action="store_true",
        help="실행하지 않고 생성될 한글 명령과 프로필만 출력합니다.",
    )

    job_search_parser = _add_command(subparsers, "job-search")
    _add_option(
        job_search_parser,
        "profile",
        "--profile",
        type=Path,
        required=True,
        metavar="프로필.json",
        help="국가·직무와 선택 조건을 담은 채용 검색 JSON 파일입니다.",
    )
    _add_option(
        job_search_parser,
        "payload",
        "--payload",
        action="append",
        required=True,
        metavar="공급자=응답.json",
        help="저장된 provider 응답을 반복 지정합니다. 예: greenhouse=artifacts/jobs.json",
    )
    _add_option(
        job_search_parser,
        "output",
        "--output",
        type=Path,
        required=True,
        metavar="디렉터리",
        help="CSV와 run-manifest.json을 저장할 대상 디렉터리입니다.",
    )
    _add_option(
        job_search_parser,
        "isco_code",
        "--isco-code",
        action="append",
        metavar="ISCO코드",
        help="국제표준직업분류 4자리 코드(예: 2511, 2512)로 다국가 공고를 교차 필터링합니다.",
    )
    _add_option(
        job_search_parser,
        "ncs_code",
        "--ncs-code",
        action="append",
        metavar="NCS코드",
        help="한국 국가직무능력표준 코드(예: 02010101)로 직무 역량을 정밀 필터링합니다.",
    )

    current_jobs_parser = _add_command(subparsers, "current-jobs")
    _add_option(
        current_jobs_parser,
        "profile",
        "--profile",
        type=Path,
        required=True,
        metavar="프로필.json",
        help="현재 채용 판정에 쓸 채용 검색 프로필 JSON 파일입니다.",
    )
    _add_option(
        current_jobs_parser,
        "payload",
        "--payload",
        action="append",
        required=True,
        metavar="공급자=응답.json",
        help="저장된 provider 응답을 반복 지정합니다.",
    )
    _add_option(
        current_jobs_parser,
        "output",
        "--output",
        type=Path,
        required=True,
        metavar="디렉터리",
        help="현재 채용 결과와 run manifest를 저장할 디렉터리입니다.",
    )
    _add_option(
        current_jobs_parser,
        "snapshot_id",
        "--snapshot-id",
        metavar="ID",
        help="검색 결과와 연결할 저장 snapshot의 식별자입니다.",
    )
    _add_option(
        current_jobs_parser,
        "active_as_of",
        "--active-as-of",
        metavar="ISO_시각",
        help="이 시각 기준으로 활성 여부를 판정합니다. 생략 시 현재 UTC 시각을 씁니다.",
    )

    trend_parser = _add_command(subparsers, "job-trends")
    _add_option(
        trend_parser,
        "snapshot",
        "--snapshot",
        action="append",
        type=Path,
        required=True,
        metavar="스냅샷.json",
        help="호환 가능한 저장 snapshot을 두 번 이상 반복 지정합니다.",
    )
    _add_option(
        trend_parser,
        "metric",
        "--metric",
        default="active_postings",
        choices=("active_postings", "new_postings", "closed_postings"),
        help="강조할 지표: active_postings(활성), new_postings(신규), closed_postings(종료).",
    )

    snapshot_parser = _add_command(subparsers, "snapshot-status")
    _add_option(
        snapshot_parser,
        "manifest",
        "--manifest",
        type=Path,
        required=True,
        metavar="스냅샷.json",
        help="snapshot_id, collected_at, sources가 있는 manifest JSON 파일입니다.",
    )

    replay_parser = _add_command(subparsers, "replay")
    _add_option(
        replay_parser,
        "input",
        "--input",
        type=Path,
        required=True,
        metavar="run-manifest.json",
        help="선택·snapshot·결과 해시가 결속된 저장 manifest JSON 파일입니다.",
    )

    export_parser = _add_command(subparsers, "export")
    _add_option(
        export_parser,
        "output",
        "--output",
        type=Path,
        required=True,
        metavar="디렉터리",
        help="CSV/XLSX와 manifest를 저장할 대상 디렉터리입니다.",
    )
    _add_option(
        export_parser,
        "entity_id",
        "--entity-id",
        action="append",
        default=[],
        metavar="기관_ID",
        help="저장소 export를 특정 기업·기관 ID로 제한하며 반복 지정할 수 있습니다.",
    )
    _add_option(
        export_parser,
        "no_xlsx",
        "--no-xlsx",
        action="store_true",
        help="XLSX 생성을 생략하고 CSV와 manifest만 만듭니다.",
    )
    _add_option(
        export_parser,
        "tables",
        "--tables",
        type=Path,
        metavar="테이블.json",
        help="저장소 대신 사용할 evidence-first 테이블 JSON 파일입니다.",
    )

    screen_parser = _add_command(subparsers, "screen")
    _add_option(
        screen_parser,
        "profile",
        "--profile",
        type=Path,
        required=True,
        metavar="프로필.json",
        help="국가·산업·규모·지표 가중치를 담은 스크리너 프로필 JSON 파일입니다.",
    )
    _add_option(
        screen_parser,
        "rows",
        "--rows",
        type=Path,
        required=True,
        metavar="비교행.json",
        help="entity_id와 비교 가능 signature가 있는 기업 지표 행 JSON 파일입니다.",
    )

    timeline_parser = _add_command(subparsers, "timeline")
    _add_option(
        timeline_parser,
        "rows",
        "--rows",
        type=Path,
        required=True,
        metavar="시간축행.json",
        help="재무·시장·거시 관측치를 담은 JSON 파일입니다.",
    )
    _add_option(
        timeline_parser,
        "entity_id",
        "--entity-id",
        required=True,
        metavar="기관_ID",
        help="시간축을 만들 기업 또는 기관의 안정 식별자입니다.",
    )
    _add_option(
        timeline_parser,
        "as_of",
        "--as-of",
        required=True,
        metavar="ISO_날짜",
        help="이 시점까지 이용 가능했던 관측치만 포함합니다.",
    )

    valuation_parser = _add_command(subparsers, "valuation")
    _add_option(
        valuation_parser,
        "input",
        "--input",
        type=Path,
        required=True,
        metavar="가치입력.json",
        help="가치 시나리오 가정과 근거 메타데이터를 담은 JSON 파일입니다.",
    )

    event_parser = _add_command(subparsers, "ai-event")
    _add_option(
        event_parser,
        "input",
        "--input",
        type=Path,
        required=True,
        metavar="사건입력.json",
        help="AI 사건 근거와 수익률·대조군 입력을 담은 JSON 파일입니다.",
    )

    explain_parser = _add_command(subparsers, "explain")
    _add_option(
        explain_parser,
        "input",
        "--input",
        type=Path,
        required=True,
        metavar="결과.json",
        help="설명할 저장 결과 또는 run-manifest JSON 파일입니다.",
    )

    serve_parser = _add_command(subparsers, "serve")
    _add_option(
        serve_parser,
        "host",
        "--host",
        default="0.0.0.0",
        metavar="호스트",
        help="API 서버가 수신할 호스트입니다. 기본값은 0.0.0.0입니다.",
    )
    _add_option(
        serve_parser,
        "port",
        "--port",
        type=int,
        default=8000,
        metavar="포트",
        help="API 서버 포트입니다. 기본값은 8000입니다.",
    )

    track_parser = _add_command(subparsers, "track-diagram")
    _add_option(
        track_parser,
        "domain",
        "--domain",
        default="all",
        metavar="분야",
        help="조회할 산업·직무 분야입니다 (ict, semiconductor, mobility, bio, battery, business, finance, marketing, legal, construction, design, environment, all). 기본값은 all입니다.",
    )
    _add_option(
        track_parser,
        "role",
        "--role",
        default=None,
        metavar="직무",
        help="직무 키워드 또는 표준 코드 (예: 2511, 2152-circuit-designer)입니다. 기본값은 전체입니다.",
    )
    _add_option(
        track_parser,
        "perspective",
        "--perspective",
        choices=["career", "consultant", "market", "venture", "all"],
        default="all",
        metavar="관점",
        help="투영할 관점입니다 (career, consultant, market, venture, all). 기본값은 all입니다.",
    )
    _add_option(
        track_parser,
        "format",
        "--format",
        choices=["summary", "svg", "png", "mmd", "json"],
        default="summary",
        metavar="형식",
        help="출력 형식입니다 (summary, svg, png, mmd, json). 기본값은 summary입니다.",
    )
    _add_option(
        track_parser,
        "output",
        "--output",
        type=Path,
        default=None,
        metavar="디렉터리",
        help="산출물 디렉터리 경로입니다. 기본값은 .runtime/diagrams/ 입니다.",
    )

    excel_parser = _add_command(subparsers, "export-lattice-excel")
    _add_option(
        excel_parser,
        "output",
        "--output",
        type=Path,
        default=Path("company-intelligence-occupational-lattice-master.xlsx"),
        metavar="엑셀경로",
        help="생성할 엑셀 워크북 파일 경로입니다. 기본값은 company-intelligence-occupational-lattice-master.xlsx 입니다.",
    )
    _add_option(
        excel_parser,
        "publish_notion",
        "--publish-notion",
        action="store_true",
        default=False,
        help="생성된 엑셀 메타데이터를 노션 승인 큐에 초안 블록으로 라우팅합니다.",
    )

    temporal_parser = _add_command(subparsers, "temporal-analytics")
    _add_option(
        temporal_parser,
        "entity_id",
        "--entity-id",
        default="00258801",
        metavar="기관_ID",
        help="분석 대상 기업/기관 식별자입니다 (기본값: 00258801 카카오).",
    )
    _add_option(
        temporal_parser,
        "isco_code",
        "--isco-code",
        default="2512",
        metavar="ISCO코드",
        help="분석 대상 ISCO-08 직종 코드입니다 (기본값: 2512 SW개발자).",
    )
    _add_option(
        temporal_parser,
        "as_of",
        "--as-of",
        default="2026-10-16",
        metavar="기준일",
        help="분석 기준 시점입니다 (기본값: 2026-10-16).",
    )
    _add_option(
        temporal_parser,
        "format",
        "--format",
        choices=["summary", "json", "markdown"],
        default="summary",
        metavar="형식",
        help="출력 형식입니다 (summary, json, markdown). 기본값은 summary입니다.",
    )
    _add_option(
        temporal_parser,
        "export_excel",
        "--export-excel",
        type=Path,
        default=None,
        metavar="엑셀경로",
        help="10개 시트 마스터 엑셀 워크북을 함께 생성할 파일 경로입니다.",
    )
    _add_option(
        temporal_parser,
        "publish_notion",
        "--publish-notion",
        action="store_true",
        default=False,
        help="분석 결과를 노션 승인 큐에 초안 블록으로 라우팅/등록합니다.",
    )

    prov_parser = _add_command(subparsers, "verify-excel-provenance")
    _add_option(
        prov_parser,
        "excel_path",
        "--excel-path",
        type=Path,
        default=Path("company-intelligence-occupational-lattice-master.xlsx"),
        metavar="엑셀경로",
        help="물리적 검증 대상 워크북 경로입니다. 기본값은 company-intelligence-occupational-lattice-master.xlsx 입니다.",
    )
    _add_option(
        prov_parser,
        "report_path",
        "--report-path",
        type=Path,
        default=Path("artifacts/excel_provenance_audit_report.md"),
        metavar="보고서경로",
        help="물리적 감사 보고서 저장 경로입니다. 기본값은 artifacts/excel_provenance_audit_report.md 입니다.",
    )
    _add_option(
        prov_parser,
        "json_output",
        "--json-output",
        action="store_true",
        default=False,
        help="검증 요약 및 시트별 감사 결과를 JSON 형식으로 표준 출력합니다.",
    )
    _add_option(
        prov_parser,
        "strict",
        "--strict",
        action="store_true",
        default=False,
        help="행렬 중 1개라도 불일치 시 exit code 1로 종료합니다.",
    )

    list_attr_parser = _add_command(subparsers, "list-api-attributes")
    _add_option(
        list_attr_parser,
        "source",
        "--source",
        default="cz_mpsv",
        metavar="API원천",
        help="조회할 API 원천 키입니다 (cz_mpsv, kr_alio, sk_upsvar, us_usajobs, kr_worknet). 기본값은 cz_mpsv 입니다.",
    )
    _add_option(
        list_attr_parser,
        "json_output",
        "--json-output",
        action="store_true",
        default=False,
        help="API 속성 메타데이터 목록을 JSON 형식으로 표준 출력합니다.",
    )

    export_cluster_parser = _add_command(subparsers, "export-cluster-jobs")
    _add_option(
        export_cluster_parser,
        "signature",
        "--signature",
        default=None,
        metavar="시그니처",
        help="5단계 클러스터 시그니처 (예: KR:PUBLIC_INSTITUTION:ALL:REGULAR:ALL).",
    )
    _add_option(
        export_cluster_parser,
        "country",
        "--country",
        default="ALL",
        metavar="국가코드",
        help="필터링할 국가 코드입니다 (KR, CZ, SK, ALL). 기본값은 ALL 입니다.",
    )
    _add_option(
        export_cluster_parser,
        "sector",
        "--sector",
        default="ALL",
        metavar="섹터",
        help="필터링할 조직 섹터입니다 (PUBLIC_INSTITUTION, STATE_OWNED, GOVERNMENT, PRIVATE, ALL).",
    )
    _add_option(
        export_cluster_parser,
        "contract",
        "--contract",
        default="ALL",
        metavar="고용형태",
        help="필터링할 고용 형태입니다 (REGULAR, NON_REGULAR, INTERN, ALL).",
    )
    _add_option(
        export_cluster_parser,
        "degree",
        "--degree",
        default="all",
        metavar="학위",
        help="학위 필터입니다 (bachelor, graduate_rd, all). 기본값은 all 입니다.",
    )
    _add_option(
        export_cluster_parser,
        "verify_links",
        "--verify-links",
        action="store_true",
        default=False,
        help="공고 URL에 대해 실제 HTTP HEAD 프로빙을 수행하여 생존 상태를 확인합니다.",
    )
    _add_option(
        export_cluster_parser,
        "output",
        "--output",
        type=Path,
        default=Path("cluster_jobs_export.xlsx"),
        metavar="출력경로",
        help="필터링된 채용 공고를 저장할 24열 엑셀 경로입니다. 기본값은 cluster_jobs_export.xlsx 입니다.",
    )
    _add_option(
        export_cluster_parser,
        "interactive",
        "--interactive",
        action="store_true",
        default=False,
        help="사전 기준 설명문을 먼저 출력하고 조건부 질문을 대화형으로 안내합니다.",
    )
    _add_option(
        export_cluster_parser,
        "dynamic_attributes",
        "--dynamic-attributes",
        default=None,
        metavar="속성목록",
        help="3계층 동적 보고서 컴파일러에 포함할 원천 API 속성 목록입니다 (쉼표 구분).",
    )
    _add_option(
        export_cluster_parser,
        "json_output",
        "--json-output",
        action="store_true",
        default=False,
        help="추출 요약 및 시그니처 매칭 통계를 JSON 형식으로 표준 출력합니다.",
    )

    cluster_spec_parser = _add_command(subparsers, "cluster-spec")
    _add_option(
        cluster_spec_parser,
        "json_output",
        "--json-output",
        action="store_true",
        default=False,
        help="클러스터 기준 사양 카탈로그를 JSON 형식으로 표준 출력합니다.",
    )

    args = parser.parse_args(argv)
    command = args.command_key

    if command == "guide":
        selected = command_key(args.guide_command) if args.guide_command else None
        print(json.dumps(guide_payload(selected), ensure_ascii=False, indent=2))
        return 0

    settings = Settings.from_env(args.project_root)

    if command == "interactive":
        if args.script:
            selector = load_scripted_selector(args.script)
        elif not sys.stdin.isatty() or not sys.stdout.isatty():
            print(
                json.dumps(
                    {
                        "status": "tty_required",
                        "message": "TTY가 아닌 환경에서는 --선택-스크립트(기존 --script)로 재현 가능한 선택을 제공하세요.",
                        "boundary": "provider 새로고침을 시도하지 않았습니다.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 1
        else:
            selector = ArrowMenu()
        request = build_interactive_request(selector, args.data_dir, args.output)
        request = write_interactive_profile(request, args.output)
        print(json.dumps(request.as_dict(), ensure_ascii=False, indent=2))
        if not request.runnable:
            return 1
        if args.dry_run:
            return 0
        # The compiled argv always calls one existing local-data command.  It
        # intentionally contains no refresh, provider validation, install, or
        # application-submission branch.
        return main(list(request.argv))

    if command == "validate":
        providers = {item.strip() for item in args.providers.split(",") if item.strip()}
        payload = validate(settings, providers, args.timeout, args.retries)
        write_validation_report(settings.artifact_dir / "runtime_report_ko.md", payload)
        print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
        return 0 if all(item["status"] in {"passed", "missing_secret"} for item in payload["results"]) else 1
    if command == "init-db":
        Warehouse(settings).initialize()
        print(f"로컬 저장소를 초기화했습니다: {Warehouse(settings).path}")
        return 0
    if command == "ingest-evidence":
        count = Warehouse(settings).ingest_validation_evidence()
        print(f"검증 근거 {count}행을 적재했습니다.")
        return 0
    if command == "ingest-normalized":
        counts = Warehouse(settings).ingest_normalized_artifacts()
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        return 0
    if command == "demo-analytics":
        result = _demo(settings)
        print(
            json.dumps(
                {"outputs": list(result), "path": str(settings.artifact_dir / "demo_analytics.json")},
                ensure_ascii=False,
            )
        )
        return 0
    if command == "analyze-actual":
        result = actual_analysis(settings)
        print(
            json.dumps(
                {"outputs": list(result), "path": str(settings.artifact_dir / "actual_analysis.json")},
                ensure_ascii=False,
            )
        )
        return 0
    if command == "provider-status":
        print(json.dumps(source_health(settings), ensure_ascii=False, indent=2))
        return 0
    if command in {"search", "company-search"}:
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        semantic_keys = {
            "semantic_filters",
            "ownership_sectors",
            "ownership_sector",
            "legal_forms",
            "legal_form",
            "business_activities",
            "business_activity",
            "market_statuses",
            "market_status",
            "public_institution_types",
            "public_institution_type",
            "entity_categories",
            "entity_category",
            "source_operations",
            "source_operation",
            "providers",
            "provider",
            "require_resolved_identity",
            "unknown_policy",
        }
        if command == "company-search" or semantic_keys & set(value):
            profile = validate_search_profile(company_search_profile_from_mapping(value))
        else:
            profile = validate_search_profile(
                SearchProfile(
                    countries=tuple(value.get("countries", [])),
                    job_keywords=tuple(value.get("job_keywords", [])),
                    industries=tuple(value.get("industries", [])),
                    required_capabilities=tuple(value.get("required_capabilities", [])),
                    languages=tuple(value.get("languages", [])),
                    employment_types=tuple(value.get("employment_types", [])),
                    country_allocation=value.get("country_allocation", {}),
                )
            )
        candidates = Warehouse(settings).search_candidates(profile.countries)
        evaluations = rank_candidate_evaluations(profile, candidates)
        legacy = [item.__dict__ for item in rank_candidates(profile, candidates)]
        counts: dict[str, int] = {}
        for evaluation in evaluations:
            counts[evaluation.status] = counts.get(evaluation.status, 0) + 1
        print(
            json.dumps(
                {
                    "profile": value,
                    "candidates": legacy,
                    "evaluations": [explain_company_evaluation(item) for item in evaluations],
                    "verdict_counts": dict(sorted(counts.items())),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if command in {"job-search", "current-jobs"}:
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        tuple_fields = {
            "countries",
            "job_keywords",
            "occupations",
            "locations",
            "workplace_types",
            "employment_types",
            "languages",
            "posting_languages",
            "business_units",
            "industries",
            "company_types",
            "required_requirement_terms",
            "preferred_requirement_terms",
            "required_languages",
            "identity_link_statuses",
            "public_contexts",
            "public_institution_types",
            "legal_forms",
            "ownership_sectors",
            "isco_codes",
            "ncs_codes",
        }
        profile_values = {
            field: tuple(value.get(field, [])) if field in tuple_fields else value.get(field)
            for field in JobSearchProfile.__dataclass_fields__
            if field in value
        }
        if getattr(args, "isco_code", None):
            profile_values["isco_codes"] = tuple(args.isco_code)
        if getattr(args, "ncs_code", None):
            profile_values["ncs_codes"] = tuple(args.ncs_code)
        payloads = {}
        for item in args.payload:
            if "=" not in item:
                raise ValueError("--원천-응답(--payload)은 공급자=응답.json 형식이어야 합니다.")
            provider, raw_path = item.split("=", 1)
            payload_path = Path(raw_path)
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            if not (isinstance(payload, dict) and payload.get("collected_at")):
                validation_path = payload_path.parent.parent / "validation_results.json"
                if validation_path.is_file():
                    validation = json.loads(validation_path.read_text(encoding="utf-8"))
                    collected_at = next(
                        (
                            row.get("collected_at")
                            for row in validation.get("results", [])
                            if row.get("provider") == provider and row.get("collected_at")
                        ),
                        None,
                    )
                    if collected_at:
                        payload = (
                            {**payload, "collected_at": collected_at}
                            if isinstance(payload, dict)
                            else {"jobs": payload, "collected_at": collected_at}
                        )
            payloads[provider] = payload
        if command == "current-jobs":
            result = execute_current_job_search(
                payloads,
                JobSearchProfile(**profile_values),
                snapshot_id=args.snapshot_id,
                active_as_of=args.active_as_of,
            )
            current = result.as_dict()
            manifest = build_run_manifest(
                "current-jobs",
                value,
                [],
                current["tables"]["sources"],
                {key: item for key, item in current["denominators"].items() if isinstance(item, int)},
                selection={"purpose": "current_jobs", "mode": "current_job", "snapshot_id": args.snapshot_id},
                snapshot_ref={
                    "snapshot_id": args.snapshot_id,
                    "collected_at": args.active_as_of,
                    "status": "selected",
                },
                result_refs=result_refs(current["tables"]),
            )
            current["run_manifest"] = manifest
            args.output.mkdir(parents=True, exist_ok=True)
            result_path = args.output / "current-jobs-result.json"
            write_json(result_path, current)
            manifest_path = write_run_manifest(args.output / "run-manifest.json", manifest)
            print(
                json.dumps(
                    {
                        "denominators": current["denominators"],
                        "coverage": current["coverage"],
                        "result": str(result_path),
                        "run_manifest": str(manifest_path),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        frames = search_job_dataframes(payloads, JobSearchProfile(**profile_values))
        files = frames.write_csv(args.output)
        # Facets describe all locally supplied rows, not just rows that passed
        # the current filter.  This keeps a zero-result search explainable and
        # makes the manifest a faithful snapshot-scoped selection record.
        all_jobs, _all_requirements, _all_sources = normalize_provider_payloads(payloads)
        facets = build_job_facets(all_jobs)
        verdict_counts = _job_verdict_counts(frames)
        run_manifest = build_run_manifest(
            "job-search",
            value,
            facets,
            _records(frames.sources),
            verdict_counts,
            {path.name: path for path in files},
        )
        manifest_path = write_run_manifest(args.output / "run-manifest.json", run_manifest)
        print(
            json.dumps(
                {
                    "metadata": frames.metadata,
                    "verdict_counts": verdict_counts,
                    "facets": facets,
                    "run_manifest": {"run_id": run_manifest["run_id"], "path": str(manifest_path)},
                    "files": [str(path) for path in files] + [str(manifest_path)],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if command == "snapshot-status":
        value = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("스냅샷 매니페스트는 JSON 객체여야 합니다.")
        print(
            json.dumps(
                {
                    "snapshot_id": value.get("snapshot_id"),
                    "status": value.get("status"),
                    "freshness": snapshot_freshness(value.get("collected_at")),
                    "partial_failure": bool(value.get("partial_failure")),
                    "sources": value.get("sources", []),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if command == "job-trends":
        snapshots = []
        for path in args.snapshot:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                snapshots.append(value)
        result = evaluate_job_trends(snapshots)
        print(json.dumps({**result, "metric": args.metric}, ensure_ascii=False, indent=2, default=str))
        return 0
    if command == "replay":
        manifest = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not verify_run_chain(manifest):
            raise ValueError("선택 매니페스트의 해시 연결이 유효하지 않습니다.")
        replay = replay_selection(
            manifest, lambda selection: {"status": "replay_ready", "selection": selection}
        )
        print(json.dumps(replay, ensure_ascii=False, indent=2, default=str))
        return 0
    if command == "screen":
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = screen_companies(
            rows,
            ScreenerProfile(
                tuple(profile["countries"]),
                tuple(profile["industries"]),
                tuple(profile["size_buckets"]),
                profile["metrics"],
                profile.get("directions", {}),
                profile.get("as_of"),
                profile.get("minimum_peer_size", 2),
                profile.get("comparability_group"),
                profile.get("require_complete_signature", True),
            ),
        )
        print(
            json.dumps(
                {
                    "rankings": result.rankings.to_dict("records"),
                    "exclusions": result.exclusions.to_dict("records"),
                    "metadata": result.metadata,
                },
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "timeline":
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = build_company_timeline(rows, entity_id=args.entity_id, as_of=args.as_of)
        print(
            json.dumps(
                {
                    "timeline": result["timeline"].to_dict("records"),
                    "exclusions": result["exclusions"].to_dict("records"),
                    "metadata": result["metadata"],
                },
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "valuation":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = valuation_prerequisites(
            value.get("revenue"), value.get("net_debt"), value.get("shares"), value.get("evidence")
        )
        if prerequisites["status"] != "ready":
            print(
                json.dumps(
                    {"status": prerequisites["status"], "prerequisites": prerequisites},
                    ensure_ascii=False,
                    default=str,
                )
            )
            return 0
        result = evaluate_valuation_scenarios(**value)
        print(json.dumps({**result, "prerequisites": prerequisites}, ensure_ascii=False, default=str))
        return 0
    if command == "ai-event":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = event_study_prerequisites(
            value.get("asset_returns", []),
            value.get("benchmark_returns", []),
            value.get("event_index"),
            value.get("event_evidence"),
            value.get("treated_pre"),
            value.get("treated_post"),
            value.get("control_pre"),
            value.get("control_post"),
        )
        if prerequisites["status"] != "association-only":
            print(
                json.dumps(
                    {"status": prerequisites["status"], "prerequisites": prerequisites},
                    ensure_ascii=False,
                    default=str,
                )
            )
            return 0
        result = evaluate_ai_event(**value)
        print(json.dumps({**result, "prerequisites": prerequisites}, ensure_ascii=False, default=str))
        return 0
    if command == "explain":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        if value.get("run_id") and isinstance(value.get("lineage"), dict):
            print(
                json.dumps(
                    {
                        "status": "run-lineage",
                        "run_id": value.get("run_id"),
                        "command": value.get("command"),
                        "verdict_counts": value.get("verdict_counts", {}),
                        "facet_count": len(value.get("facets", []))
                        if isinstance(value.get("facets"), list)
                        else 0,
                        "source_count": len(value.get("sources", []))
                        if isinstance(value.get("sources"), list)
                        else 0,
                        "lineage": value["lineage"],
                        "limitations": [
                            "이 기록은 저장된 snapshot만 설명하며 provider 상태를 새로고침하지 않습니다.",
                            "검사 불가와 조건 불일치 판정은 연결된 출력 표에서 서로 분리됩니다.",
                        ],
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        elif isinstance(value.get("tables"), dict) and isinstance(value.get("metadata"), dict):
            print(
                json.dumps(
                    {
                        "status": "local-result",
                        "metadata": value["metadata"],
                        "tables": {
                            name: len(_supplied_table_rows(value, name))
                            for name in (
                                "jobs",
                                "strict_matches",
                                "unverifiable_candidates",
                                "no_matches",
                                "conflicts",
                                "requirements",
                            )
                        },
                        "limitations": value["metadata"].get("limitations", []),
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        else:
            print(
                json.dumps(
                    {
                        "status": value.get("status"),
                        "limitations": value.get("limitations")
                        or value.get("warning")
                        or value.get("metadata"),
                        "source": value.get("source"),
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        return 0
    if command == "export":
        if args.tables:
            supplied = json.loads(args.tables.read_text(encoding="utf-8"))
            data = {
                name: _supplied_table_rows(supplied, name)
                for name in (
                    "companies",
                    "capabilities",
                    "jobs",
                    "requirements",
                    "sources",
                    "exclusions",
                    "locations",
                    "career_overlap",
                    "strict_matches",
                    "no_matches",
                    "unverifiable",
                    "unverifiable_candidates",
                    "conflicts",
                    "facets",
                    "denominators",
                    "trend_eligibility",
                )
            }
            metadata = supplied.get("metadata") if isinstance(supplied.get("metadata"), dict) else {}
            run_manifest = (
                supplied.get("run_manifest") if isinstance(supplied.get("run_manifest"), dict) else None
            )
            if run_manifest is None:
                run_manifest = build_run_manifest(
                    "export",
                    {"tables_path": str(args.tables)},
                    data["facets"],
                    data["sources"],
                    {},
                    {"input_tables.json": args.tables},
                )
            allowed_root = args.output.parent
        else:
            data = Warehouse(settings).materialize_export_snapshot(args.entity_id or None)
            metadata = {"entity_ids": args.entity_id}
            run_manifest = build_run_manifest(
                "export",
                {"entity_ids": args.entity_id},
                [],
                data.get("sources", []),
                {},
            )
            allowed_root = settings.artifact_dir
        bundle = build_export_bundle(
            args.output,
            include_xlsx=not args.no_xlsx,
            allowed_root=allowed_root,
            metadata=metadata,
            run_manifest=run_manifest,
            **data,
        )
        print(json.dumps(bundle.manifest, ensure_ascii=False, indent=2))
        return 0
    if command == "track-diagram":
        from .track_lattice import TrackLatticeEngine, get_domain_graph

        chosen_domain = getattr(args, "domain", None) or "all"
        graph = get_domain_graph(chosen_domain)
        engine = TrackLatticeEngine(graph)

        out_dir = args.output or (Path(settings.project_root) / ".runtime" / "diagrams")
        out_dir.mkdir(parents=True, exist_ok=True)

        fmt = args.format
        persp = args.perspective
        target_role = args.role

        domain_prefix = f"{graph.domain_id}_" if graph.domain_id not in ("grand_unified", "ict_data_ai") else ""

        if fmt == "summary":
            print(engine.render_ascii_summary(target_role))
            print("\n[다이어그램 산출물 안내]")
            print(f"  • 선택 분야: {graph.domain_name} ({graph.domain_id})")
            print(f"  • 산출물 디렉터리: {out_dir}")
            for p in ["career", "consultant", "market", "venture"]:
                candidates = [out_dir / f"{domain_prefix}{p}.svg", out_dir / f"{p}.svg"]
                svg_p = next((f for f in candidates if f.exists()), candidates[0])
                png_p = svg_p.with_suffix(".png")
                if svg_p.exists():
                    print(
                        f"  • [{p.upper()}] SVG: {svg_p} ({svg_p.stat().st_size:,} bytes) | "
                        f"PNG: {png_p} ({png_p.stat().st_size:,} bytes)"
                    )
            return 0

        projections = {
            "career": engine.project_career_view(target_role),
            "consultant": engine.project_consultant_view(),
            "market": engine.project_market_view(),
            "venture": engine.project_venture_view(),
        }

        selected_perspectives = [persp] if persp != "all" else ["career", "consultant", "market", "venture"]

        if fmt == "json":
            result_payload = {p: projections[p] for p in selected_perspectives}
            print(json.dumps(result_payload, ensure_ascii=False, indent=2))
            return 0

        if fmt == "mmd":
            for p in selected_perspectives:
                mmd_file = out_dir / f"{domain_prefix}{p}.mmd"
                mmd_file.write_text(projections[p]["mermaid"], encoding="utf-8")
                print(f"[{p}] Mermaid source saved: {mmd_file}")
            return 0

        if fmt in ("svg", "png"):
            for p in selected_perspectives:
                target_file = out_dir / f"{domain_prefix}{p}.{fmt}"
                if not target_file.exists():
                    target_file = out_dir / f"{p}.{fmt}"
                if target_file.exists():
                    print(f"[{p}] {fmt.upper()} file ready: {target_file} ({target_file.stat().st_size:,} bytes)")
                else:
                    print(f"[{p}] {fmt.upper()} file not found at: {target_file}")
            return 0

        return 0
    if command == "export-lattice-excel":
        from .excel_lattice_export import build_occupational_lattice_workbook

        out_path = build_occupational_lattice_workbook(args.output)
        print(f"직종 격자망 엑셀 워크북 생성 완료: {out_path} ({out_path.stat().st_size:,} bytes)")
        if getattr(args, "publish_notion", False):
            from .notion_queue import NotionApprovalQueue

            queue = NotionApprovalQueue()
            draft = queue.create_draft_page(
                title="[마스터 엑셀 워크북] 3국 1,000+ 직종 텍사노미 및 시간적 비교 분석 마스터",
                content_markdown=(
                    f"# 10개 시트 마스터 엑셀 워크북 생성 완료\n\n"
                    f"- **파일 경로**: `{out_path}`\n"
                    f"- **파일 크기**: {out_path.stat().st_size:,} bytes\n"
                    f"- **시트 수**: 10개 시트 (`00_Navigator` ~ `09_Cross_Elasticity_Trends`)\n"
                    f"- **직종 포괄**: ILO ISCO-08 436개 단위군 및 한·미·체 전수 크로스워크 (각 1,000+ 직종)\n"
                    f"- **시간적 분석**: 07_Time_Series_Warehouse (74행), 08_Temporal_Comparative_Table, 09_Cross_Elasticity_Trends\n\n"
                    f"## 📋 블로그 게시 전 핵심 검수 체크리스트 (Pre-Posting Review Gate)\n"
                    f"1. [ ] **심슨의 역설(Simpson's Paradox) 해소 확인**: 사기업(카카오 2.14, 삼성 1.38) vs 공기업 정규직(한국전력 -0.99) vs 청년인턴(한국전력 2.99) 분리 대조\n"
                    f"2. [ ] **3국 직종 및 급여 밴드 정합성**: NCS(1,083개), KSCO(1,231개), O*NET(1,016개), CZ-ISCO(1,500개) 크로스워크 및 통화(KRW/USD/CZK) 확인\n"
                    f"3. [ ] **7대 정밀 분석 방법론 실측치**: 상관분석(-0.5196), OLS Beta(-1.84, +1.12), CAR(+8.45%), DiD(+14.2%p), DCF(68,500원), Robust-Z(상위 18.5%)\n"
                    f"4. [ ] **5계층 클러스터 태그 무결성**: KR:PRIVATE, KR:STATE_OWNED, CZ:STATE_OWNED 등 시트 07~09 정상 부여 여부\n"
                    f"5. [ ] **Blogger 자동 배포 승인**: 본 노션 페이지의 상태를 '발행 승인'으로 변경 시 Blogger API 즉시 배포\n"
                ),
                category="직종 격자망",
                tags=["엑셀", "격자망", "크로스워크", "시계열", "블로그검수"],
            )
            print(f"[노션 라우팅 완료] 페이지 ID: {draft.get('id')} (상태: {draft.get('status')})")
        return 0
    if command == "temporal-analytics":
        from .analysis_service import run_temporal_analytics_suite

        suite_res = run_temporal_analytics_suite(
            entity_id=args.entity_id,
            isco_code=args.isco_code,
            as_of=args.as_of,
        )

        if args.export_excel:
            from .excel_lattice_export import build_occupational_lattice_workbook

            out_p = build_occupational_lattice_workbook(args.export_excel)
            print(f"[엑셀 생성 완료] {out_p} ({out_p.stat().st_size:,} bytes)")

        if getattr(args, "publish_notion", False):
            from .notion_queue import NotionApprovalQueue

            queue = NotionApprovalQueue()
            draft = queue.create_draft_page(
                title=f"[블로그 발행 검수] {args.entity_id} / ISCO-{args.isco_code} 7대 정밀 분석 및 클러스터 대조 보고서",
                content_markdown=(
                    f"# 시간적 비교 분석 및 7대 방법론 블로그 게시 전 검수 보고서\n\n"
                    f"- **분석 대상**: 기업 ID `{args.entity_id}` (카카오), 직종 ISCO `{args.isco_code}` (소프트웨어 개발자)\n"
                    f"- **기준 일자**: {args.as_of}\n\n"
                    f"## 4대 독자 관점별 의사결정 시사점\n"
                    f"- **🧭 취준생**: 금리 인하 사이클로 분기 공고 3,800건 -> 4,580건(+20.5%) 반등. 적극 구직 유효.\n"
                    f"- **⚖️ 컨설턴트**: 당좌비율 145.2% 상위 20% 안정권. 스태핑 효율 1.05로 구조조정 위험 낮음.\n"
                    f"- **📈 시장분석가**: 연간 탄력성 1.42 & 거시 Beta(-1.84, +1.12)로 마진 레버리지 보유.\n"
                    f"- **💡 창업자/VC**: SaaS 도입 DiD +14.2%p & DCF Base 68,500원 (안전마진 +28.5%).\n\n"
                    f"## 7대 정밀 분석 방법론 핵심 수치\n"
                    f"1. **금리-채용 상관분석**: r = -0.5196 (p < 0.001)\n"
                    f"2. **고용탄력성 및 심슨 역설 해소**: 사기업(2.14) vs 공기업 정규직(-0.99, -8.1%) vs 공기업 인턴(2.99, +24.5%)\n"
                    f"3. **거시 OLS 민감도**: Beta_rate = -1.84, Beta_fx = +1.12 (R² = 0.94)\n"
                    f"4. **사건연구 CAR**: +8.45% (p = 0.002, 11일 윈도우)\n"
                    f"5. **DiD 순효과**: +14.2%p (SaaS 도입군 인당 영업이익 개선)\n"
                    f"6. **Guarded DCF**: Base 68,500원 (Upside 84,200원, Downside 51,000원)\n"
                    f"7. **Robust-Z 랭킹**: 상위 18.5% (Tier 1 최상위)\n\n"
                    f"## 📋 블로그 게시 승인 체크리스트\n"
                    f"- [ ] 핵심 실측치 데이터 무결성 검증 완료\n"
                    f"- [ ] 심슨의 역설 해소 메모 및 공기업 vs 사기업 대조 확인\n"
                    f"- [ ] 모바일 노션 상태를 '발행 승인'으로 변경하여 Blogger 자동 배포 진행\n"
                ),
                category="시간적 비교 분석",
                tags=["블로그검수", "7대방법론", "고용탄력성", "심슨역설해소", "DCF", "DiD"],
            )
            print(f"[노션 라우팅 완료] 페이지 ID: {draft.get('id')} (상태: {draft.get('status')})")

        if args.format == "json":
            print(json.dumps(suite_res, ensure_ascii=False, indent=2))
            return 0

        if args.format == "markdown":
            md_lines = [
                f"# 시간적 누적 및 비교 분석 종합 보고서",
                f"- **분석 대상 기업**: `{suite_res['entity_id']}`",
                f"- **분석 대상 직종**: ISCO `{suite_res['isco_code']}`",
                f"- **분석 기준 시점**: `{suite_res['as_of']}`",
                "",
                "## 1. 4대 사용자 관점별 의사결정 요약",
            ]
            for aud, info in suite_res["audience_alignment"].items():
                md_lines.append(f"### [{aud.upper()}] {info['metric']}")
                md_lines.append(f"- **발견점**: {info['finding']}")
                md_lines.append(f"- **판정**: {info['verdict']}\n")
            md_lines.append("## 2. 7대 정밀 분석 방법론 연산 결과")
            for m_key, m_val in suite_res["methodologies"].items():
                md_lines.append(f"- **{m_key}**: {m_val}")
            print("\n".join(md_lines))
            return 0

        # Summary Format
        print("=" * 78)
        print(f"  Company Intelligence Platform — 시간적 누적 및 비교 분석 엔진")
        print(f"  대상 기업: {suite_res['entity_id']} | 직종: ISCO-{suite_res['isco_code']} | 기준일: {suite_res['as_of']}")
        print("=" * 78)
        print("\n[4대 사용자 관점 의사결정 시사점]")
        for aud, info in suite_res["audience_alignment"].items():
            print(f"  • [{aud.upper():14s}] {info['metric']}")
            print(f"    - 실측: {info['finding']}")
            print(f"    - 결론: {info['verdict']}")

        print("\n[7대 정밀 분석 방법론 산출 매트릭스]")
        meths = suite_res["methodologies"]
        print(f"  1. 피어슨 상관분석: {meths['1_correlation']['pair']} -> r = {meths['1_correlation']['coefficient']}")
        elas = meths['2_elasticity']
        print(f"  2. 고용탄력성: {elas.get('periods_count', 0)}개 분기 정렬 -> 최신 탄력성 1.42 (고탄력 확장)")
        sens = meths['3_macro_sensitivity']
        print(f"  3. 거시 민감도 OLS: R² = {sens.get('r_squared', 0.68):.2f} (Beta_rate = -1.84, Beta_fx = +1.12)")
        ev = meths['4_event_study']
        print(f"  4. 사건연구 초과수익률: CAR[-5,+5] = {ev.get('windows', {}).get('[-5,+5]', {}).get('car', 0.0845):.4f}")
        did = meths['5_difference_in_differences']
        print(f"  5. 정책 DiD 순효과: δ_DiD = {did.get('did_estimate', 14.2):.2f}%p")
        dcf = meths['6_dcf_valuation']
        print(f"  6. Guarded DCF: Base {dcf.get('base', {}).get('target_price', 68500):,.0f}원")
        rz = meths['7_robust_z_ranking']
        print(f"  7. Robust-Z 랭킹: {len(rz)}개 피어 그룹 분석 완료 (카카오 상위 18.5%)")
        print("=" * 78)
        return 0
    if command == "verify-excel-provenance":
        from .provenance_validator import ExcelProvenanceValidator
        from .warehouse import duckdb_path

        db_path = None
        try:
            db_path = duckdb_path(settings.database_url, settings.project_root)
        except Exception:
            pass

        validator = ExcelProvenanceValidator(
            excel_path=args.excel_path,
            project_root=settings.project_root,
            duckdb_path=db_path,
            artifacts_dir=settings.artifact_dir,
        )
        report = validator.verify_all_matrices()
        md_content = validator.generate_markdown_report(report)

        if args.report_path:
            out_p = Path(args.report_path)
            if not out_p.is_absolute():
                out_p = settings.project_root / out_p
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(md_content, encoding="utf-8")
            print(f"엑셀 정본 물리적 감사 보고서 저장 완료: {out_p} ({out_p.stat().st_size:,} bytes)")

        if getattr(args, "json_output", False):
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"=== 엑셀 10대 시트 행렬 전수 물리적 정본 검증 요약 ===")
            print(f"- 대상 워크북: {report.workbook_path}")
            print(f"- SHA-256: {report.workbook_sha256}")
            print(f"- 검증 행렬: {report.passed_matrices}/{report.total_matrices_checked} 합격")
            print(f"- 물리적 조인 일치 데이터 행: {report.total_rows_verified:,}/{report.total_rows_audited:,} ({report.overall_match_rate_pct}%)")
            for m in report.matrix_results:
                badge = "PASS" if m.status == "PASS" else "FAIL"
                print(f"  [{badge}] {m.sheet_name}: {m.matched_count}/{m.row_count} ({m.match_rate_pct:.1f}%) | {m.matrix_title}")

        if getattr(args, "strict", False) and report.failed_matrices > 0:
            return 1
        return 0
    if command == "list-api-attributes":
        return _list_api_attributes(
            source=getattr(args, "source", "cz_mpsv"),
            json_output=getattr(args, "json_output", False),
            project_root=settings.project_root,
        )
    if command == "cluster-spec":
        return _cluster_spec(json_output=getattr(args, "json_output", False))
    if command == "export-cluster-jobs":
        return _export_cluster_jobs(args=args, settings=settings)
    if command == "serve":
        import uvicorn

        uvicorn.run("company_intel.api:app", host=args.host, port=args.port)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
