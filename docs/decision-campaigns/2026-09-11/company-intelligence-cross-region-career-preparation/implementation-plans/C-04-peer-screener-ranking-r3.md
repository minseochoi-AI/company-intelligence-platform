# Implementation plan: company-intelligence-cross-region-career-preparation--C-04-peer-screener-ranking--r3

Status: `contract-ready`

## screener-comparability-selection-r3: screen 명령이 서로 다른 통화·단위·기간·available_at를 한 집단으로 묵시적으로 삭제하지 않고, 선택 가능한 비교 집단과 제외 근거를 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-06-screener-signature-groups-r3 | MODIFY | `src/company_intel/screening.py` | D-06-peer-screener-ranking | ScreenerProfile, ScreenerResult, screen_companies | sha256:3116db3b18256dbe4494188a9d0a579a9550ba86a69b6720c7eed2763ceb33ce | - | signature group와 coverage/exclusion reason을 반환하고 UI가 사용자가 비교 집단을 선택하게 한다. | - |
| D-06-screener-group-tests-r3 | MODIFY | `tests/test_screening.py` | D-06-peer-screener-ranking | test_multiple_comparability_groups | sha256:6259def1097dfe9daec6e4ec521d1bb6c30772cb90e0596711cba7669debe95b | - | 여러 group, 선택되지 않은 group, coverage 경고를 offline으로 검증한다. | D-06-screener-signature-groups-r3 |

### Routed skills

- `screening-implementation` → `company-intelligence-career-research` (IMPLEMENT, required): 비교 가능성 경계를 유지한다.
- `screening-tests` → `tdd` (VALIDATE, required): offline screener tests를 실행한다.

### Completion criteria

- `C04-r3-screener-group-tests` [planned] `tdd` phase=VALIDATE, depends=-: screen은 비교 집단과 제외 사유를 숨기지 않는다.
