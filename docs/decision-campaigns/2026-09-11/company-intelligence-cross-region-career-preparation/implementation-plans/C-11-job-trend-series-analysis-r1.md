# Implementation plan: company-intelligence-cross-region-career-preparation--C-11-job-trend-series-analysis--r1

Status: `contract-ready`

## versioned-job-trend-analysis: 동일 provider·분류 version·coverage cohort의 반복 snapshot에서 공고 등장·유지·종료와 신규·활성·종료·모집인원·급여·요건 지표를 계산하고 부적격 시 이유를 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-3a37488d99a0 | CREATE | `src/company_intel/job_trends.py` | D-16-job-trend-series-analysis-contract | TrendEligibility, PostingLifecycle, build_posting_lifecycle, evaluate_trend_eligibility, aggregate_job_trends | - | - | 안정적 posting identity와 versioned coverage를 검사한 뒤 적격 cohort만 시계열 지표로 집계한다. | - |
| file-change-9274cd7e97f7 | MODIFY | `src/company_intel/analytics.py` | D-16-job-trend-series-analysis-contract | series_signature, coverage_break, trend_comparison_groups | sha256:2600f9606bf74be060b0af2878cda3769f4c65f0ad0db463fc4f57556b6e19ac | - | snapshot frequency, provider coverage, taxonomy version, identity quality를 비교 signature에 포함한다. | file-change-3a37488d99a0 |
| file-change-086cfded9687 | MODIFY | `src/company_intel/analysis_service.py` | D-16-job-trend-series-analysis-contract | evaluate_job_trends, job_trend_timeline, job_event_boundary | sha256:cdbb79e1222ce4a7a1e5d90ca846659378363a251288a08d10f1e33a6d4eb4ad | - | 동향 eligibility와 지표 series를 반환하고 control이 없으면 event 결과를 association-only로 제한한다. | file-change-9274cd7e97f7 |
| file-change-4abcc47e1c00 | CREATE | `tests/test_job_trends.py` | D-16-job-trend-series-analysis-contract | test_single_snapshot_is_ineligible, test_posting_lifecycle, test_coverage_break, test_trend_metrics | - | - | 단일 snapshot 거부, 등장·유지·종료, coverage/version break와 동질 cohort 지표를 검증한다. | file-change-3a37488d99a0, file-change-086cfded9687 |
| file-change-8fd4c111121f | MODIFY | `tests/test_analytics.py` | D-16-job-trend-series-analysis-contract | test_job_series_signature, test_coverage_break_is_ineligible | sha256:eaa89ab061fc164c0ea839bfb695201e8023cee7539b3b30b3ad9a5c62dd99dc | - | 채용 series signature와 coverage break가 분석 적격성을 차단하는지 검증한다. | file-change-9274cd7e97f7 |
| file-change-ba9762e5fbcb | MODIFY | `tests/test_analysis_service.py` | D-16-job-trend-series-analysis-contract | test_job_trend_unavailable_reason, test_job_event_association_only | sha256:59c7893c0c7163ea2b39f088f1f57030b06c5008e1cfd9e77d01a05ef63187da | - | insufficient history·coverage break와 control 없는 association-only 응답을 검증한다. | file-change-086cfded9687 |

### Routed skills

- `c11-trend-semantics` → `company-intelligence-career-research` (IMPLEMENT, required): 공개 공고 수요 변화와 실제 고용·인과 주장의 경계를 유지한다.
- `c11-verification` → `verification-before-completion` (VALIDATE, required): snapshot lifecycle과 trend eligibility를 독립 검증한다.

### Completion criteria

- `C-11-job-trend-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 반복 snapshot만 동향으로 집계되고 단일 이력·coverage break·비동질 급여 series는 분석불가로 남는다.
