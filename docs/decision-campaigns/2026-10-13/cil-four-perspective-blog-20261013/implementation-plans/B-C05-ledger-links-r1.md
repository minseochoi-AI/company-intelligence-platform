# Implementation plan: B-C05-ledger-links-plan-r1

Status: `contract-ready`

## B-C05-ledger-links-S01: SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/ledger.py; SQLite transactional outbox·single writer·stable content&#95;key·append revision; network와 DB의 비원자성 복구 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. | B-C05-ledger-links-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/ledger.py | B-D05<br>B-D05-O01 | PublicationLedger<br>acquire&#95;writer<br>record&#95;attempt | file-change-9efdb1632b49 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/links.py; 명시 이유/관계의 typed 연결; 산업/직종/기업/시점/반박 글의 안정 ID 및 missing URL 상태; 자동 인과 추정 금지 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. | B-C05-ledger-links-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/links.py | B-D05<br>B-D05-O01 | register&#95;relation<br>refresh&#95;index&#95;links | file-change-a47c5eb0c4ed | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/migrations/001.sql; report/revision/evaluation/relation/publication&#95;attempt 테이블과 고유 content&#95;key 제약; 고객/키 데이터 저장 금지 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. | B-C05-ledger-links-K01 | CREATE | apps/company-report-blog/migrations/001.sql | B-D05<br>B-D05-O01 | ledger&#95;schema&#95;v1 | file-change-618b7cf82e49 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;ledger.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. | B-C05-ledger-links-K01 | CREATE | apps/company-report-blog/tests/test&#95;ledger.py | B-D05<br>B-D05-O01 | test&#95;ledger&#95;contract | file-change-7e7c210fc33d | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;relations.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. | B-C05-ledger-links-K01 | CREATE | apps/company-report-blog/tests/test&#95;relations.py | B-D05<br>B-D05-O01 | test&#95;relations&#95;contract | file-change-b630dece86b2 | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-9efdb1632b49 | — | — |
| file-change-a47c5eb0c4ed | — | — |
| file-change-618b7cf82e49 | — | — |
| file-change-7e7c210fc33d | — | — |
| file-change-b630dece86b2 | — | — |

</details>

### Routed skills

- B-C05-ledger-links-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C05-ledger-links-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D05-O01, changes=file-change-9efdb1632b49, file-change-a47c5eb0c4ed, file-change-618b7cf82e49, file-change-7e7c210fc33d, file-change-b630dece86b2: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리

