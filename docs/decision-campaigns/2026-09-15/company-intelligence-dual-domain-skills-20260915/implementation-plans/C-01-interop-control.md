# Implementation plan: C-01-interop-control-plan-r1

Status: `contract-ready`

## C-01-interop-control-slice: 승인된 결정을 파일 단위로 구현하고 독립 검증한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| C01-001 | CREATE | `.codex/shared/company-intelligence-interop/domain-plan.schema.json` | D-02 | domain-plan.schema.json | - | - | career와 venture DomainPlan의 공통 구조를 검증한다. | - |
| C01-002 | CREATE | `.codex/shared/company-intelligence-interop/domain-plan-ref.schema.json` | D-02, D-10 | domain-plan-ref.schema.json | - | - | DomainPlan 외부 참조의 hash와 kind를 검증한다. | - |
| C01-003 | CREATE | `.codex/shared/company-intelligence-interop/evidence-bundle.schema.json` | D-03 | evidence-bundle.schema.json | - | - | 증거 bundle manifest를 검증한다. | - |
| C01-004 | CREATE | `.codex/shared/company-intelligence-interop/evidence-bundle-ref.schema.json` | D-03 | evidence-bundle-ref.schema.json | - | - | 증거 bundle 참조를 검증한다. | - |
| C01-005 | CREATE | `.codex/shared/company-intelligence-interop/dual-path-comparison.schema.json` | D-10 | dual-path-comparison.schema.json | - | - | career와 venture 비교 결과를 검증한다. | - |
| C01-006 | CREATE | `.codex/shared/company-intelligence-interop/campaign-link.schema.json` | D-07 | campaign-link.schema.json | - | - | 외부 campaign link를 검증한다. | - |
| C01-007 | CREATE | `.codex/shared/company-intelligence-interop/connector-candidates.json` | D-06 | connector-candidates.json | - | - | 무료 connector 후보를 production 의존성 없이 기록한다. | - |
| C01-008 | CREATE | `.codex/shared/company-intelligence-interop/BOUNDARIES.md` | D-01, D-03, D-06, D-07, D-10 | BOUNDARIES.md | - | - | 세 스킬과 공통 계약의 소유권 경계를 설명한다. | - |
| C01-009 | CREATE | `.codex/shared/company-intelligence-interop/interop.py` | D-02, D-03, D-10 | interop.py | - | - | hash 검증과 DualPathComparison 생성을 결정론적으로 수행한다. | - |

### Routed skills

- `skill-create-contracts` → `skill-creator` (IMPLEMENT, required): 두 스킬의 공통 계약을 간결하고 검증 가능하게 구성한다.

### Completion criteria

- `interop-self-test` [planned] `skill-creator` phase=VALIDATE, depends=-: python3 .codex/shared/company-intelligence-interop/interop.py self-test

