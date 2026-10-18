# Implementation plan: B-C07-cli-skill-plan-r3

Status: `contract-ready`

## B-C07-cli-skill-S01: 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/pyproject.toml; 별도 앱 console entrypoint 및 SDK2.201.0/google-auth2.62.0/oauthlib1.5.0/Jinja3.1.6; CIL 루트 패키지는 변경하지 않음 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/pyproject.toml | B-D07<br>B-D07-O01 | report&#95;blog&#95;package | file-change-6da0dec88ca8 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/uv.lock; 위 직접 버전과 전이 의존성 hash를 lock하고 Python3.13 resolver/local test; 설치 성공을 live 연동으로 판단하지 않음 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/uv.lock | B-D07<br>B-D07-O01 | resolved&#95;dependency&#95;lock | file-change-269781ae6688 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/src/report&#95;blog/&#95;&#95;init&#95;&#95;.py; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/&#95;&#95;init&#95;&#95;.py | B-D07<br>B-D07-O01 | &#95;&#95;init&#95;&#95; | file-change-57c5036c11db | — |
| 이 목적의 컴포넌트 없음 | 새 앱 CLI가 typed CollectionSpec으로 collectors를 호출하고 기존 CIL CLI의 ingest/분석을 연결한다. 기존 CIL 23개 명령·Korean help/guide 파일은 수정하지 않는다. 일반 실행은 preview/초안만 생성한다. publish 및 이미 공개된 글의 content/labels 변경은 대상 report revision과 post ID에 대한 명시 mode/실행 허용이 없으면 거부한다. OAuth blogger scope와 정책 승인을 개별 게시 허가로 대체하지 않는다. | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/src/report&#95;blog/cli.py | B-D07<br>B-D09<br>B-D07-O01<br>B-D09-O01 | main | file-change-0fa8857c54f3 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/README.md; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/README.md | B-D07<br>B-D07-O01 | README | file-change-3d21764f4086 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/skills/company-report-blog/SKILL.md; 네 관점 작성과 CIL 호출·의견 소유권·preview/draft/게시·metrics를 연결하는 thin skill; 기존 분석 스킬과 캠페인 권위 보존 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/skills/company-report-blog/SKILL.md | B-D07<br>B-D07-O01 | company-report-blog | file-change-335b547b9414 | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/skills/company-report-blog/agents/openai.yaml; 스킬 trigger/예시를 보고서 실행으로 한정하고 암묵 발동이 원격 쓰기 승인을 만들지 않도록 지침 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/skills/company-report-blog/agents/openai.yaml | B-D07<br>B-D07-O01 | skill&#95;metadata | file-change-c8824f26de4b | — |
| 이 목적의 컴포넌트 없음 | 적용 경계: apps/company-report-blog/tests/test&#95;cli.py; 새 테스트 파일: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | B-C07-cli-skill-K01 | CREATE | apps/company-report-blog/tests/test&#95;cli.py | B-D07<br>B-D07-O01 | test&#95;cli&#95;contract | file-change-f292f33ffbc7 | — |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-6da0dec88ca8 | — | — |
| file-change-269781ae6688 | — | — |
| file-change-57c5036c11db | — | — |
| file-change-0fa8857c54f3 | — | — |
| file-change-3d21764f4086 | — | — |
| file-change-335b547b9414 | — | — |
| file-change-c8824f26de4b | — | — |
| file-change-f292f33ffbc7 | — | — |

</details>

### Routed skills

- B-C07-cli-skill-review → decision-campaign-workbook (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C07-cli-skill-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D07-O01, B-D09-O01, changes=file-change-6da0dec88ca8, file-change-269781ae6688, file-change-57c5036c11db, file-change-0fa8857c54f3, file-change-3d21764f4086, file-change-335b547b9414, file-change-c8824f26de4b, file-change-f292f33ffbc7: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과

