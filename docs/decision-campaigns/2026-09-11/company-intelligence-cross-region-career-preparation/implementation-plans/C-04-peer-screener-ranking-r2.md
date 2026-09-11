# Implementation plan: company-intelligence-cross-region-career-preparation--C-04-peer-screener-ranking--r2

Status: `contract-ready`

## comparable-peer-ranking-r2: 국가·산업·규모뿐 아니라 통화·기간·회계개념·단위·vintage·coverage가 같은 기업 fact만 동료군으로 묶고 비교 불가 후보를 별도 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-06-screening-signature-r2 | MODIFY | `src/company_intel/screening.py` | D-06-peer-screener-ranking | ScreenerProfile, screen_companies, ComparabilitySignature, ScreenerResult | sha256:0bc9f5aa7df1287b465373dbb3d0df39711ab936b5406823b15696f7c6fd8b19 | - | metric별 비교 signature와 최소 coverage/peer size를 강제하고 macro·procurement·activity proxy를 재무 순위에서 거부한다. | - |
| D-06-screening-tests-r2 | MODIFY | `tests/test_screening.py` | D-06-peer-screener-ranking | test_incompatible_units_excluded, test_proxy_metric_rejected, test_coverage_threshold, test_deterministic_peer_rank | sha256:666d6e7a502f6570815dfb3c2208c1ec552577501b0b5b36b749b46bc0a6d4ea | - | 통화·기간·concept·vintage 불일치, proxy 오용, coverage 미달과 동일 signature 순위를 fixture로 검증한다. | - |

### Routed skills

- `c04-r2-tdd` → `tdd` (IMPLEMENT, required): 비교 signature와 제외 규칙을 테스트 우선 구현
- `c04-r2-verify` → `verification-before-completion` (VALIDATE, required): 동료군 비교 가능성과 결정론 검증

### Completion criteria

- `C-04-r2-screener-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 동일 signature 동료군만 순위화되고 단위·기간·concept·proxy·coverage 위반은 설명 가능한 제외로 반환된다.
