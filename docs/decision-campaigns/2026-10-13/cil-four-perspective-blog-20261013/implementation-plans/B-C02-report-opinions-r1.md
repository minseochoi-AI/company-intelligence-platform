# Implementation plan: B-C02-report-opinions-plan-r1

Status: `contract-ready`

## B-C02-report-opinions-S01: AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/models.py; 원천/계산/AI/사용자 schema를 독립 타입으로 검사하고 네 perspective 및 claim별 evidence 요구 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/models.py | B-D02<br>B-D02-O01 | ArticleSpec<br>AIReportRevision<br>HumanEvaluationRevision | file-change-c03ccdb32605 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/opinions.py; 사용자만 opinion을 쓰며 visibility와 based&#95;on revision을 저장; AI 재생성 시 원문을 그대로 보존 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/opinions.py | B-D02<br>B-D02-O01 | append&#95;evaluation<br>mark&#95;review&#95;outdated | file-change-3524bc461a72 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/compose.py; CIL structured 결과와 AI claim을 결합하되 근거 없는 숫자/빈 시계열은 검증 실패 또는 명시 한계 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/compose.py | B-D02<br>B-D02-O01 | compose&#95;report | file-change-a633d3050cf5 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/render.py; Jinja escape/StrictUndefined와 URL scheme allowlist; 네 섹션과 사실/AI/사람 앵커를 한 HTML에 출력 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/render.py | B-D02<br>B-D02-O01 | render&#95;report<br>validate&#95;link&#95;scheme | file-change-f176652da040 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/templates/report.html; 원천/계산 근거, 네 AI 관점, 사용자 의견, 관련 분석 목차를 한 페이지에 분리; private 평가 제외 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/templates/report.html | B-D02<br>B-D02-O01 | report&#95;template | file-change-b1b432dea9a9 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/schemas/report.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/schemas/report.schema.json | B-D02<br>B-D02-O01 | report.schema | file-change-e6a672c902bc | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/schemas/human-evaluation.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/schemas/human-evaluation.schema.json | B-D02<br>B-D02-O01 | human-evaluation.schema | file-change-4f661150db5f | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;report&#95;contracts.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/tests/test&#95;report&#95;contracts.py | B-D02<br>B-D02-O01 | test&#95;report&#95;contracts&#95;contract | file-change-3d0882685c44 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;human&#95;preservation.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/tests/test&#95;human&#95;preservation.py | B-D02<br>B-D02-O01 | test&#95;human&#95;preservation&#95;contract | file-change-3f276d628902 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;render.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. | B-C02-report-opinions-K01 | CREATE | apps/company-report-blog/tests/test&#95;render.py | B-D02<br>B-D02-O01 | test&#95;render&#95;contract | file-change-3290aadb47d1 | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-c03ccdb32605 | — | — |
| file-change-3524bc461a72 | — | — |
| file-change-a633d3050cf5 | — | — |
| file-change-f176652da040 | — | — |
| file-change-b1b432dea9a9 | — | — |
| file-change-e6a672c902bc | — | — |
| file-change-4f661150db5f | — | — |
| file-change-3d0882685c44 | — | — |
| file-change-3f276d628902 | — | — |
| file-change-3290aadb47d1 | — | — |

</details>

### Routed skills

- B-C02-report-opinions-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C02-report-opinions-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D02-O01, changes=file-change-c03ccdb32605, file-change-3524bc461a72, file-change-a633d3050cf5, file-change-f176652da040, file-change-b1b432dea9a9, file-change-e6a672c902bc, file-change-4f661150db5f, file-change-3d0882685c44, file-change-3f276d628902, file-change-3290aadb47d1: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단

