"""Canonical responsibility owner; migrated from src/company_intel/cli_guide.py."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArgumentGuide:
    """One terminal option, its input shape, and its Korean explanation."""

    korean_option: str
    english_option: str
    value: str
    description: str
    required: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "한글_옵션": self.korean_option,
            "호환_영문_옵션": self.english_option,
            "값": self.value,
            "필수": self.required,
            "설명": self.description,
        }


@dataclass(frozen=True)
class CommandGuide:
    """A stable implementation key with a Korean terminal presentation."""

    key: str
    korean_name: str
    summary: str
    method: str
    arguments: tuple[ArgumentGuide, ...] = ()
    limitation: str | None = None
    example: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "한글_명령": self.korean_name,
            "호환_영문_명령": self.key,
            "목적": self.summary,
            "방식": self.method,
            "인자": [argument.as_dict() for argument in self.arguments],
        }
        if self.limitation:
            result["제한"] = self.limitation
        if self.example:
            result["예시"] = self.example
        return result


def _arg(
    korean_option: str,
    english_option: str,
    value: str,
    description: str,
    *,
    required: bool = False,
) -> ArgumentGuide:
    return ArgumentGuide(korean_option, english_option, value, description, required)


COMMAND_GUIDES = (
    CommandGuide(
        "guide",
        "사용-안내",
        "모든 한글 명령, 입력 파일 형식, 제한과 예시를 JSON으로 표시합니다.",
        "먼저 이 명령 또는 각 명령의 --도움말을 읽고, 필요한 로컬 JSON 파일을 준비합니다.",
        (
            _arg(
                "--명령", "--command", "한글 또는 영문 명령", "한 명령의 안내만 봅니다."
            ),
        ),
        example="company-intel 사용-안내 --명령 채용-검색",
    ),
    CommandGuide(
        "validate",
        "원천-검증",
        "등록된 provider probe를 호출해 응답 형식·필수 필드를 검증합니다.",
        "네트워크 호출을 수행합니다. 필요한 키는 환경변수에서만 읽고 출력하지 않습니다.",
        (
            _arg(
                "--공급자",
                "--providers",
                "all 또는 쉼표로 구분한 provider/probe ID",
                "검증할 원천을 고릅니다. 기본값은 all입니다.",
            ),
            _arg(
                "--시간제한",
                "--timeout",
                "초 단위 실수",
                "원천 하나의 최대 응답 대기 시간입니다. 기본값은 45초입니다.",
            ),
            _arg(
                "--재시도",
                "--retries",
                "0 이상의 정수",
                "일시적 네트워크 실패의 재시도 횟수입니다. 기본값은 2입니다.",
            ),
        ),
        limitation="실제 API를 호출합니다. 활성화되지 않은 키는 missing_secret으로 보고할 수 있습니다.",
        example="company-intel 원천-검증 --공급자 mpm_public_employment --시간제한 30",
    ),
    CommandGuide(
        "init-db",
        "저장소-초기화",
        "로컬 DuckDB 스키마를 초기화합니다.",
        "DATABASE_URL 설정에 지정된 로컬 저장소에 테이블을 준비합니다.",
        limitation="저장소 위치와 제공자는 환경설정에 따릅니다.",
        example="company-intel 저장소-초기화",
    ),
    CommandGuide(
        "ingest-evidence",
        "근거-적재",
        "저장된 원천 검증 근거 메타데이터를 DuckDB에 적재합니다.",
        "먼저 원천-검증이 만든 로컬 artifact를 준비한 뒤 실행합니다.",
        example="company-intel 근거-적재",
    ),
    CommandGuide(
        "ingest-normalized",
        "정규화-적재",
        "정규화된 재무·거시·가격·채용 행을 DuckDB에 적재합니다.",
        "artifact의 정규화 JSON을 읽어 저장소에 넣습니다. provider를 새로 호출하지 않습니다.",
        example="company-intel 정규화-적재",
    ),
    CommandGuide(
        "demo-analytics",
        "분석-예시",
        "결정론적 예제 데이터로 모든 분석 엔진의 출력 형식을 확인합니다.",
        "외부 API나 사용자 데이터 없이 artifact에 예제 결과를 만듭니다.",
        example="company-intel 분석-예시",
    ),
    CommandGuide(
        "analyze-actual",
        "수집-분석",
        "이미 수집한 API 표본으로 근거 연결 분석을 생성합니다.",
        "로컬 artifact만 읽습니다. 수집되지 않은 축은 결과에서 사용 불가로 남깁니다.",
        example="company-intel 수집-분석",
    ),
    CommandGuide(
        "search",
        "기본-기업-검색",
        "기존 SearchProfile 형식으로 저장된 기업 후보를 검색합니다.",
        "프로필 JSON의 countries와 직무·역량·산업 조건을 사용합니다. 새 의미 필터는 기업-기관-검색을 사용합니다.",
        (
            _arg(
                "--프로필",
                "--profile",
                "SearchProfile JSON 경로",
                "countries와 하나 이상의 검색 조건을 담은 파일입니다.",
                required=True,
            ),
        ),
        example="company-intel 기본-기업-검색 --프로필 search-profile.json",
    ),
    CommandGuide(
        "company-search",
        "기업-기관-검색",
        "법인·공공기관의 국가, 법적 형태, 소유 부문, 산업, 시장 상태를 의미 단위로 검색합니다.",
        "프로필 JSON에서 같은 필드의 여러 값은 OR, 서로 다른 필드는 AND입니다. 법적 형태 등 원천 taxonomy는 namespace:value를 그대로 씁니다.",
        (
            _arg(
                "--프로필",
                "--profile",
                "기업 검색 프로필 JSON 경로",
                "countries는 필수이며, job_keywords 또는 하나 이상의 의미 필터를 넣습니다.",
                required=True,
            ),
        ),
        limitation="채용 전용 필드(급여·근무 방식·지원자 언어)는 이 명령에서 검사 불가로 표시되며 채용-검색에서만 평가합니다.",
        example="company-intel 기업-기관-검색 --프로필 company-profile.json",
    ),
    CommandGuide(
        "provider-status",
        "원천-상태",
        "설정된 provider의 활성화 조건, 저장된 근거, 의미적 사용 경계를 표시합니다.",
        "환경 설정과 저장된 검증 근거를 읽습니다. provider를 새로 호출하지 않습니다.",
        example="company-intel 원천-상태",
    ),
    CommandGuide(
        "interactive",
        "대화형-선택",
        "화살표 키로 목적·조건을 고르고, 동일한 로컬 명령과 프로필로 컴파일합니다.",
        "TTY에서는 ↑/↓ 이동, Space 복수 선택, Enter 확정입니다. 비대화형 환경에서는 저장한 답변 스크립트를 사용합니다.",
        (
            _arg(
                "--데이터-경로",
                "--data-dir",
                "저장 snapshot JSON 디렉터리",
                "로컬 artifact만 탐색합니다. 기본값은 artifacts입니다.",
            ),
            _arg(
                "--출력",
                "--output",
                "디렉터리 경로",
                "생성한 프로필과 검색 결과를 저장할 경로입니다. 기본값은 artifacts/interactive입니다.",
            ),
            _arg(
                "--선택-스크립트",
                "--script",
                "답변 JSON 경로",
                "TTY 없이 재현할 때 사용합니다. 기존 prompt ID는 호환을 위해 영문으로 유지됩니다.",
            ),
            _arg(
                "--미리보기",
                "--dry-run",
                "값 없음",
                "생성할 프로필과 명령만 출력하고 실행하지 않습니다.",
            ),
        ),
        limitation="원천 새로고침, 패키지 설치, 지원 제출을 수행하지 않습니다.",
        example="company-intel 대화형-선택 --데이터-경로 artifacts --출력 artifacts/interactive",
    ),
    CommandGuide(
        "job-search",
        "채용-검색",
        "저장된 provider 채용 응답을 정규화해 조건별 DataFrame/CSV로 검색합니다.",
        "프로필의 countries와 job_keywords 또는 occupations이 필수입니다. 조건은 실제 구조화 필드에서만 검사하고, 확인할 수 없는 값은 unknown_policy에 따라 분리합니다.",
        (
            _arg(
                "--프로필",
                "--profile",
                "채용 검색 프로필 JSON 경로",
                "국가·직무·위치·근무 방식·급여·요건 조건을 담습니다.",
                required=True,
            ),
            _arg(
                "--원천-응답",
                "--payload",
                "provider=/응답.json",
                "반복 지정합니다. 예: greenhouse=artifacts/greenhouse.json. 등록된 provider ID만 사용합니다.",
                required=True,
            ),
            _arg(
                "--출력",
                "--output",
                "디렉터리 경로",
                "jobs, requirements, exclusions 등 CSV와 run-manifest.json을 저장합니다.",
                required=True,
            ),
        ),
        limitation="급여 비교는 통화·지급주기·기준이 모두 같을 때만 합니다. 본문 OTE·환율·연환산은 추정하지 않습니다.",
        example="company-intel 채용-검색 --프로필 profile.json --원천-응답 greenhouse=jobs.json --출력 artifacts/search",
    ),
    CommandGuide(
        "current-jobs",
        "현재-채용",
        "선택한 저장 snapshot을 기준으로 현재 활성 공고와 제외 사유를 계산합니다.",
        "채용-검색과 같은 프로필·payload를 받고, provider 반환→정규화→활성→판정 결과의 분모 사슬을 남깁니다.",
        (
            _arg(
                "--프로필",
                "--profile",
                "채용 검색 프로필 JSON 경로",
                "검색 조건을 담습니다.",
                required=True,
            ),
            _arg(
                "--원천-응답",
                "--payload",
                "provider=/응답.json",
                "반복 지정하는 저장된 provider 응답입니다.",
                required=True,
            ),
            _arg(
                "--출력",
                "--output",
                "디렉터리 경로",
                "current-jobs-result.json과 run-manifest.json을 저장합니다.",
                required=True,
            ),
            _arg(
                "--스냅샷-ID",
                "--snapshot-id",
                "저장 snapshot 식별자",
                "결과를 특정 수집본과 연결합니다.",
            ),
            _arg(
                "--기준시각",
                "--active-as-of",
                "ISO 8601 시각",
                "이 시점에 마감되지 않은 공고만 현재로 판정합니다.",
            ),
        ),
        limitation="MPM처럼 세부 요건이 없는 목록 응답은 불일치로 만들지 않고 검사 불가로 남깁니다.",
        example="company-intel 현재-채용 --프로필 profile.json --원천-응답 mpsv_cz=mpsv.json --출력 artifacts/current",
    ),
    CommandGuide(
        "job-trends",
        "채용-동향",
        "호환 가능한 반복 snapshot만 사용해 활성·신규·종료 공고 수의 시계열을 계산합니다.",
        "같은 provider·taxonomy·normalizer·coverage signature를 가진 snapshot을 두 개 이상 지정합니다.",
        (
            _arg(
                "--스냅샷",
                "--snapshot",
                "snapshot JSON 경로",
                "두 번 이상 반복 지정합니다.",
                required=True,
            ),
            _arg(
                "--지표",
                "--metric",
                "active_postings | new_postings | closed_postings",
                "출력에서 강조할 공고 수 지표입니다. 기본값은 active_postings입니다.",
            ),
        ),
        limitation="공고 증감은 광고된 수요 변화이며 실제 채용 인원 또는 인과 효과가 아닙니다.",
        example="company-intel 채용-동향 --스냅샷 s1.json --스냅샷 s2.json --지표 active_postings",
    ),
    CommandGuide(
        "snapshot-status",
        "스냅샷-상태",
        "저장 snapshot의 최신성·부분 실패·원천 범위를 표시합니다.",
        "manifest JSON만 읽으며 provider를 새로 호출하지 않습니다.",
        (
            _arg(
                "--매니페스트",
                "--manifest",
                "snapshot manifest JSON 경로",
                "snapshot_id, collected_at, sources가 있는 객체여야 합니다.",
                required=True,
            ),
        ),
        example="company-intel 스냅샷-상태 --매니페스트 artifacts/snapshot.json",
    ),
    CommandGuide(
        "replay",
        "선택-재현",
        "저장한 선택 manifest의 해시 연결을 검증하고 로컬 실행 준비 상태를 재현합니다.",
        "입력 manifest의 무결성을 먼저 확인하며 provider를 새로 호출하지 않습니다.",
        (
            _arg(
                "--입력",
                "--input",
                "run-manifest JSON 경로",
                "선택·snapshot·결과 해시가 결속된 파일입니다.",
                required=True,
            ),
        ),
        example="company-intel 선택-재현 --입력 artifacts/search/run-manifest.json",
    ),
    CommandGuide(
        "export",
        "증거-내보내기",
        "기업·공고·요건·제외 사유와 run manifest를 CSV 및 선택 XLSX로 내보냅니다.",
        "--표를 쓰면 제공한 테이블 JSON만 내보내고, 쓰지 않으면 로컬 저장소 snapshot을 사용합니다.",
        (
            _arg(
                "--출력",
                "--output",
                "디렉터리 경로",
                "내보낸 CSV/XLSX와 manifest의 대상 경로입니다.",
                required=True,
            ),
            _arg(
                "--표",
                "--tables",
                "테이블 JSON 경로",
                "evidence-first 로컬 export의 입력입니다.",
            ),
            _arg(
                "--기관-ID",
                "--entity-id",
                "법인/기관 ID",
                "저장소 export를 특정 기관으로 제한하며 반복 지정할 수 있습니다.",
            ),
            _arg(
                "--엑셀-생략",
                "--no-xlsx",
                "값 없음",
                "CSV와 manifest만 만들고 XLSX 생성을 생략합니다.",
            ),
        ),
        example="company-intel 증거-내보내기 --표 tables.json --출력 artifacts/export --엑셀-생략",
    ),
    CommandGuide(
        "screen",
        "기업-비교",
        "의미·단위·통화·기간이 호환되는 동료군 안에서만 기업을 순위화합니다.",
        "프로필 JSON의 countries, industries, size_buckets, metrics와 비교 행 JSON을 함께 사용합니다.",
        (
            _arg(
                "--프로필",
                "--profile",
                "스크리너 프로필 JSON 경로",
                "국가·산업·규모·지표 가중치·기준일을 담습니다.",
                required=True,
            ),
            _arg(
                "--행",
                "--rows",
                "비교 행 JSON 경로",
                "각 행에는 entity_id와 비교 가능 signature 정보가 있어야 합니다.",
                required=True,
            ),
        ),
        limitation="서명(단위·기간·개념·coverage)이 없는 행은 순위에 넣지 않고 제외 사유로 반환합니다.",
        example="company-intel 기업-비교 --프로필 screen.json --행 metrics.json",
    ),
    CommandGuide(
        "timeline",
        "기업-시간축",
        "한 기업의 재무·시장·거시 관측치를 이용 가능 시각 기준으로 정렬합니다.",
        "행 JSON과 대상 entity ID, 기준 시각을 사용하며, 서로 다른 단위·통화·빈도 series는 합치지 않습니다.",
        (
            _arg(
                "--행",
                "--rows",
                "시간축 행 JSON 경로",
                "axis, series_id, available_at을 포함한 관측치입니다.",
                required=True,
            ),
            _arg(
                "--기관-ID",
                "--entity-id",
                "기업/기관 ID",
                "시간축을 만들 대상의 안정 ID입니다.",
                required=True,
            ),
            _arg(
                "--기준일",
                "--as-of",
                "ISO 8601 날짜/시각",
                "이 시점까지 실제 이용 가능했던 값만 사용합니다.",
                required=True,
            ),
        ),
        example="company-intel 기업-시간축 --행 timeline.json --기관-ID entity-1 --기준일 2026-09-15",
    ),
    CommandGuide(
        "valuation",
        "가치-시나리오",
        "근거·시점·단위·통화가 확인된 입력으로 가치 시나리오를 계산합니다.",
        "입력 JSON의 revenue, net_debt, shares, evidence와 가정값을 검사한 뒤, 준비되지 않으면 계산 대신 사전조건을 반환합니다.",
        (
            _arg(
                "--입력",
                "--input",
                "가치 시나리오 JSON 경로",
                "원천 URL·이용 가능 시각·단위·통화가 있는 근거를 포함합니다.",
                required=True,
            ),
        ),
        limitation="연구용 시나리오이며 투자 권유나 미래 가격 예측이 아닙니다.",
        example="company-intel 가치-시나리오 --입력 valuation-input.json",
    ),
    CommandGuide(
        "ai-event",
        "AI-사건-분석",
        "AI 도입 사건 전후의 수익률·성과 변화를 근거와 대조군 조건에 따라 분석합니다.",
        "입력 JSON의 사건 근거, 자산·benchmark 수익률, event_index와 선택적 처리·대조군을 검사합니다.",
        (
            _arg(
                "--입력",
                "--input",
                "AI 사건 분석 JSON 경로",
                "사건 날짜·출처·이용 가능 시각과 시계열을 담습니다.",
                required=True,
            ),
        ),
        limitation="대조군 또는 필수 근거가 없으면 association-only로 표시하며 인과 효과를 주장하지 않습니다.",
        example="company-intel AI-사건-분석 --입력 ai-event.json",
    ),
    CommandGuide(
        "explain",
        "근거-설명",
        "저장한 검색·분석 결과의 제한, 원천 범위, 판정·계보를 설명합니다.",
        "run manifest 또는 로컬 결과 JSON을 읽습니다. provider를 새로 호출하지 않습니다.",
        (
            _arg(
                "--입력",
                "--input",
                "결과 또는 run-manifest JSON 경로",
                "설명할 저장 결과를 지정합니다.",
                required=True,
            ),
        ),
        example="company-intel 근거-설명 --입력 artifacts/search/run-manifest.json",
    ),
    CommandGuide(
        "serve",
        "API-서버",
        "동일한 분석 기능을 제공하는 FastAPI 서버를 시작합니다.",
        "지정한 host·port에서 로컬 API 프로세스를 실행합니다.",
        (
            _arg(
                "--호스트",
                "--host",
                "IP 또는 호스트명",
                "수신할 네트워크 인터페이스입니다. 기본값은 0.0.0.0입니다.",
            ),
            _arg(
                "--포트",
                "--port",
                "1~65535 정수",
                "수신 포트입니다. 기본값은 8000입니다.",
            ),
        ),
        example="company-intel API-서버 --호스트 127.0.0.1 --포트 8000",
    ),
    CommandGuide(
        "track-diagram",
        "직무-트랙-다이어그램",
        "4대 사용자 목적(취준생·컨설턴트·시장분석·창업자)에 최적화된 다면체 직무 트랙 다이어그램 및 격자망 분석을 생성합니다.",
        "ISCO-08 피벗 기반 한국 NCS, 체코 CZ-ISCO, 미국 O*NET 표준 직무 격자망을 4대 관점으로 투영하고 Mermaid 및 다이어그램 산출물을 제공합니다.",
        (
            _arg(
                "--분야",
                "--domain",
                "ict | semiconductor | mobility | bio | battery | business | finance | marketing | legal | construction | design | environment | all",
                "조회할 산업·직무 분야입니다 (기본값: all, 12대 산업 및 대통합 매크로 격자망).",
            ),
            _arg(
                "--직무",
                "--role",
                "직무 키워드 또는 표준 코드 (예: 2511, 2152-circuit-designer)",
                "특정 직무 기준 서브그래프 또는 상세 정보를 조회합니다. 기본값은 전체입니다.",
            ),
            _arg(
                "--관점",
                "--perspective",
                "career | consultant | market | venture | all",
                "투영할 관점을 지정합니다. 기본값은 all입니다.",
            ),
            _arg(
                "--형식",
                "--format",
                "summary | svg | png | mmd | json",
                "출력 형식을 지정합니다. 기본값은 summary입니다.",
            ),
            _arg(
                "--출력",
                "--output",
                "산출물 저장 디렉터리 경로",
                "다이어그램 및 데이터 산출물이 저장될 디렉터리입니다. 기본값은 .runtime/diagrams/ 입니다.",
            ),
        ),
        example="company-intel 직무-트랙-다이어그램 --분야 semiconductor --관점 career --형식 summary",
    ),
    CommandGuide(
        "export-lattice-excel",
        "직종-격자망-엑셀-생성",
        "3국 전수 직종(ISCO 436개, 한국 NCS 1,083개, 미국 ONET 1,016개, 체코 CZ-ISCO 1,500개)과 4대 관점, 시간적 누적·비교 분석 엔진을 포괄하는 10개 시트 다면체 엑셀 워크북을 생성합니다.",
        "00_Navigator 인터랙티브 대시보드 및 9개 관계형·시계열 시트가 포함된 스타일링된 다중 시트 엑셀 워크북(.xlsx)을 컴파일합니다.",
        (
            _arg(
                "--출력",
                "--output",
                "저장할 엑셀 파일 경로 (.xlsx)",
                "생성될 워크북 파일 경로입니다. 기본값은 company-intelligence-occupational-lattice-master.xlsx 입니다.",
            ),
            _arg(
                "--노션-발행",
                "--publish-notion",
                "플래그 (인자 없음)",
                "생성된 엑셀 메타데이터를 노션 승인 큐에 초안 블록으로 라우팅합니다.",
            ),
        ),
        example="company-intel 직종-격자망-엑셀-생성 --출력 master_lattice.xlsx",
    ),
    CommandGuide(
        "temporal-analytics",
        "시간적-비교-분석",
        "기업 재무, 직종 채용, 거시경제 지표의 시계열 누적 자료를 비교하고 7대 정밀 분석 방법론(상관분석, 고용탄력성, OLS Beta, 사건연구, DiD, DCF, Robust-Z)을 전수 실행합니다.",
        "시계열 및 분기 데이터를 기반으로 4대 사용자 관점(취준생, 컨설턴트, 시장분석가, 창업자)별 의사결정 시사점을 도출하고 엑셀/노션과 연동합니다.",
        (
            _arg(
                "--기관-ID",
                "--entity-id",
                "기업/기관 식별자 (예: 00258801)",
                "분석 대상 기업 식별자입니다. 기본값은 00258801(카카오)입니다.",
            ),
            _arg(
                "--직업분류-코드",
                "--isco-code",
                "ISCO 직종 코드 (예: 2512)",
                "분석 대상 직종 코드입니다. 기본값은 2512(SW개발자)입니다.",
            ),
            _arg(
                "--기준일",
                "--as-of",
                "ISO 날짜 (YYYY-MM-DD)",
                "분석 기준 시점입니다. 기본값은 2026-10-16입니다.",
            ),
            _arg(
                "--형식",
                "--format",
                "summary | json | markdown",
                "출력 형식입니다. 기본값은 summary입니다.",
            ),
            _arg(
                "--엑셀-저장",
                "--export-excel",
                "엑셀 저장 파일 경로 (.xlsx)",
                "10개 시트 마스터 엑셀 워크북을 함께 생성할 파일 경로입니다.",
            ),
            _arg(
                "--노션-발행",
                "--publish-notion",
                "플래그 (인자 없음)",
                "분석 결과를 노션 승인 큐에 초안 블록으로 라우팅/등록합니다.",
            ),
        ),
        example="company-intel 시간적-비교-분석 --기관-ID 00258801 --직업분류-코드 2512 --형식 summary",
    ),
    CommandGuide(
        "verify-excel-provenance",
        "엑셀-정본-검증",
        "모든 엑셀 출력 행렬이 어느 API 결과, DB 웨어하우스(DuckDB), 공식 텍사노미(ILO ISCO-08), 원자 과업 실측값에서 유래했는지 물리적 조인으로 검증합니다.",
        "합성 mock fixtures 없이 물리적 파일시스템의 raw API 응답, DuckDB 테이블, ILO SSOT를 전수 조인하여 10개 시트 전 행렬의 정본 일치율과 SHA-256 해시를 감사하고 보고서를 생성합니다.",
        (
            _arg(
                "--엑셀-경로",
                "--excel-path",
                "검증할 엑셀 파일 경로 (.xlsx)",
                "물리적 검증 대상 워크북 경로입니다. 기본값은 company-intelligence-occupational-lattice-master.xlsx 입니다.",
            ),
            _arg(
                "--보고서-경로",
                "--report-path",
                "저장할 마크다운 보고서 경로 (.md)",
                "물리적 감사 보고서 저장 경로입니다. 기본값은 artifacts/excel_provenance_audit_report.md 입니다.",
            ),
            _arg(
                "--json-출력",
                "--json-output",
                "플래그 (인자 없음)",
                "검증 요약 및 시트별 감사 결과를 JSON 형식으로 표준 출력합니다.",
            ),
            _arg(
                "--엄격",
                "--strict",
                "플래그 (인자 없음)",
                "행렬 중 1개라도 불일치 시 exit code 1로 종료합니다.",
            ),
        ),
        example="company-intel 엑셀-정본-검증 --엑셀-경로 company-intelligence-occupational-lattice-master.xlsx",
    ),
    CommandGuide(
        "list-api-attributes",
        "api-속성-조회",
        "지정한 채용 API 공급자(cz_mpsv, kr_alio, sk_upsvar, us_usajobs, kr_worknet)의 반환 속성 키, 타입, 정규화 매핑, 샘플 값을 터미널 테이블 또는 JSON으로 출력합니다.",
        "JobSchemaContract 및 물리적 원천 응답 스키마를 감사하여 누락되거나 불일치하는 속성 키를 사전에 식별하고 검증합니다.",
        (
            _arg(
                "--원천",
                "--source",
                "API 공급자 (cz_mpsv, kr_alio, sk_upsvar, us_usajobs, kr_worknet)",
                "조회할 API 원천 키입니다. 기본값은 cz_mpsv 입니다.",
            ),
            _arg(
                "--json-출력",
                "--json-output",
                "플래그 (인자 없음)",
                "API 속성 메타데이터 목록을 JSON 형식으로 표준 출력합니다.",
            ),
        ),
        example="company-intel api-속성-조회 --원천 cz_mpsv",
    ),
    CommandGuide(
        "export-cluster-jobs",
        "클러스터-채용-추출",
        "5단계 ClusterSignature 또는 조합 조건(국가/섹터/고용형태/학위)을 기반으로 정규화된 공고를 필터링하고 24열 하이퍼링크 엑셀로 원클릭 저장합니다.",
        "CanonicalJobRecord 정규화 및 JobProvenanceVerifier를 거쳐 클릭 가능한 =HYPERLINK() 수식과 공고 실시간 상태가 포함된 엑셀을 생성합니다.",
        (
            _arg(
                "--시그니처",
                "--signature",
                "5단계 클러스터 시그니처 (예: KR:PUBLIC_INSTITUTION:ALL:REGULAR:ALL)",
                "조합 필터링할 클러스터 시그니처입니다. 미지정 시 개별 플래그를 조합합니다.",
            ),
            _arg(
                "--국가",
                "--country",
                "국가 코드 (KR, CZ, SK, US, ALL)",
                "필터링할 국가입니다. 기본값은 ALL 입니다.",
            ),
            _arg(
                "--섹터",
                "--sector",
                "섹터 (PUBLIC_INSTITUTION, STATE_OWNED, GOVERNMENT, PRIVATE, ALL)",
                "필터링할 조직 섹터입니다. 기본값은 ALL 입니다.",
            ),
            _arg(
                "--고용형태",
                "--contract",
                "고용 형태 (REGULAR, NON_REGULAR, INTERN, ALL)",
                "필터링할 고용 계약 형태입니다. 기본값은 ALL 입니다.",
            ),
            _arg(
                "--학위",
                "--degree",
                "학위 필터 (bachelor, graduate_rd, all)",
                "학사 또는 대학원(석박사) 필터입니다. 기본값은 all 입니다.",
            ),
            _arg(
                "--실시간-링크-검증",
                "--verify-links",
                "플래그 (인자 없음)",
                "공고 URL에 대해 실제 HTTP HEAD 프로빙을 수행하여 생존 상태를 확인합니다.",
            ),
            _arg(
                "--출력-경로",
                "--output",
                "저장할 엑셀 파일 경로 (.xlsx)",
                "필터링된 채용 공고를 저장할 24열 엑셀 경로입니다. 기본값은 cluster_jobs_export.xlsx 입니다.",
            ),
            _arg(
                "--대화형",
                "--interactive",
                "플래그 (인자 없음)",
                "사전 기준 설명문을 먼저 출력하고 조건부 질문을 대화형으로 안내합니다.",
            ),
            _arg(
                "--동적-속성",
                "--dynamic-attributes",
                "콤마로 구분된 동적 속성 목록",
                "3계층 동적 보고서 컴파일러에 포함할 원천 API 속성 목록입니다.",
            ),
            _arg(
                "--json-출력",
                "--json-output",
                "플래그 (인자 없음)",
                "추출 요약 및 시그니처 매칭 통계를 JSON 형식으로 표준 출력합니다.",
            ),
        ),
        example="company-intel 클러스터-채용-추출 --국가 CZ --섹터 PUBLIC_INSTITUTION --출력-경로 cz_public_jobs.xlsx",
    ),
    CommandGuide(
        "cluster-spec",
        "클러스터-사양-안내",
        "28개 연결 API, 142개 원천 속성, 35개 티어, 21,000개 클러스터 조합 명세를 사전 브리핑하는 고정 설명문을 출력합니다.",
        "get_cluster_baseline_spec_text()를 호출하여 물리적 공급자 사양 및 5계층 클러스터 좌표계를 표준 출력합니다.",
        (
            _arg(
                "--json-출력",
                "--json-output",
                "플래그 (인자 없음)",
                "클러스터 기준 사양 카탈로그를 JSON 형식으로 표준 출력합니다.",
            ),
        ),
        example="company-intel 클러스터-사양-안내",
    ),
)

# Current contracts replace the historical fixed-count and implicit-file examples.
from dataclasses import replace

COMMAND_GUIDES = tuple(
    replace(
        g,
        summary="등록된 API operation·provider·의미 매핑 수 조회",
        method="동봉 capability catalog에서 서로 다른 계수 단위로 집계한다. 실시간 수신 성공이나 전체 응답 키 수가 아니다.",
        limitation="운영 가용성은 별도 수신 검증 필요",
        example="company-intel cluster-spec",
    )
    if g.key == "cluster-spec"
    else replace(
        g,
        summary="명시한 저장 snapshot에서 클러스터 공고 Excel 생성",
        method="--snapshot와 시간대가 있는 --as-of가 필요하다. 원천 보존·필터·계산·Excel은 모델 호출 없이 처리한다.",
        limitation="예전 CSV나 시연 공고로 자동 대체하지 않는다. 세부 요건은 research request를 사용한다.",
        example="company-intel export-cluster-jobs --snapshot snapshot.json --as-of 2026-10-20T00:00:00Z --signature KR:STATE_OWNED:ALL:REGULAR:ALL --output jobs.xlsx",
    )
    if g.key == "export-cluster-jobs"
    else replace(
        g,
        method="명시한 --taxonomy-input JSON의 taxonomy-input-v1 자료로만 생성한다.",
        limitation="직업 유사도는 회사 승진 규정이 아니다. 미확인 급여·시간축은 비워 둔다.",
    )
    if g.key == "export-lattice-excel"
    else replace(
        g,
        method="시간 비교에는 명시한 research request와 저장 자료를 사용한다.",
        limitation="입력 없이 시연 수치나 고정된 기업 사례를 실제 결과로 생성하지 않는다.",
    )
    if g.key == "temporal-analytics"
    else g
    for g in COMMAND_GUIDES
)

GUIDES_BY_KEY = {guide.key: guide for guide in COMMAND_GUIDES}

COMMAND_KEY_BY_NAME = {
    name: guide.key
    for guide in COMMAND_GUIDES
    for name in (guide.key, guide.korean_name)
}

KOREAN_OPTIONS = {
    "providers": "--공급자",
    "timeout": "--시간제한",
    "retries": "--재시도",
    "profile": "--프로필",
    "data_dir": "--데이터-경로",
    "output": "--출력",
    "script": "--선택-스크립트",
    "dry_run": "--미리보기",
    "payload": "--원천-응답",
    "snapshot_id": "--스냅샷-ID",
    "active_as_of": "--기준시각",
    "snapshot": "--스냅샷",
    "metric": "--지표",
    "manifest": "--매니페스트",
    "input": "--입력",
    "entity_id": "--기관-ID",
    "no_xlsx": "--엑셀-생략",
    "tables": "--표",
    "rows": "--행",
    "as_of": "--기준일",
    "host": "--호스트",
    "port": "--포트",
    "command": "--명령",
    "isco_code": "--직업분류-코드",
    "ncs_code": "--직무능력-코드",
    "role": "--직무",
    "perspective": "--관점",
    "format": "--형식",
    "domain": "--분야",
    "export_excel": "--엑셀-저장",
    "publish_notion": "--노션-발행",
    "excel_path": "--엑셀-경로",
    "report_path": "--보고서-경로",
    "json_output": "--json-출력",
    "strict": "--엄격",
    "source": "--원천",
    "signature": "--시그니처",
    "country": "--국가",
    "sector": "--섹터",
    "contract": "--고용형태",
    "degree": "--학위",
    "verify_links": "--실시간-링크-검증",
    "interactive": "--대화형",
    "dynamic_attributes": "--동적-속성",
}

INPUT_CONTRACTS = {
    "job-search": {
        "파일": "채용 검색 프로필 JSON",
        "필수_필드": {
            "countries": '대문자 ISO 국가 코드 배열. 예: ["US", "KR", "CZ"]',
            "job_keywords 또는 occupations": "직무 키워드 또는 직종명/코드 배열 중 하나 이상",
        },
        "선택_필드": {
            "locations": "근무지 문자열 배열",
            "workplace_types": "remote | hybrid | on-site 배열",
            "employment_types": "원천이 정규화한 고용 형태 배열",
            "posting_languages": "공고 표시 언어 배열. 지원자 요구 언어와 다릅니다.",
            "required_requirement_terms / preferred_requirement_terms": "필수 hard filter / 우대 정렬 가중치 요건 문자열 배열",
            "required_languages": "지원자에게 실제로 요구된 언어 배열",
            "minimum_salary_floor / maximum_salary_ceiling": "숫자. salary_currency와 salary_period를 반드시 함께 지정",
            "salary_currency / salary_period / salary_basis": "구조화 급여 비교 규격. 통화·주기·기준이 맞는 관측치만 비교",
            "active_only": "true면 활성 공고만 포함. 기본값 true",
            "unknown_policy": "exclude | report | include. 검사 불가값을 불일치로 추정하지 않습니다.",
            "keyword_scope": "title_or_occupation | title_or_description. 기본값은 제목·직종만 검사",
        },
        "최소_예시": {
            "countries": ["KR", "CZ"],
            "job_keywords": ["data engineer"],
            "workplace_types": ["remote", "hybrid"],
            "required_requirement_terms": ["sql"],
            "unknown_policy": "report",
        },
    },
    "company-search": {
        "파일": "기업·기관 검색 프로필 JSON",
        "필수_필드": {
            "countries": "대문자 ISO 국가 코드 배열",
            "job_keywords 또는 의미_필터": "회사명/직무 키워드 또는 아래 의미 필터 중 하나 이상",
        },
        "의미_필터": {
            "ownership_sectors": "소유 부문 배열",
            "legal_forms": "법적 형태 배열",
            "business_activities": "사업 활동 배열",
            "market_statuses": "시장 상태 배열",
            "public_institution_types": "공공기관 유형 배열",
            "entity_categories": "법인/기관 범주 배열",
            "source_operations / providers": "정보 원천 operation/provider 배열",
        },
        "값_규칙": "한 필드 안의 여러 값은 OR, 서로 다른 필드는 AND입니다. ARES·GLEIF·ALIO 등의 taxonomy는 namespace:value를 그대로 써야 하며 같은 표기처럼 보여도 병합하지 않습니다.",
        "선택_필드": {
            "require_resolved_identity": "true면 검증된 법인/기관 연결만 포함. 기본값 true",
            "unknown_policy": "exclude | report | include",
        },
        "최소_예시": {
            "countries": ["KR"],
            "public_institution_types": [
                "ALIO:public_institution_type:public_corporation"
            ],
            "require_resolved_identity": True,
            "unknown_policy": "report",
        },
    },
    "screen": {
        "파일": "스크리너 프로필 JSON과 비교 행 JSON",
        "프로필_필수": {
            "countries / industries / size_buckets": "비교 집단을 정의하는 문자열 배열",
            "metrics": '지표명: 양수 가중치 객체. 예: {"growth": 1, "margin": 1}',
        },
        "프로필_선택": {
            "directions": "지표명: false면 낮을수록 좋음, 그 외에는 높을수록 좋음",
            "as_of": "ISO 날짜/시각. 이 시점 이후 이용 가능했던 값은 제외",
            "minimum_peer_size": "순위화할 최소 동료 수. 기본값 2",
            "comparability_group": "반환된 규격 그룹 ID를 명시해 한 규격만 선택",
        },
        "비교행_핵심": "entity_id, country, industry, size_bucket, 지표값과 unit·period·concept·coverage·available_at이 필요합니다.",
    },
    "timeline": {
        "파일": "시간축 행 JSON",
        "행_핵심": "entity_id, axis(financial|market|macro), series_id, value, available_at과 period_end 또는 observation_date를 넣습니다.",
        "호환_규칙": "unit·currency·frequency·adjustment가 다른 series는 합치지 않고 별도 그룹으로 반환합니다.",
    },
    "valuation": {
        "파일": "가치 시나리오 입력 JSON",
        "필수_근거": "revenue, net_debt, shares와 evidence의 source_url·available_at·unit·currency·period·concept이 필요합니다.",
        "처리": "근거가 부족하면 계산값 대신 unavailable/사전조건을 반환합니다.",
    },
    "ai-event": {
        "파일": "AI 사건 분석 입력 JSON",
        "필수_근거": "asset_returns, benchmark_returns, event_index, event_evidence의 event_date·source_url·available_at을 넣습니다.",
        "인과_조건": "처리군·대조군의 전후 관측치가 없으면 association-only로만 반환합니다.",
    },
}


def korean_command(key: str) -> str:
    """Return the terminal-facing Korean command name for an implementation key."""
    return GUIDES_BY_KEY[key].korean_name


def korean_option(key: str) -> str:
    """Return the terminal-facing Korean spelling for an option key."""
    return KOREAN_OPTIONS[key]


def command_key(value: str) -> str:
    """Resolve either a Korean command name or a legacy English command key."""
    try:
        return COMMAND_KEY_BY_NAME[value]
    except KeyError as error:
        raise ValueError(f"알 수 없는 명령입니다: {value}") from error


def command_epilog(key: str) -> str:
    """Return the per-command Korean method, limits, and directly runnable example."""
    guide = GUIDES_BY_KEY[key]
    lines = [f"방식: {guide.method}"]
    if guide.limitation:
        lines.append(f"제한: {guide.limitation}")
    if guide.example:
        lines.extend(("예시:", f"  {guide.example}"))
    return "\n".join(lines)


def guide_payload(key: str | None = None) -> dict[str, Any]:
    """Return Korean documentation while keeping command keys explicit for automation."""
    guides = (GUIDES_BY_KEY[key],) if key else COMMAND_GUIDES
    commands = []
    for guide in guides:
        item = guide.as_dict()
        if input_contract := INPUT_CONTRACTS.get(guide.key):
            item["입력_파일_형식"] = input_contract
        commands.append(item)
    return {
        "도구": "company-intel",
        "표시_언어": "한국어",
        "공통_원칙": [
            "한글 명령과 옵션이 기본이며, 기존 영문 명령과 옵션은 호환 별칭으로 계속 사용할 수 있습니다.",
            "JSON·CSV 열 이름, provider ID, 상태 enum은 API·재현 계약이므로 영문 machine key를 유지합니다.",
            "채용 검색과 동향 분석은 저장된 snapshot을 읽습니다. 원천-검증만 네트워크 provider 호출을 수행합니다.",
            "구조화되지 않은 급여·요건·법인 형태는 추정하지 않으며 검사 불가 또는 제외 사유로 분리합니다.",
        ],
        "명령": commands,
    }
