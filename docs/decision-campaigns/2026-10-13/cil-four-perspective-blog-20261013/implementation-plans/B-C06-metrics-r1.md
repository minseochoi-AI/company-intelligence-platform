# Implementation plan: B-C06-metrics-plan-r1

Status: `contract-ready`

## B-C06-metrics-S01: Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/metrics.py; 계정·권한·시점·통화 및 실제 dimension coverage를 유지한 readonly 조회; unavailable/unknown와0을 구분 | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. | B-C06-metrics-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/metrics.py | B-D06<br>B-D06-O01 | collect&#95;search&#95;metrics<br>collect&#95;adsense&#95;metrics | file-change-475e37c19be1 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;metrics.py; 새 테스트 파일: 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. | B-C06-metrics-K01 | CREATE | apps/company-report-blog/tests/test&#95;metrics.py | B-D06<br>B-D06-O01 | test&#95;metrics&#95;contract | file-change-d88831450f77 | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-475e37c19be1 | — | — |
| file-change-d88831450f77 | — | — |

</details>

### Routed skills

- B-C06-metrics-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C06-metrics-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D06-O01, changes=file-change-475e37c19be1, file-change-d88831450f77: 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope

