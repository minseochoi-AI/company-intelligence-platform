# Implementation plan: company-intelligence-cross-region-career-preparation--C-03-evidence-export-delivery--r2

Status: `contract-ready`

## verdict-lineage-export-r2: strict match, unverifiable, no-match, conflict와 source lineage를 서로 다른 표로 내보내고 CSV/XLSX parity와 비밀·PII·수식 방어를 유지한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-05-export-verdicts-r2 | MODIFY | `src/company_intel/exporting.py` | D-05-spreadsheet-output-contract | TABLE_HEADERS, ExportBundle, render_csv_bundle, render_xlsx_workbook, build_export_manifest | sha256:baf639878d180901ba4e883b4524d9dcf24d69f132114c37c859b353e931485d | - | companies/jobs/locations/requirements/overlap/strict_matches/unverifiable/exclusions/conflicts/sources/runs를 안정적 관계키와 schema version으로 반환한다. | - |
| D-05-reporting-r2 | MODIFY | `src/company_intel/reporting.py` | D-05-spreadsheet-output-contract | render_export_summary, render_provider_limitations, render_verdict_counts | sha256:d29597658dc2bec27e69e0f3a82bcf6f6c4900316ad60b675340ca9783969232 | - | CLI run별 입력 profile, snapshot, source disposition, verdict 개수, 검사 불가 이유와 분석 부적격을 한국어로 요약한다. | - |
| D-05-security-r2 | MODIFY | `src/company_intel/security.py` | D-05-spreadsheet-output-contract | sanitize_export_value, ExportFieldPolicy, validate_output_directory, drop_restricted_fields | sha256:7264c2c705d4a0f57fad90193c551d955da455011aae49eae8cda4ddbef9b422 | - | 테이블별 허용열 정책으로 ALIO·MPSV 연락처, credential, 제한 원문과 formula payload를 제거하고 provenance locator만 남긴다. | - |
| D-05-export-tests-r2 | MODIFY | `tests/test_exporting.py` | D-05-spreadsheet-output-contract | test_verdict_tables, test_source_lineage, test_csv_xlsx_parity, test_export_redaction, test_deterministic_manifest | sha256:a6b457853d5acc7b37bfba87771fef84de5b47691f55d42c4c188cc682153a18 | - | 모든 판정표의 관계 무결성, CSV/XLSX parity, 안정적 hash, PII/secret/formula 제거와 empty/unknown 결과를 검증한다. | - |

### Routed skills

- `c03-r2-tdd` → `tdd` (IMPLEMENT, required): verdict/source 관계와 export 보안을 테스트 우선 구현
- `c03-r2-verify` → `verification-before-completion` (VALIDATE, required): CSV/XLSX parity와 redaction 독립 검증

### Completion criteria

- `C-03-r2-export-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 판정별 표, lineage, deterministic manifest, CSV/XLSX parity와 redaction이 통과한다.
