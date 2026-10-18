# Implementation plan: CIL-C04-worknet-public-plan-r1

Status: `contract-ready`

## CIL-C04-worknet-public-S01: 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 | .env에 등록된 공공데이터포털(nomal) 및 고용노동부 워크넷 OpenAPI를 활용하여 실시간 전국 공공/민간 채용공고와 NCS 직무 단위를 동적 조회하는 커넥터를 어떻게 구축할 것인가? | CIL-C04-worknet-public-K01 | CREATE | src/company&#95;intel/connectors/worknet.py | CIL-D04<br>CIL-D04-O01 | WorknetJobConnector<br>search&#95;worknet&#95;jobs | file-change-cil-d04-01 | — |
| 미구현 | 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 검증 단위 테스트 | 무결성 검증 | CIL-C04-worknet-public-K01 | CREATE | tests/test&#95;worknet.py | CIL-D04<br>CIL-D04-O02 | test&#95;worknet&#95;jobs&#95;parsing | file-change-cil-d04-02 | file-change-cil-d04-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d04-01 | — | — |
| file-change-cil-d04-02 | — | — |

</details>

### Routed skills

- CIL-C04-worknet-public-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C04-worknet-public-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D04-O01, CIL-D04-O02, changes=file-change-cil-d04-01, file-change-cil-d04-02: 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터

