# Implementation plan: company-intelligence-cross-region-career-preparation--C-10-current-job-search-execution--r1

Status: `contract-ready`

## current-job-four-state-execution: 선택된 불변 snapshot과 active_as_of에서 국가·공공기관 identity·직종·위치·고용·급여·요건을 검사하고 네 결과군과 분모 chain을 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-cdc940596fb4 | CREATE | `src/company_intel/current_jobs.py` | D-15-current-job-search-result-contract | CurrentJobResult, SearchDenominators, execute_current_job_search, summarize_coverage | - | - | snapshot manifest, active cutoff, normalized profile, result partitions와 provider coverage를 하나의 응답으로 만든다. | - |
| file-change-46da3fcbd9b9 | MODIFY | `src/company_intel/job_search.py` | D-13-public-sector-identity-linkage, D-15-current-job-search-result-contract | normalize_mpm_jobs, normalize_mpsv_jobs, identity_link_status, public_context, search_job_dataframes, evaluate_filter, active_as_of, build_denominators | sha256:dc859e7af8de87c462772b38b8230b076e4e322d3579592ea02fb8955368f808 | - | 공고 raw employer와 canonical entity/link status, public context, legal form, institution type을 분리해 보존한다. | provider returned→normalized→active→strict/unverifiable/no-match/conflict 합계를 보존하고 필터별 reason을 반환한다. | - |
| file-change-019d6886b2c8 | MODIFY | `src/company_intel/search.py` | D-13-public-sector-identity-linkage | evaluate_semantic_filter, identity_link_status, public_sector_filter | sha256:6864c22a25119686b6f8908f5f9c4ce50534099e2dd99336c9b0c5c0ebce7a09 | - | public institution/ownership/legal-form 필터가 linked evidence와 unresolved/conflict 상태를 구분한다. | - |
| file-change-da6bf1177b56 | CREATE | `tests/test_current_jobs.py` | D-15-current-job-search-result-contract | test_denominator_chain, test_active_as_of, test_mpm_missing_fields_are_unverifiable, test_salary_signature_groups | - | - | KR/CZ fixture로 분모 보존, active cutoff, field unavailable, 월/시급 분리를 검증한다. | file-change-cdc940596fb4, file-change-46da3fcbd9b9 |
| file-change-61fffd113df6 | MODIFY | `tests/test_job_search.py` | D-15-current-job-search-result-contract | test_live_snapshot_denominators, test_public_identity_verdict, test_unknown_is_not_no_match | sha256:7e577ff99fe591caf5773c4aeede07286364faa4a3cf0d6c2a675e1a9d2a0050 | - | snapshot lineage와 identity/급여/요건 UNKNOWN이 네 결과군과 합계에 반영되는지 검증한다. | file-change-46da3fcbd9b9 |

### Routed skills

- `c10-job-semantics` → `company-intelligence-career-research` (IMPLEMENT, required): 국가별 채용·급여·요건·공공기관 field 의미를 보존한다.
- `c10-verification` → `verification-before-completion` (VALIDATE, required): 현재 채용 분모와 판정군을 독립 검증한다.

### Completion criteria

- `C-10-current-job-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 현재 채용 검색이 snapshot 기준시각·분모와 네 결과군을 국가별 필드 차이 없이 보존한다.
