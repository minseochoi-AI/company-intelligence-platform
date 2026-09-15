# Company Intelligence Platform

미국·한국·EU·체코의 공식 공시, 거시, 시장가격, 채용, 조달, 법인관계 자료를 동일한 시간 구조로 저장하고 기업·산업 순위, 거시 민감도, AI 도입 사건 전후 검증과 미래가치 시나리오를 계산하는 로컬 우선 MVP입니다.

## 핵심 원칙

- 비밀키는 환경변수에만 두며 Git·결과 JSON·요청 로그에 남기지 않습니다.
- 모든 호출은 원문 보존본, 정규화 JSON, 오류 로그, 쿼터 로그, 응답 SHA-256을 생성합니다.
- API가 키를 응답에 반사하는 경우 원문 파일은 키를 마스킹하고 마스킹 전 본문의 SHA-256만 보존합니다.
- `period_end`, `available_at`, `collected_at`, `revision_at`을 분리해 미래정보 누출을 방지합니다.
- 미래가치는 예언값 하나가 아니라 침체·기준·낙관 시나리오와 데이터 신뢰도를 함께 냅니다.

## 빠른 실행

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
chmod 600 .env
# .env에 키와 실제 SEC 연락처를 입력
company-intel 저장소-초기화
company-intel 원천-검증 --공급자 all
company-intel 분석-예시
company-intel API-서버 --호스트 0.0.0.0 --포트 8000
```

검증 결과는 기본적으로 `artifacts/validation_results.json`, 원문은 `artifacts/raw/`, 정규화 결과는 `artifacts/normalized/`, 호출·오류·쿼터 기록은 `artifacts/logs/*.jsonl`에 저장됩니다.

## 구현 범위

- 키 필요: FRED, BEA, OpenDART, ECOS, ALIO Plus(시설·행사·사업·기관), 인사혁신처 공공취업정보, Alpha Vantage
- 무키: SEC, BLS, GLEIF, ARES, Eurostat, ECB, OECD, World Bank, CNB, TED, USAspending, Greenhouse, Lever, GitHub, OpenAlex
- 저장: DuckDB 기본, PostgreSQL DDL 제공
- 분석: 재무비율, 현금흐름/마진, 산업·국가·규모 그룹 순위, 거시 민감도, 채용공고 변화, 이벤트 스터디, DiD, DCF 시나리오, 미래가치 점수
- 제공: CLI, FastAPI, Docker Compose, K3s API Deployment 및 CronJob

## 중요한 한계

- ALIO Plus는 가이드 v1.6에 따라 HTTP form 요청만 지원하며, 인사혁신처 공공취업정보는 data.go.kr 서비스키의 활용신청 권한이 필요합니다.
- IMF의 기존 Data Mapper 무인증 URL은 2026-09-11 재호출에서 HTTP 403을 반환했습니다. `imf_czech_growth`는 운영 경로에서 `rejected`이며, 별도 인증된 IMF SDMX 연동 전에는 전망 변수로 사용하지 않습니다.
- Alpha Vantage 무료키는 공식 안내상 일반적으로 하루 25회이므로 대량 전수 수집용이 아닙니다.
- 공개자료만으로 실제 채용 완료 인원, 퇴직률, 부서별 손익, 설비 OEE를 확정할 수 없습니다.
- 이 프로젝트는 투자 권유가 아니며 점수와 DCF는 입력 가정에 따른 연구용 분석입니다.

## 한국어 증거 우선 CLI

CLI의 기본 표시는 한국어다. 모든 한글 명령·옵션은 바로 실행할 수 있고, 기존 영문 명령·옵션은 이미 저장한 자동화 스크립트를 깨지 않도록 호환 별칭으로 남아 있다. 전체 명령, JSON 입력 형식, 제한, 예시는 다음에서 확인한다.

```bash
company-intel 사용-안내
company-intel 채용-검색 --도움말
company-intel 사용-안내 --명령 현재-채용
```

| 목적 | 한글 명령 | 기존 영문 호환 명령 |
| --- | --- | --- |
| 원천 확인·저장소 적재 | `원천-상태`, `원천-검증`, `저장소-초기화`, `근거-적재`, `정규화-적재` | `provider-status`, `validate`, `init-db`, `ingest-evidence`, `ingest-normalized` |
| 기업·공공기관 탐색 | `기본-기업-검색`, `기업-기관-검색` | `search`, `company-search` |
| 저장 채용 검색·동향 | `채용-검색`, `현재-채용`, `채용-동향`, `스냅샷-상태` | `job-search`, `current-jobs`, `job-trends`, `snapshot-status` |
| 비교·분석 | `기업-비교`, `기업-시간축`, `가치-시나리오`, `AI-사건-분석` | `screen`, `timeline`, `valuation`, `ai-event` |
| 근거 전달·재현 | `근거-설명`, `증거-내보내기`, `선택-재현`, `대화형-선택` | `explain`, `export`, `replay`, `interactive` |
| API 서버 | `API-서버` | `serve` |

JSON·CSV의 열 이름, provider ID, 상태 enum은 API·재현 계약이므로 영문 machine key를 유지한다. 한글 도움말은 이 키의 의미와 입력값을 설명하며, 원본 API의 taxonomy 코드나 값 자체를 임의 번역·통합하지 않는다.

`채용-검색`은 기본적으로 직종 제목·직종코드만 키워드 검사에 사용한다. 설명문 키워드까지 검사하려면 프로필에 `"keyword_scope": "title_or_description"`를 명시한다.

필터 결과의 `0건`은 조건 불일치와 데이터 미확인을 구분한다. 급여는 통화·지급주기·요청한 basis가 모두 같을 때만 비교하며, `Permanent`는 `full-time`으로 추정하지 않는다. 공고 표시 언어도 지원자 요구 언어와 별도 필드다.

## 대화형 CLI: 저장된 증거에서 조건 고르기

기존의 9개 scriptable 명령은 유지한다. 저장된 JSON snapshot이 있을 때는 다음 명령으로 화살표 키로 기능과 조건을 고를 수 있다.

```bash
company-intel 대화형-선택 --데이터-경로 artifacts --출력 artifacts/interactive
```

`↑/↓`로 이동하고, 복수 선택은 `Space`, 확정은 `Enter`를 쓴다. 자유 텍스트인 직무·회사명은 직접 입력한다. 대화형 CLI는 데이터 준비(`원천-상태`), 채용·기업 탐색(`채용-검색`, `기업-기관-검색`), 기업 비교(`기업-비교`), 시간축·분석(`기업-시간축`, `가치-시나리오`, `AI-사건-분석`), 증거 전달(`근거-설명`, `증거-내보내기`) 순으로 세부 기능을 고른 뒤 한글 명령행 인수와 JSON 프로필로 컴파일한다.

선택지는 저장된 관측에 존재하는 값만 보이고, 각 항목은 건수·provider coverage·filterability를 함께 표시한다. `display-only`, `unavailable`, `forbidden`인 값은 선택할 수 없다. 회사의 소유 부문, 공공기관 유형, 법적 형태, 산업, 시장 상태와 ATS의 department/team은 별도 축이다. 서로 다른 API의 raw code를 이름만으로 병합하지 않는다.

채용 탐색은 국가, 제목/직종, 다중 위치, 근무 방식, 고용 형태, 공고 표시 언어, ATS 조직 단위, 필수·우대 요건, 지원자 요구 언어, 국가별 결과 상한, 검사 불가 처리 방식을 차례로 고른다. 구조화 급여가 있는 snapshot에만 `통화/기간/basis` 선택과 최소·최대 값 입력이 열린다. 본문 OTE, 환율 변환, 연환산은 만들지 않는다. 실행하면 기존 CSV 표와 함께 redacted `run-manifest.json`을 남겨 선택한 profile, facet, 원천 범위, strict/불일치/검증불가/충돌 건수를 다시 설명할 수 있다.

회사·공공기관 탐색의 법적 형태·산업·기관 유형 선택값은 `namespace:value`로 저장된다. 예를 들어 ARES 법적 형태는 GLEIF 법적 형태와 같은 문자열처럼 보이더라도 별도 선택값이다. 법인 식별이 확인되지 않은 후보를 보일지는 명시적으로 선택하며, 기본값은 확인된 법인만 포함하는 것이다.

비대화형 환경에서는 재현 가능한 JSON answer file을 쓴다. `--dry-run`은 실제 명령을 실행하지 않고 생성될 profile과 argv만 출력한다.

```bash
company-intel 대화형-선택 --데이터-경로 artifacts --출력 artifacts/interactive \
  --선택-스크립트 answers.json --미리보기
```

대화형 경로는 저장된 로컬 artifact만 읽는다. provider refresh, 패키지 설치, 지원 제출은 수행하지 않는다.

## Snapshot 기반 현재 채용·동향 분리

`current-jobs`는 한 번 저장한 provider payload와 `snapshot_id`를 기준으로 현재 공고를 판정한다. 반환값에는 `provider_returned → normalized → active → strict_match / unverifiable / no_match / conflict` 분모 사슬이 포함된다. 따라서 한국 MPM 목록처럼 근무지·급여·요건이 없는 원천은 불일치로 위장하지 않고 `unverifiable`로 남는다.

```bash
company-intel 현재-채용 --프로필 profile.json \
  --원천-응답 mpm_public_employment=artifacts/mpm.json \
  --원천-응답 mpsv_cz=artifacts/mpsv.json \
  --스냅샷-ID snapshot-example --출력 artifacts/current-jobs
```

`job-trends`는 두 개 이상이며 provider·정규화·taxonomy·coverage signature가 같은 저장 snapshot에만 동향을 계산한다. 공고 증감은 광고된 수요의 변화일 뿐 실제 채용 인원이나 인과 효과가 아니다.

```bash
company-intel 채용-동향 --스냅샷 artifacts/snapshot-1.json \
  --스냅샷 artifacts/snapshot-2.json --지표 active_postings
```

공공부문은 세 축을 분리한다. MPM의 공공 채용 원천 맥락과 MPSV의 공공행정 flag는 공고 맥락이고, ALIO 기관 유형·ARES 법적 형태·소유 부문은 검증된 entity link가 있을 때만 별도 필터가 된다. 기관명 일치는 `candidate`일 뿐 자동 법인 연결이 아니다. `replay`는 저장한 선택 manifest의 hash chain만 확인하며 provider를 새로 호출하지 않는다.
