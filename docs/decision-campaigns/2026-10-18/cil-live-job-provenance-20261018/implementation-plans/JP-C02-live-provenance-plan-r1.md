# Implementation plan: JP-C02-live-provenance-plan-r1

Status: `contract-ready`

## JP-C02-live-provenance-S01: 실시간 API 정본 및 링크 생존성 검증 모듈 (JobProvenanceVerifier)

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 공고 URL의 실시간 HTTP 응답 상태(200 OK vs 404) 및 접수마감일 기준 생존성 판정 로직 부재 | `JobProvenanceVerifier` 구축: HTTP HEAD 프로빙, 마감일 기준 Freshness(LIVE_ACTIVE, CLOSED) 자동 판정 | 공고 링크가 실제로 유효한지 1:1 감사하고 검증 증거 메모를 남기기 위함 | JP-C02-live-provenance-K01 | CREATE | src/company&#95;intel/live&#95;job&#95;provenance.py | JP-D02<br>JP-D02-O01 | JobProvenanceVerifier<br>verify&#95;job&#95;url&#95;liveness<br>evaluate&#95;listing&#95;freshness | file-change-jp-d02-01 | file-change-jp-d01-01 |
| 실시간 링크 생존성 검증 단위 테스트 부재 | 라이브 프로버넌스 검증기 단위 테스트 작성 | HTTP 상태 코드, SSL 타임아웃, 마감일 경과 판정 테스트 | JP-C02-live-provenance-K01 | CREATE | tests/test&#95;live&#95;job&#95;provenance.py | JP-D02<br>JP-D02-O02 | test&#95;provenance&#95;verifier&#95;http&#95;check<br>test&#95;freshness&#95;state&#95;transitions | file-change-jp-d02-02 | file-change-jp-d02-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-jp-d02-01 | — | — |
| file-change-jp-d02-02 | — | — |

</details>

### Routed skills

- JP-C02-live-provenance-route → decision-campaign-workbook (VALIDATE, required): 라이브 검증 모듈 테스트

### Completion criteria

- `JP-C02-live-provenance-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=JP-C01-schema-contract-K01, obligations=JP-D02-O01, JP-D02-O02, changes=file-change-jp-d02-01, file-change-jp-d02-02: 실시간 API 정본 및 링크 생존성 검증 모듈 (JobProvenanceVerifier)
