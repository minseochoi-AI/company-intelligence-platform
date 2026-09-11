# Implementation plan: company-intelligence-cross-region-career-preparation--C-06-job-availability-filtered-discovery--r2

Status: `contract-ready`

## cli-semantic-search-orchestration-r2: 로컬 CLI가 source 상태 확인, 저장 payload/warehouse 입력, 원자 profile 검색, 검사불가 설명, 기업 스크리너·시간축·가치·사건 분석과 CSV/XLSX export를 동일 run manifest로 실행한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-10-job-search-r2 | MODIFY | `src/company_intel/job_search.py` | D-10-job-availability-filtered-discovery | JobSearchProfile, JobDataFrames, normalize_greenhouse_jobs, normalize_lever_jobs, normalize_mpm_jobs, normalize_mpsv_jobs, search_job_dataframes | sha256:183851a950d90c7ffdf878c28f4473fd01da4b55fce7571c5d818827a0f688f1 | - | 원자 profile v2와 provider별 다중 행을 사용해 strict_matches, unverifiable_candidates, no_matches, conflicts, jobs, locations, requirements, overlap, sources를 반환한다. | - |
| D-10-cli-r2 | MODIFY | `src/company_intel/cli.py` | D-10-job-availability-filtered-discovery | main, provider_status_command, job_search_command, company_search_command, screen_command, timeline_command, valuation_command, ai_event_command, explain_command, export_command | sha256:813b84089d9e56df133827020313e5dd292ac49d509d00927930cf17a2f68b92 | - | company-intel provider-status|job-search|company-search|screen|timeline|valuation|ai-event|explain|export 명령을 profile/run manifest 중심으로 구성하고 strict와 unverifiable을 별도 파일·exit status로 반환한다. | - |
| D-10-api-r2 | MODIFY | `src/company_intel/api.py` | D-10-job-availability-filtered-discovery | JobSearchRequest, job_search, company_search, company_screener, evidence_timeline, valuation_scenarios, ai_event_analysis | sha256:d697d6621f6f4e12a5b5cd3f250ff5a4a27594dc00ff92fc9751f9c4b389c27c | - | CLI와 동일 domain service/schema를 사용하고 strict/unverifiable/conflict, source disposition, warnings와 run metadata를 반환한다. | - |
| D-10-job-tests-r2 | MODIFY | `tests/test_job_search.py` | D-10-job-availability-filtered-discovery | test_title_vs_description, test_lever_multi_location, test_permanent_not_full_time, test_posting_vs_required_language, test_salary_comparability, test_unknown_results, test_provider_semantic_fixtures | sha256:a91c48396d95fc34bfad10b18f2a10702bc67ff3dbe158e7b90ccdbc5def1f6d | - | 저장된 실제 응답에서 축약한 비밀·PII 없는 fixture로 14개 false-title, 다중위치, Permanent, unknown bullet, pay tier와 hourly/month code를 검증한다. | - |
| D-10-cli-tests-r2 | CREATE | `tests/test_cli_workflows.py` | D-10-job-availability-filtered-discovery | test_job_search_workflow, test_unverifiable_exit_contract, test_screen_and_export_workflow, test_cli_api_profile_parity | - | - | 임시 DB·profile·provider fixture로 모든 CLI 기능의 출력 파일, run manifest, exit code, schema와 v2 API parity를 검증한다. | - |
| D-10-provider-fixture-r2 | CREATE | `tests/fixtures/provider_semantic_cases.json` | D-10-job-availability-filtered-discovery | greenhouse, lever, mpm_public_employment, mpsv_cz, macro_contract_cases | - | - | 다중 위치, optional salary, unknown requirement, expired posting, codebook ID, body error와 truncated-array 회귀를 최소 레코드로 보존한다. | - |
| D-10-readme-r2 | MODIFY | `README.md` | D-10-job-availability-filtered-discovery | CLI workflows, profile schema v2, result interpretation | sha256:e3de7435521711060166b3c49b30b046cbcb6b2a762cf6b051ab775775dce84f | - | 초기화→source 상태→ingest→profile 검색→explain→screen/analysis→export 순서와 예제 profile, exit code, 데이터 한계를 문서화한다. | - |
| D-10-implementation-report-r2 | MODIFY | `IMPLEMENTATION_REPORT_KO.md` | D-10-job-availability-filtered-discovery | 기능 상태표, CLI 계약, 미검증 경계 | sha256:f77bb79b9d5c1313211ae6d28c936b458afa1fc8d00800287c1efa2d11ebf136 | - | 기능별 implemented, semantically-verified, data-covered, provider-live-verified 상태를 분리하고 CLI 명령과 남은 외부 검증을 표시한다. | - |
| D-10-atomic-report-r2 | MODIFY | `docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.md` | D-10-job-availability-filtered-discovery | CLI semantic contract, provider disposition matrix, cohort r2 turnover | sha256:a46732f0ba183b51890d00f9808862fe54f3f9ee409ba96e8f03f5ea7cae18f0 | - | 29개 source 후보의 유지·격리·폐기, 공통/특수/금지 필드, 검사불가 조합, r2 CLI 명령과 cohort 검증기준을 기록한다. | - |

### Routed skills

- `c06-r2-tdd` → `tdd` (IMPLEMENT, required): 실제형 provider fixture와 CLI end-to-end를 red-green-refactor로 구현
- `c06-r2-research` → `company-intelligence-career-research` (IMPLEMENT, required): 채용·요건·회사 분석 경계를 유지
- `c06-r2-verify` → `verification-before-completion` (VALIDATE, required): job search와 전체 CLI workflow 독립 검증

### Completion criteria

- `C-06-r2-job-semantic-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 제목/본문, 다중위치, remote scope, 계약차원, 언어차원, 급여 비교, requirement necessity와 5상태 결과가 실제형 fixture에서 통과한다.
- `C-06-r2-cli-workflow-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=C-06-r2-job-semantic-tests: 저장 provider payload에서 검색·설명·스크리너·분석·export까지 CLI가 동일 profile/run lineage와 결정론적 결과를 만든다.
