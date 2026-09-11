# Implementation plan: company-intelligence-cross-region-career-preparation--C-04-peer-screener-ranking--r1

Status: `contract-ready`

## peer-evidence-screener: 국가·산업·규모·기준일을 고정한 동료군에서 선택 지표만 순위화하고 coverage와 제외 사유를 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-06-peer-screener-ranking-service | CREATE | `src/company_intel/screening.py` | D-06-peer-screener-ranking | ScreenerProfile, screen_companies | - | - | 명시적 동료군과 지표 방향·최소 표본·coverage·근거를 보존한 결과를 반환한다. | - |
| D-06-peer-screener-ranking-test | CREATE | `tests/test_screening.py` | D-06-peer-screener-ranking | test_peer_boundaries_and_coverage | - | - | 동료군 경계·결측·방향·최소 표본을 fixture로 검증한다. | - |

### Routed skills

- `c04-verify` → `verification-before-completion` (VALIDATE, required): 스크리너 동작 검증

### Completion criteria

- `C-04-screener-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 동료군과 coverage 계약이 통과한다.
