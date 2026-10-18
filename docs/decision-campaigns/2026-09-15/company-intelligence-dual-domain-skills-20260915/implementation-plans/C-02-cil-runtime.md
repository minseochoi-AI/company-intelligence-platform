# Implementation plan: C-02-cil-runtime-plan-r1

Status: `contract-ready`

## C-02-cil-runtime-slice: 승인된 결정을 파일 단위로 구현하고 독립 검증한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| C02-001 | MODIFY | `src/company_intel/config.py` | D-09 | config.py | 44879c8438ccf7169c2b4ab8c4c975f61a9a9bf87eccaec7b8df93f7674db393 | - | 명시 root와 환경변수 fallback을 지원한다. | - |
| C02-002 | MODIFY | `src/company_intel/cli.py` | D-09 | cli.py | 79d5f528d8a7990030f8a04aad948074ca38b475834b070a227d15827233fcc7 | - | 전역 --project-root/--프로젝트-경로를 파싱한다. | - |
| C02-003 | MODIFY | `.codex/skills/company-intel-cli/SKILL.md` | D-09 | SKILL.md | 9d018a09dabb7d5a275a102345b6c69379893cb14823c6162c9cf9062c171d46 | - | 명시 project root 사용법과 fixture 경계를 안내한다. | - |
| C02-004 | CREATE | `tests/test_cli_project_root.py` | D-09 | test_cli_project_root.py | - | - | root 인자·환경변수·cwd 회귀를 검증한다. | - |

### Routed skills

- `runtime-verification` → `verification-before-completion` (VALIDATE, required): CIL 실행 위치 계약을 검증한다.

### Completion criteria

- `cil-root-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: tests/test_cli_project_root.py

