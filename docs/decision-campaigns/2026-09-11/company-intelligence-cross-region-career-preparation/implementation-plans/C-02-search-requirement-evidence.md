# Implementation plan: company-intelligence-cross-region-career-preparation--C-02-search-requirement-evidence--r1

Status: `contract-ready`

## profile-search-and-requirement-evidence: 명시적 SearchProfile로 미국·한국·체코 후보를 찾고, 회사/공고 identity·capability와 검증된 자격요건 근거를 결합해 설명 가능한 결과를 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-019d6886b2c8 | CREATE | `src/company_intel/search.py` | D-03-search-profile-and-discovery | validate_search_profile, build_company_universe, rank_candidates, explain_candidate | - | - | 필수 profile 검증, 국가별 source-aware universe, capability filter, 결정론적 순위와 exclusion reason을 제공한다. | - |
| file-change-ef3ea7e59ee6 | CREATE | `src/company_intel/career_requirements.py` | D-04-career-requirement-verification | extract_job_requirements, normalize_requirement, verify_requirement, resolve_country_baseline | - | - | required/preferred, job evidence, country baseline, crosswalk, unavailable을 분리하고 source locator를 보존한다. | - |
| file-change-927a21cab8b8 | MODIFY | `src/company_intel/connectors/keyed.py` | D-03-search-profile-and-discovery, D-04-career-requirement-verification | keyed_discovery_adapters, probe_contract, mpm_employment_detail, alio_context_adapter | sha256:52f808405b8ffb802b7f4c6673e46a8c3b35349a376e9ad39ed2daa975b0b66d | - | sample probe와 허용된 company/job discovery 호출 계약을 분리하고 pagination/as_of를 노출한다. | MPM 상세가 실제 제공하는 필드만 구조화하고 ALIO a-d는 기관 맥락으로만 연결한다. | - |
| file-change-8925cfef251f | MODIFY | `src/company_intel/connectors/keyless.py` | D-03-search-profile-and-discovery, D-04-career-requirement-verification | keyless_discovery_adapters, ats_board_policy, ats_job_detail, czech_public_requirement_sources | sha256:4d1a72cd8ddedf8af10719f50c7bc1ca52d57dacb32fe73f5a5927c01abef008 | - | 법인/공시/ATS source의 discovery 범위와 고정 표본 여부를 명시하고 허용된 pagination만 노출한다. | 허용된 ATS 상세와 체코 MPSV/NSP/NSK의 실제 공개 필드가 확인된 경우에만 evidence adapter로 연결한다. | - |
| file-change-71ee7f968ed8 | MODIFY | `src/company_intel/api.py` | D-02-company-capability-taxonomy, D-03-search-profile-and-discovery, D-04-career-requirement-verification, D-05-spreadsheet-output-contract | get_company_capabilities, get_field_availability, get_analysis_exclusions, search_companies, SearchProfileRequest, CandidateResponse, get_career_requirements, RequirementEvidenceResponse, create_export_job, get_export_status, get_export_metadata | sha256:5bcc8cf61419cc3c880d03399787e5ff8497db8349ada8828330b340d10e8607 | - | 기업 ID와 as_of 기준 capability, 필드 가용성, 근거 locator, correlation/causal exclusion을 조회한다. | 검증된 profile로 국가별 후보, 근거, match/exclusion 이유, 부족분을 반환한다. | required/preferred, evidence scope, verification status, source link, unavailable reason을 반환한다. | snapshot-bound export 요청, 상태, 형식, 파일 hash와 만료 metadata를 제공한다. | - |
| file-change-e633c98e50e6 | MODIFY | `src/company_intel/cli.py` | D-03-search-profile-and-discovery, D-05-spreadsheet-output-contract | search_command, load_search_profile, export_command, validate_output_path | sha256:842594207e87d0d06bb9417bc11514d6f3f2415ac3a5cf60224196aaa4ee6e01 | - | JSON profile 입력, dry-run validation, snapshot 검색, machine-readable output 명령을 제공한다. | profile/snapshot/run ID를 받아 안전한 output directory에 versioned bundle을 만든다. | - |
| file-change-bde11e1b67fd | CREATE | `tests/test_search_profile.py` | D-03-search-profile-and-discovery | test_profile_validation, test_country_allocation_and_exclusions, test_deterministic_ranking | - | - | 필수 입력, 국가별 부족분, 익명 공고, identity 불확실성, 결정론적 순위를 fixture로 검증한다. | - |
| file-change-70da2ae09abe | CREATE | `tests/test_career_requirements.py` | D-04-career-requirement-verification | test_required_vs_preferred, test_requirement_unavailable, test_country_baseline_scope, test_stale_job | - | - | required/preferred, 상세 필드 부재, 국가 기준, stale/limited source를 fixture로 검증한다. | - |

### Routed skills

- `c02-tdd` → `tdd` (IMPLEMENT, required): 검색·요건 동작을 fixture로 먼저 고정
- `c02-research` → `company-intelligence-career-research` (IMPLEMENT, conditional): 새 체코/한국/미국 원천을 코드에 등록할 때 공식 필드와 이용조건 확인
- `c02-verify` → `verification-before-completion` (VALIDATE, required): 계획 해시와 독립 테스트 결과 확인

### Completion criteria

- `C-02-search-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: SearchProfile 검증과 근거 기반 후보 순위가 결정론적으로 통과한다.
- `C-02-requirement-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=C-02-search-tests: 공고·국가 baseline 요건의 evidence level과 unavailable 상태가 통과한다.
