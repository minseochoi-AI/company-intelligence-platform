# Implementation plan: B-C03-cil-coverage-plan-r3

Status: `contract-ready`

## B-C03-cil-coverage-S01: 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: src/company&#95;intel/connectors/collectors.py; allowlist URL·entity/date/page·read-only collector와 원문 provenance; arbitrary URL/SSRF·키 노출·무한 pagination 금지 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | CREATE | src/company&#95;intel/connectors/collectors.py | B-D03<br>B-D03-O01<br>B-D03-O02 | CollectionSpec<br>collect&#95;evidence | file-change-2199b175807c | — |
| 기존 파일의 목적별 소비 경로 결손 | 적용 경계: src/company&#95;intel/connectors/keyed.py; 기존 probe 기본 의미 유지; 동적 FRED series id와 BEA 관측/catalog 분리; DART 직원 공시 typed 정규화 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | MODIFY | src/company&#95;intel/connectors/keyed.py | B-D03<br>B-D03-O01<br>B-D03-O02 | &#95;fred<br>&#95;bea<br>keyed&#95;probes<br>normalize&#95;employee&#95;disclosure | file-change-927a21cab8b8 | — |
| 기존 파일의 목적별 소비 경로 결손 | 적용 경계: src/company&#95;intel/connectors/keyless.py; SEC concept/기간/단위별 전체 필요한 행 및 filing history; Eurostat dimension/category mapping; 기존 표본 probe 유지 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | MODIFY | src/company&#95;intel/connectors/keyless.py | B-D03<br>B-D03-O01<br>B-D03-O02 | keyless&#95;probes<br>normalize&#95;sec&#95;companyfacts<br>normalize&#95;sdmx&#95;observations | file-change-8925cfef251f | — |
| 기존 파일의 목적별 소비 경로 결손 | 적용 경계: src/company&#95;intel/normalization.py; financial concept/account/statement/currency와 직원 공시/공고/거시 observation class 분리; 같은 comparable signature에서만 계산 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | MODIFY | src/company&#95;intel/normalization.py | B-D03<br>B-D03-O01<br>B-D03-O02 | AtomicObservationMapper<br>comparability&#95;signature | file-change-58fda9542e8a | — |
| 기존 파일의 목적별 소비 경로 결손 | 적용 경계: config/providers.json; 신규 수집 4 operation과 기존8증강의 source mapping·권리·키 전제를 별도 등록; IMF 재승격 금지 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | MODIFY | config/providers.json | B-D03<br>B-D03-O01<br>B-D03-O02 | atomic&#95;operations | file-change-e1e3c60c9a87 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: tests/test&#95;parameterized&#95;collection.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | CREATE | tests/test&#95;parameterized&#95;collection.py | B-D03<br>B-D03-O01<br>B-D03-O02 | test&#95;parameterized&#95;collection&#95;contract | file-change-18064dda30b3 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: tests/test&#95;blog&#95;source&#95;mapping.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. | B-C03-cil-coverage-K01 | CREATE | tests/test&#95;blog&#95;source&#95;mapping.py | B-D03<br>B-D03-O01<br>B-D03-O02 | test&#95;blog&#95;source&#95;mapping&#95;contract | file-change-705f2199a5ae | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-2199b175807c | — | — |
| file-change-927a21cab8b8 | sha256:d71e4ba65e252b1eb058f48c6285a1af6d3235fde2bc3ccf1a698f03236b1ff0 | — |
| file-change-8925cfef251f | sha256:891145fac6acfe39a8efac9203507c3c5cf6c690f189282431767dd68d9bef62 | — |
| file-change-58fda9542e8a | sha256:e37bc2ef638d535a4265031cc652403883fe1798bb9d95f11188cfdf369fbaa0 | — |
| file-change-e1e3c60c9a87 | sha256:de72b88a294869582fb6e9febd5c122b20c45afbe4691f371613a44cc59a7116 | — |
| file-change-18064dda30b3 | — | — |
| file-change-705f2199a5ae | — | — |

</details>

### Routed skills

- B-C03-cil-coverage-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C03-cil-coverage-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D03-O01, B-D03-O02, changes=file-change-2199b175807c, file-change-927a21cab8b8, file-change-8925cfef251f, file-change-58fda9542e8a, file-change-e1e3c60c9a87, file-change-18064dda30b3, file-change-705f2199a5ae: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지

