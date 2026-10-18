# Implementation plan: C-06-diagram-toolchain-plan-r1

Status: `contract-ready`

## diagram-toolchain: 저장소가 evidence·design·matrix를 검증하고 고정 Mermaid CLI로 SVG와 PNG를 생성·검사한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-bc37d034bad5 | MODIFY | `.gitignore` | D-11 | tools/mermaid-renderer/node_modules/ | sha256:c20e0dc819751315e627678e640e413aafce4abbbd594a18981c29afa27b799b | - | renderer-local node_modules is ignored without ignoring package-lock.json | - |
| file-change-cadd50729db0 | CREATE | `tools/flowchart_matrix.py` | D-11 | validate_evidence, validate_design, validate, build | - | - | standard-library CLI validates semantic inputs, compiles Mermaid, renders SVG/PNG, and rejects stale derivatives | file-change-970fbb67544b, file-change-b9c763c03407, file-change-2cb2323e87c8 |
| file-change-2cb2323e87c8 | CREATE | `tools/mermaid-renderer/package.json` | D-11 | devDependencies.@mermaid-js/mermaid-cli, devDependencies.puppeteer | - | - | local renderer manifest pins Mermaid CLI 11.17.0 and compatible Puppeteer | - |
| file-change-11fe041e9525 | CREATE | `tools/mermaid-renderer/package-lock.json` | D-11 | lockfileVersion, packages | - | - | npm lockfile records exact package integrity and transitive graph | file-change-2cb2323e87c8 |
| file-change-970fbb67544b | CREATE | `tools/mermaid-renderer/mermaid.config.json` | D-11 | securityLevel, theme | - | - | strict, fixed Mermaid rendering configuration | - |
| file-change-b9c763c03407 | CREATE | `tools/mermaid-renderer/puppeteer.local.json` | D-11 | executablePath, args | - | - | renderer explicitly uses /usr/bin/google-chrome with local headless flags | - |
| file-change-46574042dc93 | CREATE | `tests/tools/test_flowchart_matrix.py` | D-11 | test_validates_and_compiles, test_rejects_invalid_matrix | - | - | focused semantic validation and stale derivative tests | file-change-cadd50729db0 |
| file-change-368e35f4988c | CREATE | `tests/tools/test_mermaid_renderer.py` | D-11 | test_renders_svg_and_png, test_rejects_invalid_mermaid | - | - | real local mmdc integration tests prove SVG/PNG, invalid source, and check behavior | file-change-cadd50729db0, file-change-11fe041e9525 |

### Routed skills

- `deepwiki-mermaid-cli-boundary` → `deepwiki-code-implementation` (IMPLEMENT, required): CLI·Puppeteer 경계를 구현한다.
- `flowchart-matrix-contract` → `flowchart-matrix-validation` (VALIDATE, required): semantic flowchart contract를 저장소 CLI로 검증한다.
- `campaign-regression-orchestration` → `decision-campaign-workbook` (VALIDATE, required): repository-wide regression criterion을 소유한다.

### Completion criteria

- `flowchart-matrix-pytest` [planned] `flowchart-matrix-validation` phase=VALIDATE, depends=-: semantic validation, Mermaid compilation, and stale-source rejection work without the external skill path
- `mermaid-renderer-pytest` [planned] `deepwiki-code-implementation` phase=VALIDATE, depends=-: pinned local mmdc with explicit Chrome renders SVG/PNG and rejects invalid source or stale artifacts
- `repository-regression-pytest` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-: new diagram toolchain does not regress the repository test suite

