# Implementation plan: B-C04-blogger-plan-r1

Status: `contract-ready`

## B-C04-blogger-S01: CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/blogger.py; 소유 계정 blog 해소·list/get/draft insert/patch/publish; dry-run/명시 mode, 불확실 응답 대조 및 외부 편집 충돌 차단 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. | B-C04-blogger-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/blogger.py | B-D04<br>B-D04-O01 | BloggerPublisher<br>reconcile&#95;post | file-change-9bd037dc0311 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/google&#95;auth.py; 사용자 OAuth 파일 외부 secret reference; scope별 서비스·refresh·30s transport; key나 token 출력 금지 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. | B-C04-blogger-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/google&#95;auth.py | B-D04<br>B-D04-O01 | load&#95;user&#95;credentials<br>build&#95;authorized&#95;service | file-change-7d2de96119d5 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/config/provider-contracts.json; Google7+성과4의 호출형식·secret ref·scope·read/write·retry/쿼터/권리/exit 경계를 분리 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. | B-C04-blogger-K01 | CREATE | apps/company-report-blog/config/provider-contracts.json | B-D04<br>B-D04-O01 | provider&#95;contracts | file-change-871e48ad3a4d | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;blogger&#95;adapter.py; 새 테스트 파일: isDraft=True 명시, 같은 content&#95;key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. | B-C04-blogger-K01 | CREATE | apps/company-report-blog/tests/test&#95;blogger&#95;adapter.py | B-D04<br>B-D04-O01 | test&#95;blogger&#95;adapter&#95;contract | file-change-76f93b28cdc1 | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-9bd037dc0311 | — | — |
| file-change-7d2de96119d5 | — | — |
| file-change-871e48ad3a4d | — | — |
| file-change-76f93b28cdc1 | — | — |

</details>

### Routed skills

- B-C04-blogger-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C04-blogger-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D04-O01, changes=file-change-9bd037dc0311, file-change-7d2de96119d5, file-change-871e48ad3a4d, file-change-76f93b28cdc1: isDraft=True 명시, 같은 content&#95;key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회

