# Implementation plan: company-intelligence-cross-region-career-preparation--C-05-timeline-valuation-event-analysis--r2

Status: `contract-ready`

## point-in-time-analysis-gates-r2: 손실 없는 기업·시장·거시 fact의 series signature와 available_at을 검증한 뒤에만 시간축·가치·AI 사건 계산을 실행하고, 전망·proxy·원시주가·control 부재를 명시적으로 제한한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-07-analysis-service-r2 | MODIFY | `src/company_intel/analysis_service.py` | D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | build_company_timeline, evaluate_valuation_scenarios, evaluate_ai_event, validate_series_signature | sha256:2520ae86cfa241bea157db92e7ef5a499c1f2e34dcebc9230f4e2f69e92b5b2b | - | 축별 series signature와 lineage를 검사하고 불완전 입력은 계산 대신 UNKNOWN/NOT_APPLICABLE 및 이유를 반환한다. | - |
| D-07-analytics-r2 | MODIFY | `src/company_intel/analytics.py` | D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | rank_companies, dcf_scenarios, event_study, difference_in_differences | sha256:f4f76a87c9c7c2a226ff9164c783eb1c89beeed89c15cf1cc47346fe71a0f269 | - | 계산 입력 contract와 coverage diagnostics를 강화하고 raw price·projection·revision이 섞인 입력을 거부한다. | - |
| D-07-analysis-service-tests-r2 | MODIFY | `tests/test_analysis_service.py` | D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | test_incompatible_series_unavailable, test_projection_separated, test_raw_price_rejected, test_proxy_event_rejected | sha256:8e6ddf46d159c606c4603d4aa9f40aca44ec148884d7dc6b3f7e4cf9c9c5184c | - | Eurostat/ECB/IMF/World Bank/CNB/Alpha/GitHub 형태의 최소 fixture로 불완전 series가 계산되지 않는지 검증한다. | - |
| D-07-analytics-tests-r2 | MODIFY | `tests/test_analytics.py` | D-07-company-timeline-macro-comparison, D-08-future-value-scenarios, D-09-ai-event-effect-validation | test_guarded_dcf, test_event_requires_adjusted_market_series, test_did_requires_aligned_control | sha256:55817354f79447faa7c9ddb14dd65606c2c38391d0c2cb76e3390e7b21137d4d | - | 동일 길이만이 아니라 기간·단위·available_at·benchmark/control coverage가 맞아야 계산되는지 검증한다. | - |

### Routed skills

- `c05-r2-tdd` → `tdd` (IMPLEMENT, required): series signature와 분석 gate를 테스트 우선 구현
- `c05-r2-research` → `company-intelligence-career-research` (IMPLEMENT, required): 거시·시장 지표를 회사 사실이나 인과로 오해하지 않는 경계 검토
- `c05-r2-verify` → `verification-before-completion` (VALIDATE, required): 시간축·가치·사건 적격성 독립 검증

### Completion criteria

- `C-05-r2-analysis-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: series signature, point-in-time, actual/projection, adjusted price, benchmark/control 및 proxy 경계가 통과한다.
