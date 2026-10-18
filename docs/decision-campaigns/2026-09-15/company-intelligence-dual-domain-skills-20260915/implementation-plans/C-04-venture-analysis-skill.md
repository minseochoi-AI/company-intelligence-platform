# Implementation plan: C-04-venture-analysis-skill-plan-r1

Status: `contract-ready`

## C-04-venture-analysis-skill-slice: 승인된 결정을 파일 단위로 구현하고 독립 검증한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| C04-001 | CREATE | `.codex/skills/kr-defensible-venture-discovery/SKILL.md` | D-01, D-05 | SKILL.md | - | - | 한국형 방어가능 창업기회를 제약과 근거로 조사한다. | - |
| C04-002 | CREATE | `.codex/skills/kr-defensible-venture-discovery/agents/openai.yaml` | D-01, D-05 | openai.yaml | - | - | 발견 가능한 UI 메타데이터를 제공한다. | - |
| C04-003 | CREATE | `.codex/skills/kr-defensible-venture-discovery/references/market-archetypes.md` | D-01, D-05 | market-archetypes.md | - | - | 경쟁·틈새·미개척 후보의 증거 기준을 정의한다. | - |
| C04-004 | CREATE | `.codex/skills/kr-defensible-venture-discovery/references/research-workflow.md` | D-01, D-05 | research-workflow.md | - | - | 설정·baseline·gap·증강조사 상태 전이를 정의한다. | - |
| C04-005 | CREATE | `.codex/skills/kr-defensible-venture-discovery/references/evidence-and-barriers.md` | D-01, D-05 | evidence-and-barriers.md | - | - | 원천 권리와 방어력·자원 적합성 경계를 정의한다. | - |
| C04-006 | CREATE | `.codex/skills/kr-defensible-venture-discovery/references/venture-session.schema.json` | D-01, D-05 | venture-session.schema.json | - | - | 창업 조사 세션을 검증한다. | - |
| C04-007 | CREATE | `.codex/skills/kr-defensible-venture-discovery/references/opportunity-hypothesis.schema.json` | D-01, D-05 | opportunity-hypothesis.schema.json | - | - | 시장 유형별 후보 가설을 검증한다. | - |
| C04-008 | CREATE | `.codex/skills/kr-defensible-venture-discovery/scripts/venture_artifacts.py` | D-01, D-05 | venture_artifacts.py | - | - | 창업 artifact를 검증하고 gap을 계산한다. | - |

### Routed skills

- `create-venture-skill` → `skill-creator` (IMPLEMENT, required): 한국형 창업시장 발굴 스킬을 생성한다.

### Completion criteria

- `venture-skill-quick-validate` [planned] `skill-creator` phase=VALIDATE, depends=-: python3 /home/ubuntu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/kr-defensible-venture-discovery

