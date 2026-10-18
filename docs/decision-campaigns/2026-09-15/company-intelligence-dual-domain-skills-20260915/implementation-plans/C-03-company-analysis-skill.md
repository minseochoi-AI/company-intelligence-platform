# Implementation plan: C-03-company-analysis-skill-plan-r1

Status: `contract-ready`

## C-03-company-analysis-skill-slice: 승인된 결정을 파일 단위로 구현하고 독립 검증한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| C03-001 | CREATE | `.codex/skills/company-intelligence-analysis/SKILL.md` | D-01, D-04 | SKILL.md | - | - | 기업·기관의 CIL 기반 근거 분석을 라우팅한다. | - |
| C03-002 | CREATE | `.codex/skills/company-intelligence-analysis/agents/openai.yaml` | D-01, D-04 | openai.yaml | - | - | 발견 가능한 UI 메타데이터를 제공한다. | - |
| C03-003 | CREATE | `.codex/skills/company-intelligence-analysis/references/analysis-routing.md` | D-01, D-04 | analysis-routing.md | - | - | CIL 명령과 분석 목적 매핑을 제공한다. | - |
| C03-004 | CREATE | `.codex/skills/company-intelligence-analysis/references/output-contract.md` | D-01, D-04 | output-contract.md | - | - | 상태·근거·한계 출력 계약을 제공한다. | - |
| C03-005 | CREATE | `.codex/skills/company-intelligence-analysis/scripts/verify_cil_artifact.py` | D-01, D-04 | verify_cil_artifact.py | - | - | CIL artifact와 evidence bundle 참조를 검증한다. | - |

### Routed skills

- `create-company-skill` → `skill-creator` (IMPLEMENT, required): CIL thin orchestration 스킬을 생성한다.

### Completion criteria

- `company-skill-quick-validate` [planned] `skill-creator` phase=VALIDATE, depends=-: python3 /home/ubuntu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/company-intelligence-analysis

