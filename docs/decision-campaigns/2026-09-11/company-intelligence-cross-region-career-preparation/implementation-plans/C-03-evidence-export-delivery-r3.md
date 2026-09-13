# Implementation plan: company-intelligence-cross-region-career-preparation--C-03-evidence-export-delivery--r3

Status: `contract-ready`

## run-lineage-and-export-r3: 선택한 facet, 원천 coverage, verdict 및 출력 파일을 하나의 offline run manifest로 묶어 explain/export가 같은 판단 근거를 사용하게 한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-05-run-manifest-r3 | CREATE | `src/company_intel/run_manifest.py` | D-05-spreadsheet-output-contract | build_run_manifest, write_run_manifest | - | - | 비밀을 제외한 input·coverage·field provenance·output hash를 재현 가능한 run manifest로 작성한다. | - |
| D-05-export-verdict-tables-r3 | MODIFY | `src/company_intel/exporting.py` | D-05-spreadsheet-output-contract | build_export_bundle, build_export_manifest | sha256:fb35b38c109adfdca8089dc1bf518c0f8bd5cd4581ed8bea332e69dfdfb8b663 | - | strict, unverifiable, no-match, conflict, facets, run manifest를 evidence-first CSV/XLSX bundle에 포함한다. | D-05-run-manifest-r3 |
| D-05-export-reporting-r3 | MODIFY | `src/company_intel/reporting.py` | D-05-spreadsheet-output-contract | render_verdict_counts, render_run_lineage_summary | sha256:d51564683a2d6310d825f903b49ee2d7ff7dd0a5d857ab3029a6f71195f0d741 | - | 사용자에게 적용 조건, 제외/검사 불가, source coverage를 함께 요약한다. | D-05-run-manifest-r3 |
| D-05-export-tests-r3 | MODIFY | `tests/test_exporting.py` | D-05-spreadsheet-output-contract | test_export_bundle, test_verdict_and_lineage_export | sha256:ff48347e5b0c9b789bfe46370c6a10a83b6819b523b242ae204c2f2a475cc176 | - | 새 verdict/facet/run manifest table과 sanitizer를 offline으로 검증한다. | D-05-export-verdict-tables-r3 |
| D-05-run-manifest-tests-r3 | CREATE | `tests/test_run_manifest.py` | D-05-spreadsheet-output-contract | test_run_manifest_redacts_sensitive_values | - | - | input, coverage, fields, output hashes가 남고 secret이 남지 않는지 검증한다. | D-05-run-manifest-r3 |

### Routed skills

- `export-implementation` → `decision-campaign-workbook` (IMPLEMENT, required): evidence/run receipt를 연결한다.
- `export-tests` → `tdd` (VALIDATE, required): offline export contract를 검증한다.

### Completion criteria

- `C03-r3-export-lineage-tests` [planned] `tdd` phase=VALIDATE, depends=-: export와 run manifest가 verdict·coverage·sanitization을 보존한다.

