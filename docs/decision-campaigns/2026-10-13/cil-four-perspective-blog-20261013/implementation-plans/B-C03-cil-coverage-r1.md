# Implementation plan: B-C03-cil-coverage-plan-r1

Status: `contract-ready`

## B-C03-cil-coverage-S01: 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다.

### Changes

| ID | Operation | Path | Decisions | Obligations | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| file-change-2199b175807c | CREATE | `src/company_intel/connectors/collectors.py` | B-D03 | B-D03-O01, B-D03-O02 | CollectionSpec, collect_evidence | - | - | 적용 경계: src/company_intel/connectors/collectors.py; allowlist URL·entity/date/page·read-only collector와 원문 provenance; arbitrary URL/SSRF·키 노출·무한 pagination 금지 | - |
| file-change-927a21cab8b8 | MODIFY | `src/company_intel/connectors/keyed.py` | B-D03 | B-D03-O01, B-D03-O02 | _fred, _bea, keyed_probes, normalize_employee_disclosure | sha256:a23b1ba496c6cd2fff4a27e2b502a08a48c5161298a58a9b13e6306131166d36 | - | 적용 경계: src/company_intel/connectors/keyed.py; 기존 probe 기본 의미 유지; 동적 FRED series id와 BEA 관측/catalog 분리; DART 직원 공시 typed 정규화 | - |
| file-change-8925cfef251f | MODIFY | `src/company_intel/connectors/keyless.py` | B-D03 | B-D03-O01, B-D03-O02 | keyless_probes, normalize_sec_companyfacts, normalize_sdmx_observations | sha256:749eb418824d2fd9922893fe677dac630db68d5cd04250f386faba80a4a35e71 | - | 적용 경계: src/company_intel/connectors/keyless.py; SEC concept/기간/단위별 전체 필요한 행 및 filing history; Eurostat dimension/category mapping; 기존 표본 probe 유지 | - |
| file-change-58fda9542e8a | MODIFY | `src/company_intel/normalization.py` | B-D03 | B-D03-O01, B-D03-O02 | AtomicObservationMapper, comparability_signature | sha256:e37bc2ef638d535a4265031cc652403883fe1798bb9d95f11188cfdf369fbaa0 | - | 적용 경계: src/company_intel/normalization.py; financial concept/account/statement/currency와 직원 공시/공고/거시 observation class 분리; 같은 comparable signature에서만 계산 | - |
| file-change-e633c98e50e6 | MODIFY | `src/company_intel/cli.py` | B-D03 | B-D03-O01, B-D03-O02 | main | sha256:92efaf5991ad2c27d677968f3dafc853f0ca17714c14b1b3c3674b7834235a1f | - | 적용 경계: src/company_intel/cli.py; 새 앱 CLI는 보고서 inspect/collect/compose/render/evaluate/link/preview/sync/reconcile/metrics의 typed 입출력; 기존 CIL CLI에는 allowlisted collect만 추가 | - |
| file-change-e1e3c60c9a87 | MODIFY | `config/providers.json` | B-D03 | B-D03-O01, B-D03-O02 | atomic_operations | sha256:eda18ca82e832c07426425671a29b56b90875654444a7fa06d588d32cb5b7a74 | - | 적용 경계: config/providers.json; 신규 수집 4 operation과 기존8증강의 source mapping·권리·키 전제를 별도 등록; IMF 재승격 금지 | - |
| file-change-18064dda30b3 | CREATE | `tests/test_parameterized_collection.py` | B-D03 | B-D03-O01, B-D03-O02 | test_parameterized_collection_contract | - | - | 적용 경계: tests/test_parameterized_collection.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | - |
| file-change-705f2199a5ae | CREATE | `tests/test_blog_source_mapping.py` | B-D03 | B-D03-O01, B-D03-O02 | test_blog_source_mapping_contract | - | - | 적용 경계: tests/test_blog_source_mapping.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | - |

### Routed skills

- `B-C03-cil-coverage-review` → `decision-campaign-workbook` (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C03-cil-coverage-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D03-O01, B-D03-O02, changes=file-change-2199b175807c, file-change-927a21cab8b8, file-change-8925cfef251f, file-change-58fda9542e8a, file-change-e633c98e50e6, file-change-e1e3c60c9a87, file-change-18064dda30b3, file-change-705f2199a5ae: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지

