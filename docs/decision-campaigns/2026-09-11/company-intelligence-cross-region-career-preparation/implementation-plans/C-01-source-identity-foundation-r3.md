# Implementation plan: company-intelligence-cross-region-career-preparation--C-01-source-identity-foundation--r3

Status: `contract-ready`

## provider-native-taxonomy-and-facets-r3: 법인·공공기관·공고 조직단위의 서로 다른 의미를 합치지 않고, 원천 namespace와 증거 상태를 유지한 facet catalog를 만든다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-02-taxonomy-model-r3 | MODIFY | `src/company_intel/models.py` | D-02-company-capability-taxonomy | TaxonomyFact, FacetAvailability, CompanyClassification | sha256:6c54b354368caf47d20585a4ebb252562516b9f07e3075311eeb825ea370757f | - | 법인/기관 taxonomy와 facet availability를 명시적으로 표현하는 불변 모델을 제공한다. | - |
| D-02-taxonomy-classification-r3 | MODIFY | `src/company_intel/classification.py` | D-02-company-capability-taxonomy | classify_company, classify_taxonomy_axes | sha256:675ede9bb03fd1fd30d21f7ae3f26b15cb651f7c23b8ed3e98f7dabb11e24a36 | - | 소유 부문, 공공기관 유형, 법적 형태, 산업, 시장 상태, 공고 조직단위를 독립 축으로 분류한다. | D-02-taxonomy-model-r3 |
| D-01-nested-field-resolution-r3 | MODIFY | `src/company_intel/normalization.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | AtomicObservationMapper, resolve_field_path | sha256:1ae5213b9d6ed62c7bbc6f6c179f90facd3730a14df489ce17a20eda71309f14 | - | dotted/nested 원천 필드를 lossless하게 추출하고, 단일 의미를 강제로 평탄화하지 않는다. | - |
| D-01-field-capability-catalog-r3 | MODIFY | `src/company_intel/source_catalog.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | SourceCatalog, field_capabilities | sha256:4b5494236973e11f0213c381d15b9552c4e48adf2dcc9830b0c9e28760c0c6d0 | - | provider-native field capability와 금지된 통합 용도를 선언한다. | - |
| D-02-taxonomy-module-r3 | CREATE | `src/company_intel/taxonomy.py` | D-02-company-capability-taxonomy | taxonomy_facts_from_record, TAXONOMY_AXES | - | - | ARES, GLEIF, SEC, ALIO, MPM과 ATS business unit을 명시적 축과 evidence 상태로 변환한다. | D-02-taxonomy-model-r3 |
| D-02-facet-catalog-r3 | CREATE | `src/company_intel/facets.py` | D-02-company-capability-taxonomy | FacetDefinition, FacetOption, build_job_facets, build_taxonomy_facets | - | - | 저장된 snapshot에서 선택지 수, provider coverage, evidence 상태, disabled 사유를 가진 facet catalog를 생성한다. | D-02-taxonomy-module-r3, D-01-field-capability-catalog-r3 |
| D-02-classification-tests-r3 | MODIFY | `tests/test_classification.py` | D-02-company-capability-taxonomy | test_classify_company, test_taxonomy_axes | sha256:51b5bb54d4773218684d03452b664d8a5a6a98e3a37786d5a0d003c59b72f65b | - | 서로 다른 legal/public/business axes가 합쳐지지 않는 회귀 사례를 추가한다. | D-02-taxonomy-classification-r3 |
| D-02-taxonomy-tests-r3 | CREATE | `tests/test_taxonomy.py` | D-02-company-capability-taxonomy | test_provider_native_taxonomy | - | - | ARES/GLEIF/SEC/ALIO/MPM/ATS 최소 반환 형태를 offline으로 검증한다. | D-02-taxonomy-module-r3 |
| D-02-facet-tests-r3 | CREATE | `tests/test_facets.py` | D-02-company-capability-taxonomy | test_dynamic_facet_availability | - | - | unknown-only 회사 유형과 구조화되지 않은 급여를 disabled/display-only로 반환하는 사례를 검증한다. | D-02-facet-catalog-r3 |

### Routed skills

- `taxonomy-implementation` → `company-intelligence-career-research` (IMPLEMENT, required): provider field semantics를 보존한다.
- `taxonomy-validation` → `tdd` (VALIDATE, required): offline taxonomy/facet regression을 실행한다.

### Completion criteria

- `C01-r3-taxonomy-facet-tests` [planned] `tdd` phase=VALIDATE, depends=-: 원천 namespace와 facet availability가 회귀 없이 동작한다.
