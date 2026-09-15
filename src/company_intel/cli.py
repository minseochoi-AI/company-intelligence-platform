from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, ClassVar

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
    args = parser.parse_args(argv)
    command = args.command_key

    if command == "guide":
        selected = command_key(args.guide_command) if args.guide_command else None
        print(json.dumps(guide_payload(selected), ensure_ascii=False, indent=2))
        return 0

    settings = Settings.from_env(Path.cwd())

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
        }
        profile_values = {
            field: tuple(value.get(field, [])) if field in tuple_fields else value.get(field)
            for field in JobSearchProfile.__dataclass_fields__
            if field in value
        }
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
    if command == "serve":
        import uvicorn

        uvicorn.run("company_intel.api:app", host=args.host, port=args.port)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
