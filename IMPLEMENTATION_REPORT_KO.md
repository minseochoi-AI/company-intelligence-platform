# 기업 인텔리전스 플랫폼 로컬 구현·실행 보고서

## 최종 상태

2026-08-20 KST 기준으로 별도 Git 프로젝트를 생성하고, 요청한 9개 구현 영역을 로컬에서 실제 실행했다.

- 통합 API 프로브: **24개**
- 통과: **22개**
- 외부 API 재호출: **26/28 통과**
- BEA: HTTP 200이지만 `This UserId is not active` 공급자 오류
- IMF 기존 Data Mapper: HTTP 403이므로 운영 경로에서 `rejected`
- 국내 공공 채용 원천: 현재 ALIO Plus·인사혁신처 공공취업정보로 대체됨
- 결과물 내 제공 키 누출 검사: **0건**
- 테스트: **43/43 통과**
- FastAPI 실제 기동: `/health`, `/analysis/future-score`, `/analysis/dcf` 모두 HTTP 200
- DuckDB 실제 적재: 성공
- Docker/K3s: 파일 구현 및 YAML 파싱 통과. 이 로컬 샌드박스에는 Docker CLI가 없어 이미지 빌드는 미실행

## 요청 사항별 구현 결과

| 번호 | 요청 | 구현 결과 |
|---:|---|---|
| 1 | 별도 Git 프로젝트 | `company_intelligence_platform` 독립 저장소와 `main` 브랜치 생성 |
| 2 | 키 기반 커넥터 | FRED, BEA, OpenDART, ECOS, ALIO Plus, 인사혁신처 공공취업정보, Alpha Vantage 구현 |
| 3 | 무키 커넥터 | SEC, BLS, GLEIF, ARES, Eurostat, ECB, OECD, IMF, World Bank, CNB, TED, USAspending, Greenhouse, Lever, GitHub, OpenAlex 구현 |
| 4 | 원문·정규화·오류·쿼터 로그 | `artifacts/raw`, `normalized`, `logs`, SHA-256, 재시도 횟수, HTTP 메타데이터, 키 마스킹 구현 |
| 5 | 시계열 DB | DuckDB DDL·적재기 및 PostgreSQL 호환 DDL 구현 |
| 6 | 기업 분석 | 현금흐름, 마진, 성장률, 부채·유동성, 인당 생산성, 산업/국가/규모 동료군 순위 구현 |
| 7 | AI 사건 검증·미래가치 | 이벤트 스터디, DiD, 거시 민감도 회귀, 3개 DCF 시나리오, 신뢰도 포함 미래가치 점수 구현 |
| 8 | 배포 | Dockerfile, Docker Compose, K3s Deployment·Service·PVC·CronJob·Secret 예시 구현 |
| 9 | 실호출 검증 JSON | `validation_results.json`, `field_catalog.json`, `plan_alignment.json`, `warehouse_validation.json` 생성 |

## 키 기반 API 실제 결과

| 공급자 | 실제 판정 | 확인 내용 |
|---|---|---|
| FRED | 통과 | FEDFUNDS 12개 월별 관측치. 최신 표본 2026-07, 3.63% |
| BEA | 공급자 오류 | 키 형식은 전달됐으나 BEA가 비활성 UserID라고 응답. 이메일 활성화 후 재실행 필요 |
| OpenDART | 통과 | 삼성전자 2025 연결 연차 재무 229행, status `000` |
| ECOS | 통과 | 한국은행 기준금리 368개 일별 관측치. 최신 표본 2026-08-17, 2.75% |
| 국내 공공 채용 원천 | 대체됨 | ALIO Plus·인사혁신처 공공취업정보의 현재 검증 결과를 별도 운영 기록으로 관리 |
| ALIO Plus 기관 | 통과·문맥 전용 | 실제 응답의 `apbaId` 빈 값과 `apbaNa=null`을 확인했다. `title`/`apbaTypeNa`만 기관 표시명·유형으로 사용하며 법인 식별에는 사용하지 않는다. |
| IMF Data Mapper | 폐기 | 실호출 HTTP 403. 무인증 운영 source로 사용하지 않으며, IMF SDMX 인증 연동을 별도로 검증하기 전 시나리오 변수에 넣지 않는다. |
| Alpha Vantage | 통과 | IBM 일별 OHLCV 100행. 최신 표본 2026-08-19 종가 237.16 USD |

공식 문서 기준 요청 형식은 [FRED series observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html), [BEA API User Guide](https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf), [OpenDART 전체 재무제표](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020), [ECOS Open API](https://ecos.bok.or.kr/api/), [Alpha Vantage documentation](https://www.alphavantage.co/documentation/)을 사용했다.

## 무키 API 실제 결과

다음 18개 프로브는 모두 HTTP·파싱·필수 필드 검증을 통과했다.

- SEC Submissions 및 Companyfacts
- BLS 무등록 고용 API
- GLEIF LEI 법인정보
- 체코 ARES 사업자정보
- Eurostat 체코 GDP 성장률
- ECB USD/EUR
- OECD CLI SDMX 2.0
- IMF 체코 GDP 성장 전망
- World Bank 미국·한국·체코 GDP
- CNB 환율 및 CZEONIA
- TED 체코 공공조달
- USAspending 미국 계약
- Greenhouse Airtable 채용공고
- Lever Spotify 채용공고
- GitHub Microsoft 조직 활동
- OpenAlex Microsoft 기관 연구성과

OECD는 첫 요청에서 Cloudflare가 기본 Python 브라우저 서명을 차단했으나, 정당한 식별 User-Agent를 추가하자 정상 응답했다. 우회는 사용하지 않았다. 응답 스키마도 기존 `header/dataSets`가 아니라 `meta/data.dataSets`인 SDMX 2.0 구조임을 실제 응답으로 교정했다.

## 실제 기업 분석 표본

OpenDART의 삼성전자 2025 연결 연차 자료에서 다음을 계산했다.

| 지표 | 값 |
|---|---:|
| 매출 | 333,605,938,000,000 KRW |
| 전년 대비 매출 성장률 | 10.88% |
| 영업이익률 | 13.07% |
| 순이익률 | 13.55% |
| CFO 마진 | 25.57% |
| 추정 FCF | 37,792,969,000,000 KRW |
| FCF 마진 | 11.33% |
| CFO/순이익 | 1.887 |
| 유동비율 | 2.328 |
| CAPEX/매출 | 14.25% |

성장성과 수익성 두 항목만 사용한 예비 부분점수는 64.74지만 데이터 신뢰도는 0.20으로 표시했다. 시장가치·산업 동료군·인력·지배구조가 없는 상태이므로 이 값은 목표 가격이나 완성된 미래가치가 아니다.

채용은 첫 로컬 snapshot에서 Airtable 16건, Spotify 97건을 저장했다. 첫 관측만 있으므로 증감률은 의도적으로 `null`이며 다음 CronJob snapshot부터 변화량을 계산할 수 있다. 이는 실제 채용 완료 인원이 아니라 공개 공고 수요다.

## DuckDB 적재 검증

| 테이블 | 실제 행 수 |
|---|---:|
| `entity` | 4 |
| `evidence` | 23 |
| `financial_fact` | 229 |
| `macro_observation` | 380 |
| `market_price` | 100 |
| `job_posting_snapshot` | 113 |
| `api_call_log` | 23 |

빈 테이블도 의도적으로 생성했다. `filing`, `workforce_fact`, `company_event`, `score_run`은 향후 공시·사건·스코어 실행 때 채워진다.

모든 시계열은 최소한 `period_end/observation_date`, `available_at`, `revision_at`, `collected_at`을 분리할 수 있도록 설계했다. 과거 분석에는 공시·통계가 실제 이용 가능해진 시각 이후의 값만 결합해야 한다.

## 실행 명령

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
chmod 600 .env
# .env에 키와 실제 SEC 연락처 입력

company-intel validate --providers all
company-intel init-db
company-intel ingest-evidence
company-intel ingest-normalized
company-intel analyze-actual
company-intel demo-analytics
company-intel serve --host 0.0.0.0 --port 8000
```

Docker Compose 수동 수집:

```bash
docker compose --profile collector run --rm collector
docker compose up -d api
```

K3s에서는 `secret.example.yaml`을 복사해 실제 Secret을 별도 생성하고 Git에는 올리지 않는다. 이미지 경로 `ghcr.io/replace-me/...`도 실제 레지스트리로 바꿔야 한다.

## 남은 외부 조치

1. BEA 가입 이메일의 활성화 링크를 완료한 뒤 `company-intel validate --providers bea` 재실행
2. ALIO Plus·인사혁신처 공공취업정보 키를 각각 설정한 뒤 `company-intel validate --providers alioplus,mpm_public_employment`를 재실행
3. `SEC_USER_AGENT`를 실제 앱명과 연락 이메일로 교체
4. 두 번째 채용 snapshot부터 기업별 공고 증감·부서 mix 변화 계산
5. 실제 AI 도입 사건은 회사 공식 공시 URL·사건일·노출점수를 `company_event`에 적재한 뒤 이벤트 스터디와 DiD 실행
6. 전체 산업 순위는 여러 기업을 수집한 후 `country × industry × size_bucket` 내부에서만 산출

## CLI r2 의미 계약

- `provider-status`는 접근 가능성과 생산 검색 가능성을 같은 상태로 표시하지 않는다.
- `job-search`는 `match`, `no_match`, `unknown`, `conflict`, `not_applicable` 의미를 보존한다.
- `screen`은 국가·산업·규모뿐 아니라 통화·기간·단위·개념·vintage·coverage가 같은 그룹만 순위화한다.
- `export`는 불일치, 검증불가, 충돌 행을 서로 다른 CSV/XLSX 표로 반환한다.

## 보안 메모

실제 키는 코드, Git, 배포 예시, 결과 JSON에 저장하지 않았다. BEA처럼 응답 본문에 키를 반사할 수 있는 공급자는 마스킹 전 본문의 SHA-256만 기록하고 저장 원문에서는 값을 제거한다. 사용자가 채팅에 직접 공개한 키는 작업 완료 후 재발급하는 것이 안전하다.
