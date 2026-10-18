# Implementation plan: CIL-C05-notion-approval-plan-r1

Status: `contract-ready`

## CIL-C05-notion-approval-S01: 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 미구현 또는 고정 픽스처 | 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 | 에이전트가 생성한 기업/직무 분석 보고서를 노션 데이터베이스('에이전트 개발 로그')에 초안으로 등록하고, 스마트폰 노션 앱에서의 '승인' 토글을 감지하는 모바일 승인 큐를 어떻게 구축할 것인가? | CIL-C05-notion-approval-K01 | CREATE | src/company&#95;intel/notion&#95;queue.py | CIL-D05<br>CIL-D05-O01 | NotionApprovalQueue<br>create&#95;draft&#95;page<br>poll&#95;approved&#95;pages | file-change-cil-d05-01 | — |
| 미구현 | 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 검증 단위 테스트 | 무결성 검증 | CIL-C05-notion-approval-K01 | CREATE | tests/test&#95;notion&#95;queue.py | CIL-D05<br>CIL-D05-O02 | test&#95;notion&#95;approval&#95;flow | file-change-cil-d05-02 | file-change-cil-d05-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-cil-d05-01 | — | — |
| file-change-cil-d05-02 | — | — |

</details>

### Routed skills

- CIL-C05-notion-approval-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `CIL-C05-notion-approval-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=CIL-D05-O01, CIL-D05-O02, changes=file-change-cil-d05-01, file-change-cil-d05-02: 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진

