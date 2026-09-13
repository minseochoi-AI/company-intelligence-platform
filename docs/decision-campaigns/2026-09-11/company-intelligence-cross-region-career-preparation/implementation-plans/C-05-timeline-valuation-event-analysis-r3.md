# Implementation plan: company-intelligence-cross-region-career-preparation--C-05-timeline-valuation-event-analysis--r3

Status: `contract-ready`

## timeline-and-analysis-prerequisites-r3: timeline/valuation/ai-event 메뉴가 서로 다른 축과 series signature를 섞지 않고, 선택 전의 비교 불가 조건과 필요한 evidence를 설명한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-07-axis-series-timeline-r3 | MODIFY | `src/company_intel/analysis_service.py` | D-07-company-timeline-macro-comparison | validate_series_signature, build_company_timeline, timeline_series_groups | sha256:d576bc39cccc2bac36d52a98748da738ebeececd23e2f8c2dd62887bd1f00c0e | - | axis별·signature별 series group를 유지하고 date alignment 및 제외 사유를 명시한다. | - |
| D-08-D09-analysis-prerequisite-r3 | MODIFY | `src/company_intel/analytics.py` | D-08-future-value-scenarios, D-09-ai-event-effect-validation | valuation_prerequisites, event_study_prerequisites | sha256:7d1de8faec145f4e3ea440bf54773585605221e9514ca4d3a394b96fbff17e44 | - | 가치 시나리오와 AI 사건 분석 전에 필요 evidence, comparison/control 한계, association-only 상태를 반환한다. | - |
| D-07-timeline-tests-r3 | MODIFY | `tests/test_analysis_service.py` | D-07-company-timeline-macro-comparison | test_multi_axis_timeline_groups | sha256:739f5918cf2cd1e4813f67b5f2c33b5dfbcf1526f990a24eadb7b20c1263d7a4 | - | company/market/macro axes와 incompatible signature가 독립 group으로 남는지 검증한다. | D-07-axis-series-timeline-r3 |
| D-08-D09-analytics-tests-r3 | MODIFY | `tests/test_analytics.py` | D-08-future-value-scenarios, D-09-ai-event-effect-validation | test_analysis_prerequisites | sha256:55817354f79447faa7c9ddb14dd65606c2c38391d0c2cb76e3390e7b21137d4d | - | missing source/time/unit/control의 deterministic explanation을 검증한다. | D-08-D09-analysis-prerequisite-r3 |

### Routed skills

- `analysis-implementation` → `company-intelligence-career-research` (IMPLEMENT, required): series meaning과 evidence limit을 보존한다.
- `analysis-tests` → `tdd` (VALIDATE, required): offline timeline/analytics tests를 실행한다.

### Completion criteria

- `C05-r3-analysis-groups-tests` [planned] `tdd` phase=VALIDATE, depends=-: 다축 timeline과 valuation/event precondition이 올바르게 설명된다.

