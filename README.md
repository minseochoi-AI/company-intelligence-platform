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
company-intel init-db
company-intel validate --providers all
company-intel demo-analytics
uvicorn company_intel.api:app --host 0.0.0.0 --port 8000
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

## 증거 우선 CLI

`provider-status`, `company-search`, `job-search`, `screen`, `timeline`, `valuation`, `ai-event`, `explain`, `export` 명령을 제공한다. `job-search`는 기본적으로 직종 제목·직종코드만 키워드 검사에 사용한다. 설명문 키워드까지 검사하려면 profile에 `"keyword_scope": "title_or_description"`를 명시한다.

필터 결과의 `0건`은 조건 불일치와 데이터 미확인을 구분한다. 급여는 통화·지급주기·요청한 basis가 모두 같을 때만 비교하며, `Permanent`는 `full-time`으로 추정하지 않는다. 공고 표시 언어도 지원자 요구 언어와 별도 필드다.

## 대화형 CLI: 저장된 증거에서 조건 고르기

기존의 9개 scriptable 명령은 유지한다. 저장된 JSON snapshot이 있을 때는 다음 명령으로 화살표 키로 기능과 조건을 고를 수 있다.

```bash
company-intel interactive --data-dir artifacts --output artifacts/interactive
```

`↑/↓`로 이동하고, 복수 선택은 `Space`, 확정은 `Enter`를 쓴다. 자유 텍스트인 직무·회사명은 직접 입력한다. 대화형 CLI는 데이터 준비(`provider-status`), 채용·기업 탐색(`job-search`, `company-search`), 기업 비교(`screen`), 시간축·분석(`timeline`, `valuation`, `ai-event`), 증거 전달(`explain`, `export`) 순으로 세부 기능을 고른 뒤 기존 명령행 인수와 JSON profile로 컴파일한다.

선택지는 저장된 관측에 존재하는 값만 보이고, 각 항목은 건수·provider coverage·filterability를 함께 표시한다. `display-only`, `unavailable`, `forbidden`인 값은 선택할 수 없다. 회사의 소유 부문, 공공기관 유형, 법적 형태, 산업, 시장 상태와 ATS의 department/team은 별도 축이다. 서로 다른 API의 raw code를 이름만으로 병합하지 않는다.

채용 탐색은 국가, 제목/직종, 다중 위치, 근무 방식, 고용 형태, 공고 표시 언어, ATS 조직 단위, 필수·우대 요건, 지원자 요구 언어, 국가별 결과 상한, 검사 불가 처리 방식을 차례로 고른다. 구조화 급여가 있는 snapshot에만 `통화/기간/basis` 선택과 최소·최대 값 입력이 열린다. 본문 OTE, 환율 변환, 연환산은 만들지 않는다. 실행하면 기존 CSV 표와 함께 redacted `run-manifest.json`을 남겨 선택한 profile, facet, 원천 범위, strict/불일치/검증불가/충돌 건수를 다시 설명할 수 있다.

회사·공공기관 탐색의 법적 형태·산업·기관 유형 선택값은 `namespace:value`로 저장된다. 예를 들어 ARES 법적 형태는 GLEIF 법적 형태와 같은 문자열처럼 보이더라도 별도 선택값이다. 법인 식별이 확인되지 않은 후보를 보일지는 명시적으로 선택하며, 기본값은 확인된 법인만 포함하는 것이다.

비대화형 환경에서는 재현 가능한 JSON answer file을 쓴다. `--dry-run`은 실제 명령을 실행하지 않고 생성될 profile과 argv만 출력한다.

```bash
company-intel interactive --data-dir artifacts --output artifacts/interactive \
  --script answers.json --dry-run
```

대화형 경로는 저장된 로컬 artifact만 읽는다. provider refresh, 패키지 설치, 지원 제출은 수행하지 않는다.
