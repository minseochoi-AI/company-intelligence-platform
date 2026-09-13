# Implementation plan: company-intelligence-cross-region-career-preparation--C-06-job-availability-filtered-discovery--r3

Status: `contract-ready`

## interactive-cli-and-job-verdicts-r3: 9개 scriptable CLI를 유지하면서, 저장된 API snapshot의 실제 facet을 화살표/공백/Enter로 선택하고 strict/unverifiable/no-match/conflict를 분리하는 대화형 offline workflow를 제공한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-10-job-search-verdicts-r3 | MODIFY | `src/company_intel/job_search.py` | D-10-job-availability-filtered-discovery | JobSearchProfile, JobDataFrames, normalize_greenhouse_jobs, normalize_lever_jobs, normalize_mpm_jobs, search_job_dataframes | sha256:57f7bc4b0114afa46c4410fce2b813835598ab756bb8f0e76fe5bfddd5c7873b | - | posting/requirement language, business unit, all locations, salary signature, field verdict와 strict/unverifiable/no-match/conflict/locations tables를 제공한다. | - |
| D-10-interactive-module-r3 | CREATE | `src/company_intel/interactive.py` | D-10-job-availability-filtered-discovery | ArrowMenu, InteractiveWorkflow, ScriptedSelector, build_interactive_request | - | - | 표준 curses 기반 arrow/space/Enter selector와 non-TTY scripted adapter로 provider-status, discovery, comparison, analysis, explain, export menu를 구성한다. | D-10-job-search-verdicts-r3 |
| D-10-cli-interactive-routing-r3 | MODIFY | `src/company_intel/cli.py` | D-10-job-availability-filtered-discovery | main, interactive_command, job_search_command, company_search_command, explain_command, export_command | sha256:c0c60ee83f9a392ec12e9aafa54820f4cfa143b5c12296549fc7dc60cdcb870b | - | company-intel interactive가 saved data path에서 facet menu를 표시하고 profile/run manifest preview 또는 선택한 command 실행을 안전하게 라우팅한다. | D-10-interactive-module-r3 |
| D-10-api-profile-parity-r3 | MODIFY | `src/company_intel/api.py` | D-10-job-availability-filtered-discovery | JobSearchRequest, SearchProfileRequest, job_search, company_search | sha256:c19c8f6d8e5b46bab987858d0d8c45fbcb2d4187d0fe29c6225725a599bd27e9 | - | CLI와 API가 같은 semantic profile, verdict tables, facet/run metadata를 사용한다. | D-10-job-search-verdicts-r3 |
| D-10-job-search-tests-r3 | MODIFY | `tests/test_job_search.py` | D-10-job-availability-filtered-discovery | test_unknown_policy, test_salary_ceiling_signature, test_lever_all_locations, test_job_verdict_tables | sha256:ef561f7b4158abc71c5d5afd0db129cf38401718d3d0fa11ebff713702a7b31e | - | offline fixture로 이질 salary, Permanent, language, business unit, unknown policy와 5상태 table을 검증한다. | D-10-job-search-verdicts-r3 |
| D-10-cli-workflow-tests-r3 | MODIFY | `tests/test_cli_workflows.py` | D-10-job-availability-filtered-discovery | test_interactive_scripted_preview, test_non_tty_guidance, test_cli_profile_parity | sha256:6b5c6589f6af5df8a09577d0c65ce2680d83d0be118e6af25310d80cc6f96ebd | - | scripted selector로 profile preview, facet disabled reason, non-TTY guidance, command parity를 offline으로 검증한다. | D-10-cli-interactive-routing-r3 |
| D-10-interactive-tests-r3 | CREATE | `tests/test_interactive.py` | D-10-job-availability-filtered-discovery | test_arrow_menu_scripted_selection, test_disabled_facet_is_explained | - | - | arrow/space/Enter selection model, disabled options, multi-select와 profile compiler를 offline으로 검증한다. | D-10-interactive-module-r3 |
| D-10-cli-docs-r3 | MODIFY | `README.md` | D-10-job-availability-filtered-discovery | Interactive CLI, facet semantics, offline data boundary | sha256:efa322ccb86fda2536d3fd761bb6c34f686fcd077530a9d714da104de449f4f4 | - | interactive command, arrow/space/Enter control, saved snapshot boundary, 5상태 결과와 feature menu를 문서화한다. | D-10-cli-interactive-routing-r3 |
| D-10-korean-status-docs-r3 | MODIFY | `IMPLEMENTATION_REPORT_KO.md` | D-10-job-availability-filtered-discovery | 대화형 CLI 상태, 검증 경계 | sha256:4824331f9afffb289cedc407b10d378341f2936c075a37a3a949105330c9badf | - | interactive 기능의 구현 상태, offline snapshot 제한, 테스트 전/후 상태를 명시한다. | D-10-cli-interactive-routing-r3 |
| D-10-api-compatibility-report-r3 | MODIFY | `docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.md` | D-10-job-availability-filtered-discovery | CLI facet field contract, provider-native classification | sha256:8e3adf82a00db9a31d29cf67899e7824ee9f3982943d2a9a289379dceb99adf4 | - | CLI facet, filter/sort/display-only/forbidden classification, public/private axes, provider handling을 implementation contract로 남긴다. | D-10-cli-interactive-routing-r3 |

### Routed skills

- `cli-implementation` → `cli-creator` (IMPLEMENT, required): composable scriptable/interactive CLI를 구현한다.
- `job-semantics` → `company-intelligence-career-research` (IMPLEMENT, required): 채용 조건과 provider field meaning을 보존한다.
- `cli-tests` → `tdd` (VALIDATE, required): offline CLI/UI tests를 실행한다.

### Completion criteria

- `C06-r3-interactive-and-job-tests` [planned] `tdd` phase=VALIDATE, depends=-: interactive selector, profile compiler, job verdict tables와 API parity가 offline으로 동작한다.
