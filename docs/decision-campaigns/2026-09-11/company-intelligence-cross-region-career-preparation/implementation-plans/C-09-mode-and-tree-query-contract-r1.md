# Implementation plan: company-intelligence-cross-region-career-preparation--C-09-mode-and-tree-query-contract--r1

Status: `contract-ready`

## purpose-mode-progressive-facet-tree: 데이터 상태·현재 채용·채용 동향·기업기관 분석·결과 전달의 목적 트리에서 상위 선택으로 남은 snapshot 행만 사용해 다음 facet 값·count·coverage와 disabled reason을 재계산한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-a2dce4728cf0 | CREATE | `src/company_intel/category_tree.py` | D-14-progressive-facet-tree-navigation | PurposeNode, SelectionSession, FacetBranch, advance_selection, backtrack_selection, preview_selection | - | - | 5개 목적 root와 동적 branch, count, coverage, invalidation을 순수 함수 state machine으로 제공한다. | - |
| file-change-3db064398654 | MODIFY | `src/company_intel/interactive.py` | D-12-current-search-trend-mode-separation, D-14-progressive-facet-tree-navigation | build_interactive_request, select_purpose, select_current_job_mode, select_trend_mode, ArrowMenu, render_branch, apply_selection, backtrack, render_preview | sha256:1195b3136a5e06d2376cacfbfe0657ea9bd3beabc8ce631f59515ff857f5e585 | - | 최상위 목적에서 current_job과 job_trend를 분리하고 mode별 필수 조건과 eligibility를 표시한다. | 각 단계의 option count·coverage·disabled reason을 갱신하고 backtracking과 실행 전 preview를 제공한다. | file-change-a2dce4728cf0 |
| file-change-79c10e85533c | MODIFY | `src/company_intel/facets.py` | D-13-public-sector-identity-linkage, D-14-progressive-facet-tree-navigation | taxonomy_facet_options, identity_link_status, public_context, facet_options_for_selection, facet_count, facet_coverage, invalid_selection | sha256:72fd3f3707d831672b9a08eeef0e2cbaf6f99b6b7b500d6ba6c102f5bbe8a611 | - | 공공 맥락, public institution type, legal form, ownership과 link status를 독립 facet으로 제공한다. | 선택된 후보 집합에서 고유값·행 수·provider coverage를 계산하고 0건 강제 선택을 invalid_selection으로 판정한다. | - |
| file-change-884e869a1a0f | MODIFY | `src/company_intel/query_contract.py` | D-12-current-search-trend-mode-separation, D-14-progressive-facet-tree-navigation, D-15-current-job-search-result-contract, D-16-job-trend-series-analysis-contract | QueryMode, CurrentJobQuery, JobTrendQuery, parse_query_profile, SelectionProfile, normalize_tree_selection, validate_facet_selection, CurrentResultContract, DenominatorContract, VerdictPolicy, TrendMetric, TrendComparison, TrendEligibility | sha256:0efef6245a0de8e7fa33c75a1ea561946159a9cd6e85fe99ec15a22c37470d1a | - | current_job과 job_trend의 서로 다른 필수 시각·기간·지표·comparison 입력을 typed contract로 정의한다. | ordered selection과 normalized flat profile, snapshot_id, 선택 근거를 함께 표현한다. | current 결과가 provider returned·normalized·active·partition counts와 active_as_of를 요구한다. | new/active/closed/openings/salary/requirement metrics와 비교 기준 및 insufficient history를 typed하게 정의한다. | - |
| file-change-d3aed88ac6ff | CREATE | `tests/test_category_tree.py` | D-14-progressive-facet-tree-navigation | test_counts_recompute_after_selection, test_backtracking_invalidates_children, test_disabled_branch_not_compiled | - | - | 선택·뒤로가기·0건·disabled·preview의 결정적 상태 전이를 offline fixture로 검증한다. | file-change-a2dce4728cf0 |
| file-change-98b9acce66be | MODIFY | `tests/test_interactive.py` | D-14-progressive-facet-tree-navigation | test_purpose_tree_scripted_parity, test_backtracking, test_preview_denominator | sha256:e585cfefb6a7ebe3335c751d27e824877236b461603cfc05ba53d36395ecbe42 | - | purpose mode, progressive facets, backtracking과 TTY/script profile parity를 검증한다. | file-change-3db064398654 |
| file-change-4b8a5b1304c0 | MODIFY | `tests/test_facets.py` | D-14-progressive-facet-tree-navigation | test_progressive_counts, test_identity_branch_status, test_invalid_selection | sha256:ca066bc3e245b05dc9db3657e3996a83ea9cea22328c3d61c449017f14e097c1 | - | 상위 선택별 count·coverage와 identity/disabled branch를 검증한다. | file-change-79c10e85533c |
| file-change-d840e60bc9b6 | MODIFY | `tests/test_query_contract.py` | D-12-current-search-trend-mode-separation | test_current_mode_defaults, test_trend_requires_series, test_selection_profile_roundtrip | sha256:67d25951197061989341f7b692a809fea4c2bbf0c55fce460a2041781a5890db | - | 모드별 필수값, legacy current adapter와 normalized selection roundtrip을 검증한다. | file-change-884e869a1a0f |

### Routed skills

- `c09-cli-contract` → `cli-creator` (IMPLEMENT, required): composable CLI와 interactive tree가 같은 query compiler를 사용하게 한다.
- `c09-verification` → `verification-before-completion` (VALIDATE, required): tree state와 query parity를 독립 검증한다.

### Completion criteria

- `C-09-mode-tree-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 현재/동향 목적 분리와 점진 facet tree가 실제 후보 count·disabled reason·backtracking을 보존한다.
