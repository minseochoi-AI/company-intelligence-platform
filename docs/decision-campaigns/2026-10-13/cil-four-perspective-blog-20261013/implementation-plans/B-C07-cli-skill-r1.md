# Implementation plan: B-C07-cli-skill-plan-r1

Status: `contract-ready`

## B-C07-cli-skill-S01: 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.

### Changes

| ID | Operation | Path | Decisions | Obligations | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| file-change-6da0dec88ca8 | CREATE | `apps/company-report-blog/pyproject.toml` | B-D07 | B-D07-O01 | report_blog_package | - | - | 적용 경계: apps/company-report-blog/pyproject.toml; 별도 앱 console entrypoint 및 SDK2.201.0/google-auth2.62.0/oauthlib1.5.0/Jinja3.1.6; CIL 루트 패키지는 변경하지 않음 | - |
| file-change-269781ae6688 | CREATE | `apps/company-report-blog/uv.lock` | B-D07 | B-D07-O01 | resolved_dependency_lock | - | - | 적용 경계: apps/company-report-blog/uv.lock; 위 직접 버전과 전이 의존성 hash를 lock하고 Python3.13 resolver/local test; 설치 성공을 live 연동으로 판단하지 않음 | - |
| file-change-57c5036c11db | CREATE | `apps/company-report-blog/src/report_blog/__init__.py` | B-D07 | B-D07-O01 | __init__ | - | - | 적용 경계: apps/company-report-blog/src/report_blog/__init__.py; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | - |
| file-change-0fa8857c54f3 | CREATE | `apps/company-report-blog/src/report_blog/cli.py` | B-D07 | B-D07-O01 | main | - | - | 적용 경계: apps/company-report-blog/src/report_blog/cli.py; 새 앱 CLI는 보고서 inspect/collect/compose/render/evaluate/link/preview/sync/reconcile/metrics의 typed 입출력; 기존 CIL CLI에는 allowlisted collect만 추가 | - |
| file-change-3d21764f4086 | CREATE | `apps/company-report-blog/README.md` | B-D07 | B-D07-O01 | README | - | - | 적용 경계: apps/company-report-blog/README.md; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. | - |
| file-change-335b547b9414 | CREATE | `apps/company-report-blog/skills/company-report-blog/SKILL.md` | B-D07 | B-D07-O01 | company-report-blog | - | - | 적용 경계: apps/company-report-blog/skills/company-report-blog/SKILL.md; 네 관점 작성과 CIL 호출·의견 소유권·preview/draft/게시·metrics를 연결하는 thin skill; 기존 분석 스킬과 캠페인 권위 보존 | - |
| file-change-c8824f26de4b | CREATE | `apps/company-report-blog/skills/company-report-blog/agents/openai.yaml` | B-D07 | B-D07-O01 | skill_metadata | - | - | 적용 경계: apps/company-report-blog/skills/company-report-blog/agents/openai.yaml; 스킬 trigger/예시를 보고서 실행으로 한정하고 암묵 발동이 원격 쓰기 승인을 만들지 않도록 지침 | - |
| file-change-f292f33ffbc7 | CREATE | `apps/company-report-blog/tests/test_cli.py` | B-D07 | B-D07-O01 | test_cli_contract | - | - | 적용 경계: apps/company-report-blog/tests/test_cli.py; 새 테스트 파일: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. | - |

### Routed skills

- `B-C07-cli-skill-review` → `decision-campaign-workbook` (VALIDATE, required): 계획 연결과 실제 테스트 영수증 구분

### Completion criteria

- `B-C07-cli-skill-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=B-D07-O01, changes=file-change-6da0dec88ca8, file-change-269781ae6688, file-change-57c5036c11db, file-change-0fa8857c54f3, file-change-3d21764f4086, file-change-335b547b9414, file-change-c8824f26de4b, file-change-f292f33ffbc7: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지

