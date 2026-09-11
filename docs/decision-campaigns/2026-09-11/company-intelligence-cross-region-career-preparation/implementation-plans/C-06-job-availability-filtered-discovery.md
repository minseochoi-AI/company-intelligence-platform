# Implementation plan: company-intelligence-cross-region-career-preparation--C-06-job-availability-filtered-discovery--r1

Status: `contract-ready`

## provider-semantic-job-dataframes: 저장된 실제 Greenhouse·Lever·MPM 응답과 체코 MPSV 스키마를 provider별로 해석한 뒤 공통 의미만 정규화하고 국가·직종·연봉·위치·근무형태·언어·기업분류·검증 요건으로 필터링 가능한 DataFrame 묶음을 만든다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-10-job-standardization-service | CREATE | `src/company_intel/job_search.py` | D-10-job-availability-filtered-discovery | JobSearchProfile, normalize_greenhouse_jobs, normalize_lever_jobs, normalize_mpm_jobs, normalize_mpsv_jobs, search_job_dataframes | - | - | 공고·요건·기업·career overlap·제외·source DataFrame을 반환하고 unknown을 하드 필터 일치로 처리하지 않는다. | - |
| D-10-keyless-normalized-fields | MODIFY | `src/company_intel/connectors/keyless.py` | D-10-job-availability-filtered-discovery | _greenhouse, _lever | sha256:380ed972840191094dce0582b2c9717f900a7d4011163ef2b59ddb94917be788 | - | 실제 응답에 존재하는 구조 필드를 의미 변경 없이 보존한다. | - |
| D-10-job-search-api | MODIFY | `src/company_intel/api.py` | D-10-job-availability-filtered-discovery, D-06-peer-screener-ranking, D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | JobSearchRequest, job_search | sha256:59330f230279ba5a5582d9ed7ff06091ebcec03ebc15595da6841eaa64fa976f | - | 파일 기반 provider 레코드와 profile을 받아 표별 schema·행·shortage를 JSON으로 반환한다. | D-10-job-standardization-service |
| D-10-job-search-cli | MODIFY | `src/company_intel/cli.py` | D-10-job-availability-filtered-discovery | job_search_command | sha256:e9442583150c23c8d5248f6a89f7057da861b7b0887e83efcc5629238bed4146 | - | profile과 provider 응답 파일을 받아 JSON·CSV DataFrame 묶음을 생성한다. | D-10-job-standardization-service |
| D-10-export-career-overlap | MODIFY | `src/company_intel/exporting.py` | D-10-job-availability-filtered-discovery | TABLE_HEADERS, render_csv_bundle | sha256:3925b5c93b488278564b346c7673ab4af1d5304b743595c444800725ce9a7806 | - | 정규화 jobs·requirements·career_overlap·exclusions·sources 표를 CSV/XLSX로 보존한다. | D-10-job-standardization-service |
| D-10-pandas-dependency | MODIFY | `pyproject.toml` | D-10-job-availability-filtered-discovery | project.dependencies | sha256:73f4f8e5b814b6e400623583f78ab20abf34e46fdf9525b4e005d255d8f2341b | - | 핵심 런타임에 pandas 2.x를 고정한다. | - |
| D-10-lockfile | MODIFY | `uv.lock` | D-10-job-availability-filtered-discovery | package:pandas | sha256:920aebcf673c1f0dd7bd545969cc95fbc3778f8398fd1ee5d6711e17690af984 | - | 재현 가능한 pandas 의존성 해시가 기록된다. | D-10-pandas-dependency |
| D-10-job-search-test | CREATE | `tests/test_job_search.py` | D-10-job-availability-filtered-discovery | test_provider_semantics_and_filters, test_career_overlap_dataframes | - | - | Greenhouse·Lever·MPM·MPSV fixture로 국가·직종·연봉·위치·근무형태·언어·요건·unknown 규칙을 검증한다. | D-10-job-standardization-service |
| D-10-field-contract-report | MODIFY | `docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.md` | D-10-job-availability-filtered-discovery, D-06-peer-screener-ranking, D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | D-06-D-10 implementation matrix | sha256:491caf69cf4cd7bf586d0059520b096831f7085cf5d656f83605bc71b3915388 | - | provider별 raw→canonical 필드, 병합 금지 의미, 검색 가능성, 실제 샘플 coverage와 cohort 완료도를 기록한다. | - |

### Routed skills

- `c06-career-research` → `company-intelligence-career-research` (IMPLEMENT, required): 실제 provider 응답과 공식 스키마의 의미 경계 확인
- `c06-verify` → `verification-before-completion` (VALIDATE, required): 필터·DataFrame·전체 회귀 검증

### Completion criteria

- `C-06-job-search-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: provider 의미 보존과 모든 명시 필터·overlap DataFrame이 통과한다.
- `C-06-full-regression` [planned] `verification-before-completion` phase=VALIDATE, depends=C-06-job-search-tests: 전체 로컬 suite와 lint가 통과한다.
