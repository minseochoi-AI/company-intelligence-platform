# Implementation plan: B-C01-taxonomy-plan-r1

Status: `contract-ready`

## B-C01-taxonomy-S01: 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/taxonomy.py; 명시 sector parent/order와 네 audience를 유지하고 slug collision/분류 미등록을 검사; 목차는 report&#95;id로 연결 | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | B-C01-taxonomy-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/taxonomy.py | B-D01<br>B-D01-O01 | build&#95;sector&#95;tree<br>project&#95;blogger&#95;labels | file-change-760b6123d467 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/schemas/taxonomy.schema.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | B-C01-taxonomy-K01 | CREATE | apps/company-report-blog/schemas/taxonomy.schema.json | B-D01<br>B-D01-O01 | taxonomy.schema | file-change-8a2889c1dc62 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/config/taxonomy.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | B-C01-taxonomy-K01 | CREATE | apps/company-report-blog/config/taxonomy.json | B-D01<br>B-D01-O01 | taxonomy | file-change-0a8210721a0f | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;taxonomy.py; 새 테스트 파일: 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report&#95;id의 중복 방지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. | B-C01-taxonomy-K01 | CREATE | apps/company-report-blog/tests/test&#95;taxonomy.py | B-D01<br>B-D01-O01 | test&#95;taxonomy&#95;contract | file-change-aeda4c03fbdf | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-760b6123d467 | — | — |
| file-change-8a2889c1dc62 | — | — |
| file-change-0a8210721a0f | — | — |
| file-change-aeda4c03fbdf | — | — |

</details>

### Routed skills

- B-C01-taxonomy-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C01-taxonomy-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D01-O01, changes=file-change-760b6123d467, file-change-8a2889c1dc62, file-change-0a8210721a0f, file-change-aeda4c03fbdf: 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report&#95;id의 중복 방지

