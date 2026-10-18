# Implementation plan: JP-C01-schema-contract-plan-r1

Status: `contract-ready`

## JP-C01-schema-contract-S01: ClusterSignature 기반 CanonicalJobRecord 및 JobSchemaContract 키 불일치 방어 엔진

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 원천 API별 상이한 키(`portal_id` vs `job_id`, `job_url` vs `posting_url`)로 인한 무음 결함(None 반환) | `CanonicalJobRecord` 및 `JobSchemaContract` 선언적 매핑 및 엄격한 키 검증기 구축 | 체코 196건 URL 누락과 같은 API 키 불일치 오류를 런타임에 즉시 탐지하고 정규화하기 위함 | JP-C01-schema-contract-K01 | MODIFY | src/company&#95;intel/classification.py | JP-D01<br>JP-D01-O01 | CanonicalJobRecord<br>JobSchemaContract<br>from&#95;cz&#95;mpsv&#95;job&#95;record<br>from&#95;kr&#95;public&#95;job&#95;record | file-change-jp-d01-01 | — |
| 키 매핑 및 불일치 방어 검증 테스트 부재 | 스키마 계약 및 팩토리 단위 테스트 스위트 작성 | 별칭 매핑, 필수 키 누락 시 KeyAlignmentError 발생, 와일드카드 매칭 검증 | JP-C01-schema-contract-K01 | CREATE | tests/test&#95;job&#95;cluster&#95;signature.py | JP-D01<br>JP-D01-O02 | test&#95;job&#95;schema&#95;contract&#95;validation<br>test&#95;mpsv&#95;portal&#95;url&#95;synthesis | file-change-jp-d01-02 | file-change-jp-d01-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-jp-d01-01 | — | — |
| file-change-jp-d01-02 | — | — |

</details>

### Routed skills

- JP-C01-schema-contract-route → decision-campaign-workbook (VALIDATE, required): 단위 구현 및 회귀 테스트 검증

### Completion criteria

- `JP-C01-schema-contract-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=JP-D01-O01, JP-D01-O02, changes=file-change-jp-d01-01, file-change-jp-d01-02: ClusterSignature 기반 CanonicalJobRecord 및 JobSchemaContract 키 불일치 방어 엔진
