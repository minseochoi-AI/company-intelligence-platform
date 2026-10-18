# Implementation plan: CIL-C01-opendart-master-plan-r1

Status: `contract-ready`

## CIL-C01-opendart-master-S01: 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 | 대한민국 119,634개 상장/외감 법인 전수를 로컬 DuckDB에 색인하여 임의 기업명에서 corp&#95;code를 0.001초 내 동적 해소하는 어댑터를 어떻게 구축할 것인가? | CIL-C01-opendart-master-K01 | CREATE | src/company&#95;intel/connectors/opendart&#95;master.py | CIL-D01<br>CIL-D01-O01 | OpenDartMasterIndex<br>resolve&#95;corp&#95;code | file-change-cil-d01-01 | — |
| 미구현 | 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 검증 단위 테스트 | 무결성 검증 | CIL-C01-opendart-master-K01 | CREATE | tests/test&#95;opendart&#95;master.py | CIL-D01<br>CIL-D01-O02 | test&#95;opendart&#95;master&#95;index | file-change-cil-d01-02 | file-change-cil-d01-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d01-01 | — | — |
| file-change-cil-d01-02 | — | — |

</details>

### Routed skills

- CIL-C01-opendart-master-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C01-opendart-master-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D01-O01, CIL-D01-O02, changes=file-change-cil-d01-01, file-change-cil-d01-02: 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터

