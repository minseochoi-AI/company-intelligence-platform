# Implementation plan: company-intelligence-cross-region-career-preparation--C-01-source-identity-foundation--r1

Status: `contract-ready`

## source-identity-capability-foundation: 28개 원자 API의 접근·필드·활성화 정책을 단일 catalog로 검증하고, 법인 identity와 capability/분석 적격성을 근거 단위로 저장·분류한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-e1e3c60c9a87 | MODIFY | `config/providers.json` | D-01-source-access-policy | providers, atomic_operations, activation_policy | sha256:3366d63c0e10e456e3024e0669a64982420ee70bc013beff009fd0c6af828d5d | - | 각 원자 작업에 region, access_mode, data_role, required_paths, field_semantics, quota, license, last_verified, activation_policy를 선언한다. | - |
| file-change-538214ac8333 | MODIFY | `sql/duckdb_schema.sql` | D-02-company-capability-taxonomy, D-04-career-requirement-verification | company_source_capability, identifier_mapping, field_availability, classification_history, job_requirement, credential_evidence, requirement_verification, source_excerpt | sha256:37cb68ba7983a2f11f4c086bbdaf319711f0b3e22a4cac165d90071f65a283c2 | - | 기업·source·필드·시점·근거를 분리한 additive 테이블과 FK/유일성 제약을 추가한다. | 요건 주장, evidence scope, 검증 상태, 원문 locator를 분리한 additive 테이블을 추가한다. | - |
| file-change-ba1af64467c1 | MODIFY | `src/company_intel/models.py` | D-01-source-access-policy, D-02-company-capability-taxonomy, D-03-search-profile-and-discovery, D-04-career-requirement-verification | SourcePolicy, AtomicFieldContract, ProviderHealth, Capability, CompanyClassification, AnalysisEligibility, Provenance, SearchProfile, CountryAllocation, CandidateMatch, ExclusionReason, RequirementStatus, EvidenceScope, VerificationStatus, RequirementAvailability | sha256:ad84062f97673e08a5d4163530d27c524af3ba903d2a06e873c7c7515a075052 | - | 접근 모드·필드 계약·검증 시각·실패 범주를 불변 모델로 정의한다. | finance, job_posting, employment, market, macro capability와 exclusion reason을 타입화한다. | 명시적 입력만 담는 SearchProfile과 국가 배분·근거·제외 사유 모델을 추가한다. | 공고 직접 근거·국가 baseline·crosswalk·unavailable 상태를 분리한다. | - |
| file-change-954e39bf4b3a | CREATE | `src/company_intel/source_catalog.py` | D-01-source-access-policy | SourceCatalog, load_source_catalog, validate_atomic_contract, evaluate_activation | - | - | catalog 로드·schema 검증·freshness·activation gate·redacted 진단을 한 모듈이 제공한다. | - |
| file-change-bdb2949cb581 | CREATE | `src/company_intel/identity.py` | D-02-company-capability-taxonomy, D-03-search-profile-and-discovery | CompanyIdentityResolver, IdentifierLink, ResolutionResult, resolve_candidate_company, explain_resolution | - | - | identifier type/value/source/as_of/confidence를 보존하며 후보 법인을 결정론적으로 연결한다. | 검색 후보는 해소된 법인 ID 또는 명시적 unresolved 이유와 confidence를 갖는다. | - |
| file-change-58fda9542e8a | CREATE | `src/company_intel/normalization.py` | D-02-company-capability-taxonomy | AtomicObservationMapper, normalize_unit, deduplication_key | - | - | 원자 필드 의미, 단위, period, available_at, source locator를 손실 없이 표준 observation으로 변환한다. | - |
| file-change-c2dd27200b1c | CREATE | `src/company_intel/classification.py` | D-02-company-capability-taxonomy | classify_company, evaluate_analysis_eligibility, CapabilityGate | - | - | 독립 capability 축과 근거 충분성 gate로 기업을 다중 분류하고 이유 코드를 반환한다. | - |
| file-change-50ab952c86b5 | MODIFY | `src/company_intel/connectors/registry.py` | D-01-source-access-policy, D-03-search-profile-and-discovery, D-04-career-requirement-verification | ConnectorRegistry, select_adapter, probe_vs_production, discovery_adapters, requirement_evidence_adapters | sha256:3f9e38e145a9e35a3f2ee46914fad85623d13abff0263bd0091cbef004ec7220 | - | 승인된 operation ID와 용도에 맞는 adapter만 선택하고 미충족 gate는 구조화 오류로 반환한다. | discovery 가능 source만 검색 universe 구성에 노출한다. | requirement evidence를 제공하는 adapter만 상세 요건 pipeline에 등록한다. | - |
| file-change-51ccd281e59c | MODIFY | `src/company_intel/validation.py` | D-01-source-access-policy | ValidationOutcome, classify_provider_error, redacted_receipt | sha256:927a93efe71898fdc531544840c854eafa1ad3a3d4591db4d717e5f6be3e69f8 | - | transport, provider result, required field, semantic freshness를 각각 판정하고 비밀 제거 receipt를 만든다. | - |
| file-change-42c469cea05e | MODIFY | `src/company_intel/warehouse.py` | D-02-company-capability-taxonomy, D-04-career-requirement-verification, D-05-spreadsheet-output-contract | upsert_identity, upsert_capability, record_field_availability, record_classification, store_job_snapshot, store_requirement_evidence, query_export_bundle, materialize_export_snapshot | sha256:6cc623eed35be3ff01209f0b9ce4566db410f4c2441644930fdc013d545303e5 | - | 법인 식별자, 원자 observation, capability, 분류 이력을 멱등 적재한다. | 공고 as_of, 만료 상태, 요건 claim, locator, verification 결과를 증분 저장한다. | 동일 snapshot에서 companies, capabilities, jobs, requirements, sources, exclusions를 결정론적으로 조회한다. | - |
| file-change-d0c6f2fbd963 | CREATE | `tests/test_source_catalog.py` | D-01-source-access-policy | test_all_28_atomic_operations_are_declared, test_activation_gates_and_redaction | - | - | 28개 작업 완전성, 필수 필드, freshness, probe/production 경계, secret redaction을 fixture로 검증한다. | - |
| file-change-7a2cfff77575 | CREATE | `tests/test_classification.py` | D-02-company-capability-taxonomy | test_atomic_capability_classes, test_analysis_eligibility_gates | - | - | 다중 capability와 exclusion reason, identifier ambiguity, period/unit 부족을 표로 검증한다. | - |

### Routed skills

- `c01-tdd` → `tdd` (IMPLEMENT, required): source catalog와 분류 계약을 fixture 기반 red-green-refactor로 구현
- `c01-verify` → `verification-before-completion` (VALIDATE, required): 계획 해시와 독립 테스트 결과를 확인

### Completion criteria

- `C-01-catalog-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 28개 원자 source catalog와 activation/redaction 계약이 통과한다.
- `C-01-classification-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=C-01-catalog-tests: 기업 capability와 분석 적격성 분류 fixture가 통과한다.
