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
