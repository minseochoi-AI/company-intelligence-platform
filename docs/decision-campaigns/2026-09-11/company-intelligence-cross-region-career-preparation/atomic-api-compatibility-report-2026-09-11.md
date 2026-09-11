# 원자 API 호환·필드 계약 보고서 — 2026-09-11

## 현재 최종 실행 상태 — 2026-09-11

> 이 절은 아래의 초기 r1 준비·turnover 기록을 대체하는 현재 실행 판정이다. 과거 receipt는 감사 이력으로 보존한다.

| 항목 | 현재 사실 | 검증 근거 |
|---|---|---|
| 캠페인 범위 | 1개 캠페인, 승인 결정 10/10, 구현 cohort 6개(C-01~C-06) | `campaign.json`, r2 context packet·plan |
| 외부 원자 API | 28개 재호출 중 26 `passed`, 2개 비생산 상태 | `company-intel validate --providers all --timeout 30 --retries 1` |
| BEA | HTTP 200이나 provider error `This UserId is not active` | 키는 존재하지만 활성화되지 않았으므로 dataset discovery도 실행 결과상 사용할 수 없다. |
| IMF | HTTP 403 (`Access Denied`) | 기존 Data Mapper 무인증 URL을 `rejected`로 분류했다. 별도 인증된 IMF SDMX 통합 전에는 시나리오 변수로 사용하지 않는다. |
| ALIO+ 기관 | HTTP 200 및 `title`·`apbaTypeNa` 계약 통과 | `apbaId` 빈 값·`apbaNa=null`을 법인 식별자로 오인하지 않고 기관 표시명/유형의 `context_only`로 제한했다. |
| 자동 테스트 | pytest 43/43, Ruff 오류 0, `git diff --check` 오류 0 | 전체 repository-local 실행 |
| CLI 경로 | 9/9 명령 exit 0 | `provider-status`, `job-search`, `company-search`, `screen`, `timeline`, `valuation`, `ai-event`, `explain`, `export` |

실제 반환물 기반 CLI 결과는 `job-search` 90개 공고 중 33개 일치와 CSV 6종, `company-search`의 OpenDART 삼성전자 매칭, `timeline`의 Alpha Vantage IBM 2개 시점, `export`의 CSV 9종·XLSX·manifest 1개다. `valuation`은 검증된 순부채·주식 수가 없어 `unavailable`, `ai-event`는 원시(`raw`) 가격 series여서 `ineligible`을 반환했다. 두 결과는 오류가 아니라 증거 부족/의미 불일치를 통과로 위장하지 않는 정상 gate다. `screen`은 실데이터에 동질 동료군이 아직 없으므로 비교규격이 일치하는 2개 fixture로 ranking 계약을 실행 검증했다.

## 1. 범위와 검증 상태

이 문서는 `company-intelligence-cross-region-career-preparation` 캠페인의 `DISCUSS`·`AMEND_SCOPE`·`APPROVE`·`PREPARE`·repository-local `IMPLEMENT`·`RESUME`/`VALIDATE` 결과를 함께 기록한다. 5개 결정의 권장안 B는 모두 `ACCEPT`로 처분됐고, 3개 cohort의 25개 계획 경로는 구현·수정 후 결과 hash로 결속됐다. 현재 plan의 로컬 pytest 5개와 저장소 전체 pytest 19개는 통과했다. provider 호출·유료 사용·외부 업로드·커밋·푸시는 이번 검증 범위에 포함하지 않았다. 현재 코드의 28개 `Probe`를 **원자 API 작업**으로 센다. 같은 공급자라도 목적·식별자·시간축이 다르면 하나로 합치지 않는다.

### 통제 용어

- `원자 API 작업`(한 가지 사실 유형만 읽고, 다른 작업의 결과를 필요로 하지 않는 최소 호출 단위)
- `호환 계약`(원천 필드와 내부 공통 필드의 의미·시간·식별 경계를 고정하는 규칙)
- `source_record_id`(원천이 부여한 레코드 식별자이며, 내부 법인 ID와 동의어가 아님)
- `identity_resolved`(국가별 법인 식별자와 법인명이 근거로 일치한 상태)
- `aggregate_only`(국가·산업·시장 집계여서 특정 기업의 사실로 귀속할 수 없는 상태)
- `correlation_candidate`(식별자·기간·산업/지역·가용시점이 모두 확인된 분석 후보이며 인과 증거는 아님)

### e 키 재검증 영수증

| 검증 시각(KST) | 원자 작업 | 결과 | 확인 필드 | 해석 |
|---|---|---|---|---|
| 2026-09-11 | `mpm_public_employment_list` | `passed`, HTTP 200 | XML `resultCode` | `MPM_PUBLIC_EMPLOYMENT_API_KEY`는 현재 목록 API에 인증되었다. 목록은 채용 완료 인원이 아니라 공고 스냅샷이다. |

검증은 비밀값과 공고 원문을 출력하지 않고 임시 증거 디렉터리에서 실행했다. 데이터 포털 명세는 `getList`에 `serviceKey`, `Pblanc_ty`, `Instt_se`, `Sort_order`를 요구한다. [인사혁신처 공공취업정보 공식 명세](https://www.data.go.kr/data/15156780/openapi.do)

### 무키 무료 API 전체 재검증 영수증

2026-09-11에 키 없는 18개 작업을 실제 읽기 전용 요청으로 일괄 검증했다. **18/18 통과, 실패 0**이며, 각 작업은 HTTP 200뿐 아니라 아래 괄호 안의 코드상 `required_paths`도 모두 충족했다. 증적은 비밀값·원문을 보고서에 남기지 않도록 임시 디렉터리에만 보관했다.

| 권역·용도 | 통과한 원자 작업(필수 필드) |
|---|---|
| 미국 공시·노동·조달 | `sec_submissions_apple` (`cik`, `name`, 최근 accession), `sec_companyfacts_apple` (`cik`, `entityName`, Assets 값), `bls_total_nonfarm` (`seriesID`, 월별 `value`), `usaspending_contracts` (`Award ID`, `Recipient Name`) |
| 글로벌 법인·기업 활동 | `gleif_apple` (LEI, 법정명), `greenhouse_airtable` (공고 ID·제목·갱신일), `lever_spotify` (공고 ID·제목·생성일), `github_microsoft` (저장소 ID·이름·push 시각), `openalex_microsoft` (성과 ID·발표연도·건수) |
| 체코·EU·다국가 | `ares_czech_company` (IČO·상호·국가), `eurostat_czech_gdp` (차원·관측값), `ecb_usd_eur` (발신자·series), `oecd_cli` (발신자·관측값), `world_bank_gdp` (국가·연도), `cnb_exchange` (통화·환율·적용일), `cnb_czeonia` (금리·거래량·적용일), `ted_czech_notices` (공고 건수·발행번호). `imf_czech_growth`는 2026-09-11 재검증에서 기존 무인증 URL이 WAF 403을 반환해 운영 경로에서 제외한다. |

이는 해당 시점의 **접근성·필드 계약** 검증이지, 장기 무료 쿼터·제공자 약관·특정 기업의 향후 데이터 지속성을 보장한다는 뜻은 아니다. SEC는 계속 실제 연락처가 포함된 `SEC_USER_AGENT`가 필요하다.

## 2. 캠페인 결정·cohort 정확한 개수

| 항목 | 현재 개수 | 상태 | 근거 |
|---|---:|---|---|
| 캠페인 | 1 | `validating`; 3개 cohort의 현재 plan 기준은 모두 통과, 외부 실행은 미수행 | `campaign.json.campaign_id`, `receipts/validation.json` |
| 의사결정 | 5 | 5/5 `accepted` | 각 decision JSON의 `status`, `accepted_decision` |
| 직접 의존 관계 | 4 | 중복 없는 순차 DAG로 잠김 | `scope-lock.json.scope.dependencies` |
| 구현 cohort | 3 | 모두 `validated`; 5/5 blocking criterion 통과 | `campaign.json.implementation_cohorts`, `receipts/validation.json` |
| 구현 계획 | 3 | plan ID/SHA 결속 유지; repository-local 구현·검증 완료 | `campaign.json`, `receipts/authorize-implementation-before-test-turnover-20260911.json` |
| 원자 API 작업 | 28 | 현재 코드 인벤토리 | `build_probes(Settings)` |

| 순서 | 결정 ID | 육하원칙 요약 | 선행 결정 |
|---:|---|---|---|
| 1 | `D-01-source-access-policy` | 누가: 데이터 운영자 / 무엇: 무료·공개 접근 정책 / 어디: 3개 권역 / 언제: 활성화 전 / 왜: 접근·재배포 경계 / 어떻게: 원천별 권한·제한 기록 | 없음 |
| 2 | `D-02-company-capability-taxonomy` | 누가: 기업 레코드 / 무엇: 재무·채용·시장·거시 가용성 / 어디: 기업·국가 연결 / 언제: 수집 시점 기준 / 왜: 분석 부적격을 숨기지 않기 위해 / 어떻게: 독립 capability 필드 | D-01 |
| 3 | `D-03-search-profile-and-discovery` | 누가: 사용자 지정 검색 프로필 / 무엇: 국가·직무·산업 후보 / 어디: 권역별 원천 / 언제: 요청 갱신일 / 왜: 임의 추천 방지 / 어떻게: 명시 필터와 법인 식별 | D-02 |
| 4 | `D-04-career-requirement-verification` | 누가: 공고·공식 자격 원천 / 무엇: required·preferred·unknown 요건 / 어디: 국가별 관할 원천 / 언제: 공고 확인일 / 왜: 자격증 추정 금지 / 어떻게: URL·인용 필드 보존 | D-03 |
| 5 | `D-05-spreadsheet-output-contract` | 누가: 스프레드시트 수신자 / 무엇: 기업·공고·요건·증거·제외 보기 / 어디: 반환 파일 / 언제: 내보내기 시점 / 왜: 가용성과 한계 노출 / 어떻게: 공통 provenance 열 | D-04 |

따라서 현재 정답은 **1개 캠페인, 5개 결정, 3개 cohort**다. 5개 결정은 서로 독립적으로 승인하지만, 실행은 공유 파일과 의미 의존성을 고려해 아래 3개 단위로 묶는다.

### 2.1 5개 결정의 보강 사항과 연결 cohort

| 결정 | 실제 프로그램을 위해 추가·교정한 사항 | 연결 cohort | 검증 초점 |
|---|---|---|---|
| D-01 | 28개 원자 작업, 18 keyless/10 registered-key, ALIO HTTP 제약, MPM 목록 한계, probe와 production adapter 분리, Work24·sec-api.io 재도입 금지를 명시 | C-01 | catalog 28개 일대일, activation gate, 비밀 마스킹 |
| D-02 | 공통 provenance 10필드, 원천별 단위·시간·ID 네임스페이스, 중복 제거 키, public-context-only와 분석 부적격 상태를 추가 | C-01 | identity·기간·단위·가용시점이 불완전한 분석 차단 |
| D-03 | 고정 표본 Probe를 실제 추천으로 쓰지 않는 규칙, SearchProfile 필수 입력, 국가별 shortage·exclusion·결정론적 순위를 추가 | C-02 | missing profile, 익명·만료·정책 제한 후보 제외 |
| D-04 | MPM 목록에는 상세 자격 근거가 없다는 한계, ATS 원문·MPM 상세·체코 MPSV/NSP/NSK의 후속 검증 경계, `requirement_unavailable`을 추가 | C-02 | 원문 없는 자격증 생성 금지, required/preferred 분리 |
| D-05 | CSV 기준/XLSX 파생 계약, 관계형 7개 시트, provider status 부록, export sanitizer와 결정론적 해시를 추가 | C-03 | 외래키·출처·redaction·빈 결과의 limitation 표현 |

### 2.2 cohort 구성과 비판적 검증

| cohort | 포함 결정 | 실행 의존 | 책임 범위 | 비판적 판정 |
|---|---|---|---|---|
| `C-01-source-identity-foundation` | D-01, D-02 | 없음 | source catalog, 원자 필드 계약, identity, capability, 분석 gate, additive schema | 후속 기능이 모두 이 계약을 소비하므로 첫 단위가 맞다. D-01과 D-02를 분리하면 `models.py`·`warehouse.py`·schema 소유권이 충돌한다. |
| `C-02-search-requirement-evidence` | D-03, D-04 | C-01 | SearchProfile, source-aware discovery, 공고 snapshot, requirement evidence, country policy | 검색 후보와 자격요건은 동일 공고·identity·exclusion 경계를 공유하므로 한 cohort 안에서 순차 구현하는 편이 안전하다. |
| `C-03-evidence-export-delivery` | D-05 | C-02 | CSV/XLSX, run manifest, export sanitizer, CLI/API download metadata | 상류 관계키와 제한 상태가 확정된 뒤에만 안정적인 사용자 계약을 만들 수 있으므로 마지막 단위여야 한다. |

대안 비교 결과, 1개 cohort는 실패 범위와 검토 범위가 너무 크고, 결정별 5개 cohort는 공유 파일의 단일 소유권을 깨뜨릴 가능성이 높다. 3개 cohort는 결정 독립성과 실행 소유권을 함께 보존하는 최소 구조다. 다만 **cohort 등록은 구현 가능성을 보장하지 않는다**. 특히 C-02는 한국 상세 공고와 체코 공고·직업 기준의 실제 필드/약관 검증이 끝나지 않으면 `requirement_unavailable`을 반환하는 제한 구현으로만 완료할 수 있다.

### 2.3 hash와 승인 상태

| 계약 | 현재 값 | 의미 |
|---|---|---|
| scope lock SHA-256 | `7999304264b29201eaa9cf2f3966bf6ee7c33d00343e9c4613eeacfbe6f4676a` | 결정 순서 5개, 직접 의존 4개, cohort membership 3개를 고정 |
| 승인된 결정 | 5/5 | 모두 권장안 B `ACCEPT`; 결정별 승인 receipt 생성 |
| Context Packet | 3/3 | 각 cohort에 v2 packet path/SHA-256 결속 완료 |
| implementation plan ID/SHA-256 | 3/3 | compound plan 3개가 `contract-ready`; 아래 표의 실제 값으로 결속 |
| 구현 authorization | false | 결정 승인과 별개이며 현재 코드 변경 권한을 뜻하지 않음 |
| 실행 환경 manifest | 기존 1개, `stale/misaligned` | 저장소 경로는 맞지만 현재 회사정보 API가 아닌 Google/YouTube 계열 설정과 과거 런타임 상태를 담고 있어 cohort 실행 근거로 재사용 금지 |

| cohort | plan ID | plan SHA-256 | Context Packet SHA-256 | 소유 파일 작업 |
|---|---|---|---|---:|
| `C-01-source-identity-foundation` | `company-intelligence-cross-region-career-preparation--C-01-source-identity-foundation--r1` | `c8b5c8c96de5d900195abc2528b9ceb2762a7ecad73c2a475ab5e28148d284b6` | `189f3b5b4bf2149046e5a9253f85b6b79ce1e5b75449b3d80cc249dbbe9fc653` | 12 |
| `C-02-search-requirement-evidence` | `company-intelligence-cross-region-career-preparation--C-02-search-requirement-evidence--r1` | `88b644caebcf290de5296ac93c01638305224e188ca45598ed72ab07634b5daf` | `9cc145df00a1271f07f075a09628f343cbd4db86f9844ae09d3b48db4df76524` | 8 |
| `C-03-evidence-export-delivery` | `company-intelligence-cross-region-career-preparation--C-03-evidence-export-delivery--r1` | `7eced62ade8fb756b22e7e4763fb3f8789403b8b0721fcea4618827911148ffe` | `474b2c80d7f0d5b8087611bd8de3a1012a32d583b859b63ea96da576d2891b35` | 5 |

전역 변경 그래프는 **25개 고유 경로, 중복 소유 0개**다. `sql/duckdb_schema.sql`, `models.py`, `registry.py`, `warehouse.py`, `api.py`, `cli.py`처럼 여러 결정이 기여하는 파일도 한 cohort만 작업 소유자가 되고, 다른 결정의 기여는 해당 operation의 `contribution_refs`에 결정 JSON SHA와 함께 결속된다. C-01 → C-02 → C-03 실행 의존도는 scope lock과 동일하다.

기존 `receipts/execution-environment.json`은 감사 이력으로 보존한다. 이후 `IMPLEMENT` 또는
provider validation 인계 시 현재 저장소의 `uv run --frozen` 경로, `.venv` 존재 여부,
10개 키의 **값이 아닌 존재 여부**, 외부 네트워크 경계, 첫 미완료 criterion만 담은 새
redacted manifest를 별도 immutable receipt로 생성해야 한다.

## 3. 공통 호환 계약 — 중복 없는 최소 내부 속성

아래 논리 계약은 승인·구현되었지만 아직 행동 테스트로 검증되지 않았다. 원천별 추가 필드를 공통 테이블에 무차별 복사하지 않는다.

| 내부 속성 | 의미 | 필수인 원자 작업 | 중복 방지 규칙 |
|---|---|---|---|
| `source_name` | 공급자·작업 ID | 전부 | 공급자명만이 아니라 `probe.id`를 보존한다. |
| `source_record_id` | 공고·공시·계약·관측치·저장소의 원천 ID | 레코드형 작업 | 회사명·제목을 ID로 대체하지 않는다. |
| `entity_external_id` | CIK, DART corp code, LEI, IČO 등 법정/공시 식별자 | 법인 식별·재무 작업 | 국가·식별 체계 접두어를 붙이고, 이름 일치 전에는 내부 ID에 병합하지 않는다. |
| `subject_type` | `company`, `job_posting`, `macro_series`, `procurement`, `activity` 등 | 전부 | 서로 다른 subject type을 한 순위 점수에 합산하지 않는다. |
| `country_code` | ISO 국가 범위 또는 명시적 `aggregate` | 전부 | 집계 국가값을 기업 소재지로 해석하지 않는다. |
| `observation_date` | 사실이 관측된 일자·기간 끝 | 시계열·공고·공시 | `collected_at`과 대체하지 않는다. |
| `available_at` | 사용자가 알 수 있었던 시점 | 공시·빈티지·공고 | point-in-time 분석에서 필수다. |
| `collected_at` | 플랫폼이 API를 읽은 시각 | 전부 | 원천 갱신일과 구별한다. |
| `source_url` | 재검증 가능한 원천 URL | 전부 | 키가 포함된 query string은 마스킹한다. |
| `classification_reason` | `aggregate_only`, `identity_unresolved` 등의 근거 | 전부 | 빈 값으로 두지 않고 제외 사유를 기록한다. |

## 4. 원자 API 인벤토리와 육하원칙형 최소 필드

### 4.1 미국·한국의 공시·거시·공공 원천

| 원자 작업 | 왜/무엇(필요한 필드=의미) | 누가·어디 | 언제 | 어떻게/사용 경계 |
|---|---|---|---|---|
| `fred_federal_funds_rate` | `observations[].date`=관측일, `value`=연방기금금리, `realtime_start`=빈티지 가용일 | 미국 거시 시계열, 기업 아님 | 관측일·빈티지일 | 할인율·거시 통제만. `aggregate_only`. |
| `bea_dataset_catalog` | `DatasetName`=BEA 데이터셋명, `DatasetDescription`=범위 설명 | 미국 거시·산업 통계 카탈로그 | 호출 시점 | 데이터 존재 확인만; 이 호출 자체를 산업 수치로 쓰지 않는다. |
| `opendart_samsung_financials` | `corp_code`=법인 코드, `account_nm`=계정명, `thstrm_amount`=당기 금액, `rcept_no`=접수번호 | 한국 공시 법인 | 보고연도·접수일 | 재무 fact와 공시 증거. 대상 회사·보고기간을 바꿀 수 있으나 계정명만으로 산업 비교하지 않는다. |
| `ecos_korea_base_rate` | `TIME`=관측일, `DATA_VALUE`=기준금리 값, `STAT_CODE`=통계표 | 한국 거시 시계열 | 일별 관측일 | 한국 통화 통제 변수만. 기업 고용·매출 추정 금지. |
| `alioplus_facility` | `facltNa`=시설명, `apbaNa`=기관명, `address`=공개 주소, `cateNaPath`=시설 분류 | 한국 공공기관 시설 | API 수집 시점 | 기관 서비스 존재 신호만. 공개 담당자 연락처는 분석·내보내기 최소화. HTTP form 전송만 지원. |
| `alioplus_event` | `evtNa`=행사명, `apbaNa`=기관명, `evtStDt`/`evtEndDt`=행사 기간, `cateNaPath`=분류 | 한국 공공기관 행사 | 행사 시작·종료일 | 활동 신호만; 채용·재무·직원 수 증거가 아니다. |
| `alioplus_business` | `bsnNa`=사업명, `apbaNa`=기관명, `bsnDsc`=사업 설명, `lifeCycleNa`=생애주기 | 한국 공공기관 사업 | 사업 기간·수집 시점 | 기관의 공개 사업 설명. 계약 수익·실적·고용 결과로 변환하지 않는다. |
| `alioplus_organization` | `title`=응답에 실제 채워진 기관 표시명, `apbaTypeNa`=유형, `adr`=주소, `bsnMstList`=주요 사업. `apbaId`는 빈 값, `apbaNa`는 null일 수 있다. | 한국 공공기관/지점 | 설립일 `estaDt`, 수집 시점 | 문맥 데이터 전용: 기관 표시명·유형으로 공개 사업을 묶되 법인 식별·외부 ID 매칭에는 사용하지 않는다. |
| `mpm_public_employment_list` | `idx`=공고 ID, `title`=공고명, `insttname`=기관명, `type01`/`type02`=기관·공고 유형, `regdate`/`enddate`=등록·마감일 | 국가·지방·공공기관·교육청 공고 | 등록일·마감일 | 공공 채용 스냅샷. 공고별 상세·파일은 `idx`를 키로 별도 호출하며, 공고는 고용 완료가 아니다. |
| `alphavantage_ibm_daily` | `Time Series (Daily)`의 일자, `4. close`=종가, `5. volume`=거래량 | 상장 보안/시장 | 거래일 | 수익률·이벤트 스터디용. 무료 compact 범위를 장기 전수 가격으로 오인하지 않는다. |

### 4.2 미국·세계 법인·공시·채용·조달 원천

| 원자 작업 | 왜/무엇(필요한 필드=의미) | 누가·어디 | 언제 | 어떻게/사용 경계 |
|---|---|---|---|---|
| `sec_submissions_apple` | `cik`=SEC 발행인 ID, `name`=법인명, `filings.recent.accessionNumber`=공시 식별자 | 미국 SEC 발행인 | 공시 접수순 | 공시 인덱스·법인명 매칭. 실제 연락처가 든 `SEC_USER_AGENT` 필요; sec-api.io와 무관. |
| `sec_companyfacts_apple` | `cik`=발행인 ID, `entityName`=명칭, `facts.us-gaap.*.units.*.val`=XBRL 수치 | 미국 SEC 발행인 | 사실 기간·filed 시점 | 재무 fact. concept·단위·기간·filed를 함께 보존하지 않으면 비교 불가. |
| `bls_total_nonfarm` | `seriesID`=BLS 시계열, `data[].period`=월, `value`=비농업 고용 집계 | 미국 노동시장 | 월별 관측일 | 거시 고용 통제만. 특정 기업 채용·인원과 결합 금지. |
| `gleif_apple` | `data[].id`=LEI, `legalName.name`=법정명, `relationships`=관계 링크 | LEI 등록 법인/국가 코드 | LEI 레코드 갱신일 | 국제 법인 식별 보조. LEI 부재는 법인 부재가 아니다. |
| `usaspending_contracts` | `Award ID`=계약 식별자, `Recipient Name`=수령인, `Award Amount`=금액, `Awarding Agency`=발주 기관 | 미국 연방 조달 수령인 | 조회 기간·계약/행위일 | 공공 고객·수요 신호. action date와 계약 사건일을 구분한다. |
| `greenhouse_airtable` | `jobs[].id`=공고 ID, `title`=직무명, `updated_at`=갱신 시각, `departments`=부서 | 특정 Greenhouse 보드 기업 | 발행·갱신일 | 기업별 공고 스냅샷·부서 수요. 보드 token과 삭제된 공고는 별도 발견/이력 필요. |
| `lever_spotify` | `id`=공고 ID, `text`=직무명, `createdAt`=생성 시각, `categories.location`=위치 | 특정 Lever 보드 기업 | 생성일 | 기업별 공고 스냅샷·팀/위치 수요. 실제 채용 완료로 해석하지 않는다. |
| `github_microsoft` | `id`=저장소 ID, `full_name`=조직/저장소, `pushed_at`=마지막 push 시각 | 공개 GitHub 조직 | push 시각 | 엔지니어링 활동 대리 신호. AI 채택 또는 인력 규모의 직접 증거가 아니다. |
| `openalex_microsoft` | `id`=연구성과 ID, `publication_year`=발표연도, `meta.count`=검색 결과 수 | 연구기관 연결 결과 | 발표연도 | 연구 활동 대리 신호. 기업 특허·매출·제품 출시와 동일시하지 않는다. |

### 4.3 체코·EU·다국가 거시·조달 원천

| 원자 작업 | 왜/무엇(필요한 필드=의미) | 누가·어디 | 언제 | 어떻게/사용 경계 |
|---|---|---|---|---|
| `ares_czech_company` | `ico`=체코 사업자 식별자, `obchodniJmeno`=상호, `sidlo.kodStatu`=국가, `czNace`=산업 | 체코 법인 | 레지스트리 수집 시점 | 체코 법인 마스터·산업 매칭. IČO 없는 공고와 자동 병합하지 않는다. |
| `eurostat_czech_gdp` | `id`=차원명, `value`=관측값, `class`=JSON-stat 구조 | EU/체코 GDP 집계 | 기간 차원 | 국가 비교 거시 변수. 기업 재무 fact로 변환 금지. |
| `ecb_usd_eur` | `header.sender.id`=제공기관, `dataSets[].series`=환율 시계열 | EUR/USD 시장 | 일/월 등 시계열 주기 | 환율 통제 변수. 현지 통화 노출은 법인별 근거가 있을 때만 연결한다. |
| `oecd_cli` | `meta.sender.id`=제공기관, `observations`=CLI 관측치 | OECD·EU·체코 선행지수 | 월별 관측기간 | 경기 국면 통제 변수. 기업 단위 결과와 중복 합산하지 않는다. |
| `imf_czech_growth` | 기존 Data Mapper의 `values.NGDP_RPCH.CZE`/`periods` 계약 | IMF 체코 전망/거시 | 전망 기준 기간 | 2026-09-11 실호출은 HTML WAF 403이었다. IMF의 현재 API 안내는 SDMX 2.1/3.0과 포털 인증을 명시하므로 이 무인증 endpoint는 `rejected`로 기록한다. 무료 무인증 시나리오 통제에는 Eurostat·World Bank의 실적 데이터를 대체 사용하되, 전망치로 바꾸지 않는다. |
| `world_bank_gdp` | `countryiso3code`=국가, `date`=연도, `value`=명목 GDP, `total`=검색 총량 | 미국·한국·체코 국가 집계 | 연도 | 국가 규모 통제. 성장률·환율·기업 성과와 중복 대용치로 쓰지 않는다. |
| `cnb_exchange` | `currencyCode`=통화, `rate`=CZK 환율, `validFor`=적용일 | 체코 중앙은행 환율 | 적용일 | CZK 노출 통제. ECB EUR/USD와 다른 통화쌍이므로 동일 series가 아니다. |
| `cnb_czeonia` | `rate`=CZEONIA 금리, `volumeInCZKmio`=거래량, `validFor`=적용일 | 체코 단기금융시장 | 적용일 | 체코 단기금리·할인율 통제. 환율 작업과 중복하지 않는다. |
| `ted_czech_notices` | `publication-number`=공고 ID, `buyer-name`=구매자, `winner-name`=낙찰자, `total-value`=가치 | EU/체코 조달 | 발행일 | 체코 계약 수요·구매자/공급자 근거. 낙찰자와 법인 ID는 별도 검증한다. |

## 5. 중복 제거와 분석 적격성 규칙

1. **기관 정체성**: 한국은 ALIO Plus `apbaId`와 공고 `insttname`을 후보 연결로만 두고, DART corp code·SEC CIK·ARES IČO·GLEIF LEI는 서로 다른 네임스페이스로 보존한다.
2. **채용**: `mpm_public_employment_list`, Greenhouse, Lever만 공고 레코드다. ALIO Plus 행사·사업·시설은 채용 작업으로 변환하지 않는다. BLS는 항상 `aggregate_only`다.
3. **재무**: SEC XBRL과 OpenDART만 현재 구조화 재무 fact 작업이다. 조달 계약·사업 설명·GitHub 활동은 재무 수치의 대체값이 아니다.
4. **거시**: FRED·ECOS·Eurostat·ECB·OECD·IMF·World Bank·CNB는 모두 독립 series다. 국가/단위/빈도/실적 대 전망을 같은 측정값으로 병합하지 않는다.
5. **상관 분석**: `entity_external_id`, `country_code`, 공통 기간, 산업/지역 규칙, `available_at`이 확인된 행만 `correlation_candidate`가 될 수 있다. 그렇더라도 인과 주장은 금지한다.
6. **공개 연락처**: ALIO Plus의 `chrg*`, `email`, `tel` 등은 공공 API에 있어도 검색 순위·개인 프로파일·스프레드시트 기본 열에 사용하지 않는다.

## 6. 원천별 접근·실행 경계

| 범주 | 작업 수 | 접근 방식 | 운영 규칙 |
|---|---:|---|---|
| 무키 공개 | 18 | SEC, BLS, GLEIF, ARES, Eurostat, ECB, OECD, IMF, World Bank, CNB, TED, USAspending, ATS, GitHub, OpenAlex | 캐시·재시도·공정 사용; SEC에는 실제 연락처 User-Agent 필요 |
| 무료 등록 키 | 10 | FRED, BEA, OpenDART, ECOS, ALIO Plus 4개, MPM 공공취업정보, Alpha Vantage | 키는 환경변수만; URL·로그·보고서에 값 기록 금지 |
| 평문 HTTP 제약 | 4 | ALIO Plus 시설·행사·사업·기관 | PDF v1.6이 SSL 미지원으로 명시. 신뢰된 실행 환경에서만 호출하고 개인정보 검색어를 보내지 않는다. |
| 기업 단위 재무 | 2 | SEC Companyfacts, OpenDART | 보고기간·개념·통화·공시 가용시점 보존 |
| 기업 단위 공고 | 3 | MPM, Greenhouse, Lever | 공고 스냅샷이며 채용 완료·인원 증감의 증거가 아님 |
| 거시/시장 통제 | 11 | FRED, ECOS, BLS, Eurostat, ECB, OECD, IMF, World Bank, CNB 2개, Alpha Vantage | 회사 데이터와 혼합 점수화 금지; 빈도·단위별 별도 열. BEA catalog probe는 수치 관측이 아니라 데이터셋 발견용이다. |

## 7. 구현·로컬 검증 산출물과 다음 경계

- 구현 인벤토리: `src/company_intel/connectors/keyed.py`, `src/company_intel/connectors/keyless.py`, `src/company_intel/connectors/registry.py`
- ALIO Plus 필드·HTTP 제약: `docs/알리오 플러스 API 가이드 1.6.pdf`
- 공통 접근 정책: `source-verification-2026-09-11.md`
- 캠페인 잠금 hash: `7999304264b29201eaa9cf2f3966bf6ee7c33d00343e9c4613eeacfbe6f4676a`
- 전역 변경 그래프: `campaign-change-graph.json` (`5c7205e416f417e03668414b461a6d3965ae0a4cfbcbb92c15300099b835340d`)
- 컴포넌트 인벤토리: `component-inventory.json` (`f9bb4f122b05db6f60de95a13fd18e446aafc96e1e36e7998c9f95168b78d2c6`)
- PREPARE 영수증: `receipts/prepare-attempts/ddaacbbd47378bc6c2e71d0259a83463ef63fa09bb9ab686326a59d841d051aa.json`
- 구현 권한 영수증: `receipts/authorize-implementation-before-test-turnover-20260911.json`
- 구현 전 결과 영수증(불변 이력): `receipts/post-implementation-results-before-tests-20260911.json`
- 현재 구현 결과 hash 영수증: `receipts/post-implementation-results-after-repair-20260911.json` (계획 경로 25개)
- 현재 검증 receipt: `receipts/validation.json` (C-01 2개, C-02 2개, C-03 1개 criterion 통과)
- 전체 로컬 suite receipt: `receipts/full-local-pytest-20260911.json` (19 passed)
- 검증 후 환경 manifest: `receipts/execution-environment-after-validation-20260911.json`
- 검증 후 turnover: `reports/execution/7999304264b29201eaa9cf2f3966bf6ee7c33d00343e9c4613eeacfbe6f4676a/db0ce21ded810181de44fcddd1db3fe69de57539.md`

실제 수정은 C-01 분류의 `evidence_complete=false` 경로가 `missing-aligned-series`를 analysis eligibility에 보존하지 않던 결함 1건이었다. 직접 `missing-period-alignment` 판정은 유지하고, 상위 분류 결과에 누락 사유를 추가해 C-01 재검증과 전체 suite를 통과했다. 다음 유효 행동은 별도 권한 하의 실제 provider/API·CLI·DuckDB smoke이며, 특히 MPM 상세와 체코 공공 요건 source는 공식 상세 필드 검증 전까지 `unavailable`/`pending`을 유지한다.

## 8. D-06~D-10 승인·계획 결속과 실제 반환물 재검증

사용자는 2026-09-11 `D-06~D-10 권장안 B APPROVE, 로컬 구현`을 명시했다. 다섯 결정은 모두 `ACCEPT`이고 다음 세 compound plan에 중복 경로 없이 결속됐다.

| Cohort | 결정 | Plan SHA-256 | Context Packet SHA-256 | 로컬 구현 범위 |
|---|---|---|---|---|
| C-04 | D-06 | `ad5501d7d4b1ef82a720135929c5330f165aeb0604d961e063e8bad8d21333be` | `ce908e71de977fc2555d220b15da5ecabf49d670548cabb0ed684841324c598e` | 국가×산업×규모 동료군 스크리너, 지표 방향·coverage·최소 동료 수·제외 |
| C-05 | D-07~D-09 | `367805654026b42a923be38b5084c4591a638fe484b5dfa10ed9cdb197c7c193` | `21791a585a678e722759f6f0e7df9edaeef30b12971f3f301b735a937d901239` | point-in-time 시간축, 근거 제한 DCF, AI 사건/DiD 적격성 |
| C-06 | D-10 및 통합 경계 | `daba7054b70c72723918ad0ef32c919ba49c02b3549e411921661158812a1f5f` | `3237d00339605484bc53b5b8b8099d930e9085d6ca98d83ba3d23999a0fde0ba` | provider별 공고 정규화, 하드필터, pandas DataFrame 6종, API·CLI·export |

승인 receipt는 `receipts/authorize-D-06-through-D-10-local-implementation-20260911.json`이다. 외부 지원·메시지·커밋·푸시는 승인 범위가 아니며 실행하지 않는다.

새 샘플을 만들지 않고 저장된 실제 2026-09-11 반환물을 읽었다.

| Provider/산출물 | 실제 관측 | 필드 coverage | 비판적 판정 |
|---|---:|---|---|
| Greenhouse Airtable | HTTP 200, 16공고, 수집 `05:40:09Z`, raw SHA `ffc7ef…ed53` | `id/title/location/language/department/office/first_published/updated_at/content` | 16건 모두 구조화 `pay_input_ranges`와 deadline이 없었다. 본문의 지역별 OTE 구간은 단일 base salary가 아니므로 자동 숫자 병합 금지. |
| Lever Spotify | HTTP 200, 74공고, 수집 `05:40:12Z`, raw SHA `b24029…2c59` | `id/text/country/categories/workplaceType/createdAt/descriptions/lists` | 국가·근무형태·commitment는 구조화됐다. 이 표본의 `salaryRange`는 0건이며 posting language는 보통 없다. |
| MPM 공공취업 목록 | HTTP 200, `resultCode` 통과, 전체 `58,349`, 요청 표본 1건, 수집 `05:34:49Z`, raw SHA `f3a738…1614` | `idx/title/insttname/type01/type02/regdate/enddate` | 표본은 2008년 마감 공고였다. 단순 HTTP 200은 현재 공고 증거가 아니며 `enddate < collected_at`이면 active에서 제외한다. 상세 endpoint를 확인하기 전 위치·급여·자격요건은 unavailable이다. |
| 체코 MPSV 공개구인 스키마 | 공식 JSON Schema 확인 | `portalId`, `datumVlozeni/Zmeny`, `expirace`, `mesicniMzdaOd/Do`, `typMzdy`, `mistoVykonuPrace`, 고용주 `ico/nazev`, `profeseCzIsco`, 근로관계, 교육·언어·기술 | 실제 전체 JSON snapshot은 아직 저장 검증되지 않았다. 스키마 기반 adapter는 제공하되 운영 source 상태는 snapshot 호출 전 `candidate/needs-live-validation`이다. 연락처 PII는 의도적으로 삭제한다. |

## 9. 검색 규격의 원자 필드 계약

### 9.1 DataFrame 여섯 종류

| DataFrame | 행 단위 | 주요 키 | 사용자 판단 |
|---|---|---|---|
| `companies` | 검색에 남은 회사×국가 | `entity_id/company_name/country_code` | 국가별 회사와 일치 공고 수 비교 |
| `jobs` | provider 공고 snapshot | `provider/job_id/snapshot_at` | 직종·위치·근무형태·연봉·고용형태 필터 결과 |
| `requirements` | 공고의 원자 요건 | `provider/job_id/requirement_id` | skill/language/education/experience/credential와 required/preferred 구분 |
| `career_overlap` | 정규화 요건 하나 | `requirement_kind/normalized_key` | 공고·회사·국가 간 겹치는 요건과 prevalence |
| `exclusions` | 공고×실패 조건 하나 | `provider/job_id/field/reason` | 어떤 unknown/불일치 때문에 빠졌는지 확인 |
| `sources` | provider snapshot 하나 | `provider/snapshot_at` | 수집 시각·범위·제한·원천 확인 |

### 9.2 합칠 수 있는 의미와 합치면 안 되는 의미

| 검색 개념 | 공통 canonical 속성 | Provider raw 매핑 | 병합/필터 규칙 |
|---|---|---|---|
| 공고 정체성 | `provider + job_id` | GH `id`, Lever `id`, MPM `idx`, MPSV `portalId/id` | provider namespace 없이 ID만 합치지 않는다. |
| 회사 | `entity_id/company_name` | GH `company_name`, Lever hosted URL의 board slug, MPM `insttname`, MPSV `zamestnavatel.ico/nazev` | board slug는 법정명·법인 ID가 아니다. MPSV IČO만 ARES 연결 후보가 된다. |
| 국가 | `country_code` | Lever `country`, MPSV=`CZ`, MPM=`KR`, GH location/office의 명시 국가 힌트 | structured ISO를 우선한다. 텍스트 힌트는 notes에 남기고 모호하면 unknown이다. |
| 직종 | `occupation_label/code/system` | MPSV `profeseCzIsco.id`, 나머지 `title/text` | CZ-ISCO 코드와 자유 제목은 동일 코드로 추정하지 않는다. 제목은 keyword 검색만 가능하다. |
| 위치 | `location_raw/city/region` | GH `location/offices`, Lever `categories.location/allLocations`, MPSV `mistoVykonuPrace` | 검색용 raw text는 가능하나 행정구역 코드는 codebook 없이 이름으로 변환하지 않는다. |
| 근무형태 | `workplace_type` | Lever `workplaceType`; GH 위치의 명시 `remote/hybrid`; MPM/MPSV 미확인 | `remote/hybrid/on-site/unknown`. unknown은 하드필터를 통과하지 못한다. |
| 고용형태 | `employment_type + raw` | Lever `categories.commitment`, MPSV `pracovnePravniVztahy`; GH/MPM 미확인 | raw를 보존하고 확실한 표현만 full-time/part-time/contract/internship으로 변환한다. |
| 공고언어 | `posting_language` | GH `language`, MPSV=`cs`, MPM=`ko`, Lever 대부분 없음 | 공고 언어와 요구 외국어를 같은 열에 넣지 않는다. |
| 요구언어 | requirement `kind=language` | MPSV `pozadovanaJazykovaZnalost`; ATS 공고의 명시 문장 | provider 구조 필드 또는 명시 문장만 사용한다. |
| 급여 | `min/max/currency/period/basis` | Lever `salaryRange`; GH 단일 structured pay range만; MPSV `mesicniMzdaOd/Do + typMzdy` | 통화와 period가 정확히 같을 때만 비교한다. FX·연환산·gross/net·base/OTE를 추정하지 않는다. |
| 기업분류 | `company_type/industry_raw` | MPM=public-sector source, MPSV `statniSpravaSamosprava`; ARES `czNace` 등 별도 company source | 공고 source만으로 상장/비상장·산업을 만들지 않는다. unknown은 필터 불일치다. |
| 요건 필요도 | `necessity` | MPSV `pozadovana*`=required; ATS의 `must/required/you have`와 `preferred/nice/might` | responsibility 문장을 필수 자격으로 승격하지 않는다. 불명확하면 unknown이며 hard match에 쓰지 않는다. |
| 현재 공고 | `is_active` | live ATS list, GH deadline, MPM `enddate`, MPSV `expirace` | 수집일 기준 마감일이 지났으면 제외한다. 공고 존재는 채용 완료가 아니다. |

### 9.3 실제 필터 의미

하드필터는 `countries`, `job_keywords/occupations`, `locations`, `workplace_types`, `employment_types`, `languages`, `industries`, `company_types`, `minimum_salary_floor`, `maximum_salary_ceiling`, `salary_currency`, `salary_period`, `required_requirement_terms`, `active_only`다. 값이 없으면 “제약 없음”이고, 사용자가 값을 지정했는데 provider 값이 unknown이면 불일치다. `preferred_requirement_terms`는 제외가 아니라 정렬용 hit 수다. 국가별 `country_allocation`은 부족분을 `country_shortages`로 반환한다.

급여 floor는 공고의 하한이 사용자의 하한 이상일 때만 통과한다. 예를 들어 USD/year와 CZK/month는 숫자가 같아도 비교하지 않는다. Greenhouse 본문에 지역별 base/OTE 구간이 여러 개이면 어느 위치·보상 basis인지 분리되기 전까지 salary hard filter에서 제외한다.

## 10. 기능 목적 10개와 현재 달성 상태

| # | 기능 목적 | 코드 경로 | 테스트 상태 | 실제 데이터 상태 / 남은 제한 |
|---:|---|---|---|---|
| 1 | 미국·한국·체코 국가별 분리 | `job_search.py` canonical country·shortage | 통과 | US ATS 실제 있음. KR MPM 실제 응답은 있으나 저장 표본은 만료. CZ는 공식 스키마 adapter만 있고 실제 snapshot 미수집. |
| 2 | 기업별 데이터 가용성·분석부적격 분류 | 기존 classification/source catalog | 기존 suite 통과 | 원천 coverage에 따라 unavailable 유지. |
| 3 | 실제 공개 채용공고 확인 | ATS/MPM/MPSV normalizer + active gate | 통과 | 저장 실제 ATS 90건은 확인 가능. MPM 현재성 query 개선과 MPSV 실제 수집이 필요. |
| 4 | 국가·직무·산업·조건 필터 | `JobSearchProfile` hard filters | 통과 | 산업·기업유형은 ATS만으로 대개 unknown이라 별도 company source join 필요. |
| 5 | 필수·우대 자격/준비사항 확인·필터 | atomic requirements + `career_overlap` | 통과 | ATS는 명시 텍스트, MPSV는 구조 필드. MPM 상세 미검증은 unavailable. 자격증 법적 동등성은 판단하지 않음. |
| 6 | CSV/XLSX 근거 export | 기존 export + overlap 표, CLI 6 CSV | 통과 | CLI actual smoke로 6개 CSV 생성. |
| 7 | 동료군 기업 스크리너 | `screening.py` | 통과 | 실제 다기업 재무 fact가 충분해야 순위가 성립. 최소 표본 미달은 제외. |
| 8 | 회사 시간축·시장·거시 비교 | `analysis_service.build_company_timeline` | 통과 | point-in-time 필터는 동작. 실제 동일 회사의 세 축 적재 coverage가 필요. |
| 9 | 근거·가정·신뢰도 미래가치 시나리오 | `evaluate_valuation_scenarios` | 통과 | source/time/unit/currency가 없으면 unavailable. 투자 조언이 아님. |
| 10 | AI 사건 후 채용·수익성 변화 검증 | `evaluate_ai_event` | 통과 | event source·benchmark·충분한 기간·control이 필요. 기본 결과는 association-only이며 인과 확정하지 않음. |

로컬 실제 산출물 smoke는 저장된 세 provider의 91공고를 읽어 `engineer` 검색을 수행했다. 국가 범위를 US/GB/SE/CZ/KR로 두었을 때 49공고가 남았고, 42건이 필터에서 제외됐으며(한 공고가 여러 제외 사유를 가질 수 있음), US·GB·SE는 allocation을 충족하고 CZ·KR은 각각 1건 부족으로 반환됐다. 이 결과는 Airtable·Spotify라는 두 ATS board와 MPM 1행 표본의 범위이며 시장 전체 채용 universe가 아니다.

같은 저장 응답에 `remote + full-time + USD/year 하한 100,000` 하드필터를 적용한 별도 smoke 결과는 **0건**이다. 이것은 필터 결함이 아니라 이번 실제 ATS 응답 90건에 구조화 급여가 0건이라는 정확한 제한 결과다. 본문에서 숫자를 긁어 임의 연봉으로 승격하지 않았음을 검증한다.

## 11. CLI r2 구현 규칙

현재 CLI는 `provider-status`, `company-search`, `job-search`, `screen`, `timeline`, `valuation`, `ai-event`, `explain`, `export`를 제공한다. 저장 응답 기반 검색에서 `Permanent`는 기간 표현일 뿐 근무시간을 보장하지 않아 `full-time` 필터에 자동 합치지 않는다. 공고 표기 언어와 지원자 요구 언어는 각각 `posting_language`와 requirement `kind=language`로 분리한다.

비교·정렬은 country, industry, size bucket, currency, period, unit, concept, vintage, coverage의 comparability signature가 일치할 때만 허용한다. GitHub/OpenAlex는 proxy, ALIO Plus는 context, MPM 목록은 metadata-only로 처리한다. 결과 내보내기에는 `exclusions`, `unverifiable`, `conflicts`를 분리해 0건의 원인을 감사할 수 있게 한다.
