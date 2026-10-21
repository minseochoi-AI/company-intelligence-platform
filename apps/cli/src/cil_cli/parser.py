"""Canonical responsibility owner; migrated from src/company_intel/cli.py."""

from __future__ import annotations
from cil_cli.guides import COMMAND_GUIDES
from cil_cli.guides import command_epilog
from cil_cli.guides import command_key
from cil_cli.guides import guide_payload
from cil_cli.guides import korean_option
from typing import Any, ClassVar
from pathlib import Path
import argparse
import sys


class KoreanHelpFormatter(argparse.HelpFormatter):
    """Translate argparse's structural headings without changing argument contracts."""

    _HEADINGS: ClassVar[dict[str, str]] = {
        "positional arguments": "명령",
        "optional arguments": "선택 인자",
        "options": "선택 인자",
    }

    def add_usage(
        self, usage: str | None, actions: Any, groups: Any, prefix: str | None = None
    ) -> None:
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
    return parser.add_argument(
        korean_option(option_key), english_option, dest=dest or option_key, **kwargs
    )


def _add_command(subparsers: Any, key: str) -> argparse.ArgumentParser:
    guide = next((item for item in COMMAND_GUIDES if item.key == key))
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


def build_parser():
    parser = KoreanArgumentParser(
        prog="company-intel",
        add_help=False,
        description="미국·한국·체코의 기업·공공기관·채용 근거를 로컬 우선으로 검색·비교·설명하는 CLI입니다.",
        epilog="한글 명령과 옵션이 기본입니다. 기존 영문 명령과 옵션은 자동화 호환 별칭으로 계속 사용할 수 있습니다.\n전체 입력 안내: company-intel 사용-안내\n예: company-intel 채용-검색 --도움말",
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
        dest="command",
        required=True,
        metavar="명령",
        parser_class=KoreanArgumentParser,
        prog=parser.prog,
    )
    subparsers.add_parser(
        "research",
        aliases=["조사"],
        help="명시한 요청·저장 snapshot의 조사 Excel과 봉인 보고서",
        add_help=False,
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
    for key in (
        "init-db",
        "ingest-evidence",
        "ingest-normalized",
        "demo-analytics",
        "analyze-actual",
    ):
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
    excel_parser.add_argument(
        "--taxonomy-input",
        type=Path,
        required=True,
        help="명시적으로 선택한 taxonomy-input-v1 JSON",
    )
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
        default=None,
        metavar="기관_ID",
        help="분석 대상 기업/기관 식별자입니다.",
    )
    _add_option(
        temporal_parser,
        "isco_code",
        "--isco-code",
        default=None,
        metavar="ISCO코드",
        help="분석 대상 ISCO-08 직종 코드입니다.",
    )
    _add_option(
        temporal_parser,
        "as_of",
        "--as-of",
        default=None,
        metavar="기준일",
        help="분석 기준 시점입니다.",
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
    export_cluster_parser.add_argument(
        "--snapshot", type=Path, help="명시적으로 선택한 저장 근거 JSON"
    )
    export_cluster_parser.add_argument("--as-of", help="시간대가 있는 조사 기준 시각")
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
    return parser
