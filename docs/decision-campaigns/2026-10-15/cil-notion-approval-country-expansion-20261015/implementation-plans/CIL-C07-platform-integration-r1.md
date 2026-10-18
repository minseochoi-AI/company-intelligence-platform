# Implementation plan: CIL-C07-platform-integration-plan-r1

Status: `contract-ready`

## CIL-C07-platform-integration-S01: 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 | 구축된 OpenDART 마스터, 체코 MPSV/ARES, 워크넷, 노션-Blogger 배포 파이프라인을 통합하여 #1 채용 및 #2 기업 스크리닝 엔드포인트를 실시간 동적 검색 체계로 완성할 방안은 무엇인가? | CIL-C07-platform-integration-K01 | CREATE | src/company&#95;intel/dynamic&#95;screening.py | CIL-D07<br>CIL-D07-O01 | DynamicScreeningEngine<br>run&#95;screening&#95;pipeline | file-change-cil-d07-01 | — |
| 미구현 | 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 검증 단위 테스트 | 무결성 검증 | CIL-C07-platform-integration-K01 | CREATE | tests/test&#95;dynamic&#95;screening.py | CIL-D07<br>CIL-D07-O02 | test&#95;dynamic&#95;screening&#95;pipeline | file-change-cil-d07-02 | file-change-cil-d07-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d07-01 | — | — |
| file-change-cil-d07-02 | — | — |

</details>

### Routed skills

- CIL-C07-platform-integration-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C07-platform-integration-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D07-O01, CIL-D07-O02, changes=file-change-cil-d07-01, file-change-cil-d07-02: 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통

