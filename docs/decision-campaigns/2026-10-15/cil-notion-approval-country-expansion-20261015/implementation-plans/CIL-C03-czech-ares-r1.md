# Implementation plan: CIL-C03-czech-ares-plan-r1

Status: `contract-ready`

## CIL-C03-czech-ares-S01: 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 | 체코 경제주체 레지스트리(ARES) REST API를 통해 기업 상호명 및 IČO로 18개 이상 CZ-NACE 산업분류와 본사 주소를 실시간 동적 조회하는 어댑터를 어떻게 구축할 것인가? | CIL-C03-czech-ares-K01 | CREATE | src/company&#95;intel/connectors/ares&#95;dynamic.py | CIL-D03<br>CIL-D03-O01 | AresDynamicClient<br>get&#95;economic&#95;subject | file-change-cil-d03-01 | — |
| 미구현 | 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 검증 단위 테스트 | 무결성 검증 | CIL-C03-czech-ares-K01 | CREATE | tests/test&#95;ares&#95;dynamic.py | CIL-D03<br>CIL-D03-O02 | test&#95;ares&#95;dynamic&#95;lookup | file-change-cil-d03-02 | file-change-cil-d03-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d03-01 | — | — |
| file-change-cil-d03-02 | — | — |

</details>

### Routed skills

- CIL-C03-czech-ares-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C03-czech-ares-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D03-O01, CIL-D03-O02, changes=file-change-cil-d03-01, file-change-cil-d03-02: 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기

