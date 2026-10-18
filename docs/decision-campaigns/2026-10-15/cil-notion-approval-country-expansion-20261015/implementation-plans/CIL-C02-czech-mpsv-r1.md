# Implementation plan: CIL-C02-czech-mpsv-plan-r1

Status: `contract-ready`

## CIL-C02-czech-mpsv-S01: 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 | 체코 노동사회부(MPSV)의 178.8MB 전수 구인공고 JSON 덤프를 메모리 폭증 없이 청크 단위로 스트리밍 파싱하여 CZ-ISCO 직무 코드로 집계하는 수집기를 어떻게 구축할 것인가? | CIL-C02-czech-mpsv-K01 | CREATE | src/company&#95;intel/connectors/mpsv&#95;stream.py | CIL-D02<br>CIL-D02-O01 | stream&#95;mpsv&#95;vacancies<br>aggregate&#95;by&#95;cz&#95;isco | file-change-cil-d02-01 | — |
| 미구현 | 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 검증 단위 테스트 | 무결성 검증 | CIL-C02-czech-mpsv-K01 | CREATE | tests/test&#95;mpsv&#95;stream.py | CIL-D02<br>CIL-D02-O02 | test&#95;mpsv&#95;stream&#95;parsing | file-change-cil-d02-02 | file-change-cil-d02-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d02-01 | — | — |
| file-change-cil-d02-02 | — | — |

</details>

### Routed skills

- CIL-C02-czech-mpsv-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C02-czech-mpsv-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D02-O01, CIL-D02-O02, changes=file-change-cil-d02-01, file-change-cil-d02-02: 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑

