# Implementation plan: company-intelligence-cross-region-career-preparation--C-03-evidence-export-delivery--r1

Status: `contract-ready`

## evidence-first-spreadsheet-delivery: 동일 snapshot의 기업·capability·공고·요건·원천·제외를 관계형 CSV bundle과 선택적 XLSX로 안전하고 결정론적으로 반환한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-82feda91e73b | CREATE | `src/company_intel/exporting.py` | D-05-spreadsheet-output-contract | ExportBundle, render_csv_bundle, render_xlsx_workbook, build_export_manifest | - | - | versioned headers와 안정적 row key/order를 가진 CSV bundle을 기준 계약으로 만들고 동일 데이터를 XLSX sheet로 렌더링한다. | - |
| file-change-c46a3c2c1704 | MODIFY | `src/company_intel/reporting.py` | D-05-spreadsheet-output-contract | render_export_summary, render_provider_limitations, render_korean_guidance | sha256:8fa8e14a4fc9ec2c0f9542e3de94922b8c97423f60bc5c706d8f2e3ce5fdfac2 | - | export manifest, source freshness, unavailable/exclusion 통계, 한국어 사용 안내를 생성한다. | - |
| file-change-36b865e1eb42 | MODIFY | `src/company_intel/security.py` | D-05-spreadsheet-output-contract | sanitize_export_value, ExportFieldPolicy, validate_output_directory | sha256:05961908ffc8906b1732303119c33ad5ee5c305884126e6d7eeb6375514ab399 | - | secret/PII/restricted text 제거, CSV formula injection 방지, output path 경계 검증을 제공한다. | - |
| file-change-50c86b7ed8ac | MODIFY | `pyproject.toml` | D-05-spreadsheet-output-contract | project.dependencies, openpyxl | sha256:6f163cb3fc098b808c134abfbd27438ab9270475511d11a4ec0c13c31b863400 | - | 검토된 openpyxl 3.1 호환 범위를 XLSX extra 또는 직접 의존성으로 명시하고 lockfile 갱신을 구현 단계에 수행한다. | - |
| file-change-c1f9750959a4 | CREATE | `tests/test_exporting.py` | D-05-spreadsheet-output-contract | test_csv_contract, test_xlsx_parity, test_export_redaction, test_deterministic_bundle, test_empty_limited_output | - | - | CSV/XLSX parity, 정렬, hyperlinks, mandatory evidence/exclusion, formula/secret redaction, empty/limited output을 검증한다. | - |

### Routed skills

- `c03-tdd` → `tdd` (IMPLEMENT, required): CSV 기준 계약과 XLSX parity/redaction을 테스트 우선 구현
- `c03-verify` → `verification-before-completion` (VALIDATE, required): 계획 해시와 독립 export 테스트 확인

### Completion criteria

- `C-03-export-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: CSV bundle과 XLSX가 동일 관계 데이터·근거·제외를 안전하고 결정론적으로 반환한다.
