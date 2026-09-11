# Implementation plan: company-intelligence-cross-region-career-preparation--C-01-source-identity-foundation--r2

Status: `contract-ready`

## semantic-provider-identity-foundation-r2: 28개 등록 operation과 MPSV 후보를 probe·production·context·proxy로 분리하고, 원문 손실 없는 fact와 법인·단위·시점·5상태 가용성 계약을 CLI의 공통 기반으로 만든다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-01-provider-catalog-r2 | MODIFY | `config/providers.json` | D-01-source-access-policy | atomic_operations, provider_disposition, semantic_contract | sha256:d8d0f64418df17737cee247f1ff9f2eb50ac9b316371d3cda2d04f39db572e64 | - | operation마다 cluster, lifecycle, usable fields, forbidden uses, semantic validators, production eligibility를 선언하고 BEA catalog·OECD CZ·context/proxy를 사용자 검색에서 격리한다. | - |
| D-01-env-contract-r2 | MODIFY | `.env.example` | D-01-source-access-policy | SEC_USER_AGENT, provider activation examples | sha256:4fef9c61ef28bd656858387f99f9569085b3e918d25363a83427c4e602f8a0a3 | - | placeholder가 운영 준비로 통과하지 않도록 비밀이 아닌 configuration 요구사항과 예시 형식을 명시한다. | - |
| D-01-k3s-config-r2 | MODIFY | `deploy/k3s/secret.example.yaml` | D-01-source-access-policy | SEC_USER_AGENT, provider configuration placeholders | sha256:19c9d9fe8321953701b64b15c8373451216381787029d1131865bd23168c8c67 | - | SEC 식별 문자열과 API key placeholder를 구분하고 실제 값 커밋 금지를 표시한다. | - |
| D-01-lossless-base-r2 | MODIFY | `src/company_intel/connectors/base.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | compact, to_decimal, preserve_payload | sha256:b4e9a42028123d2575c780d3d9b6198bf4b27d383ed5572386891838308b7cd8 | - | compact는 preview 전용으로 명명·표시하고 production normalizer는 전체 행을 보존하며 금액은 Decimal 안전 변환을 제공한다. | - |
| D-01-keyed-semantics-r2 | MODIFY | `src/company_intel/connectors/keyed.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | _dart, _ecos, _alio_plus, _public_employment, _alpha | sha256:951e2c73427e63ae5f8befb628dc45ceda0ff444bcf682175708af62f8fc7f32 | - | 각 원천을 전체 복합키·요청/반환 주기·codebook 상태·price adjustment와 함께 보존하고 목록-only 제약을 명시한다. | - |
| D-01-keyless-semantics-r2 | MODIFY | `src/company_intel/connectors/keyless.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | _greenhouse, _lever, keyless_probes, SDMX and JSON-stat normalizers | sha256:2f44850263221028d0b46c52b73a4daa297c441a679ebdc33e8900289e56b467 | - | provider별 전체 행을 원자화하고 다중 위치·급여 tier·series signature·pagination·notice revision을 보존한다. | - |
| D-01-catalog-validator-r2 | MODIFY | `src/company_intel/source_catalog.py` | D-01-source-access-policy | SourceCatalog, validate_atomic_contract, evaluate_activation | sha256:3e0236390e1fdc10542ff7f9d0749c327b585d943589bf3c4adc60ddfe6e13a0 | - | catalog/probe field contract parity, lifecycle, cluster, forbidden-use, nonempty/type/domain validator를 검사한다. | - |
| D-01-runtime-validator-r2 | MODIFY | `src/company_intel/validation.py` | D-01-source-access-policy | validate, SemanticFieldCheck, _provider_error | sha256:0d9a12a86a8ac272140f4759d6f62b8bc8f99a76a64bc590202d42b6b2c3919d | - | transport/provider/schema/value/coverage/freshness/production-readiness를 독립 상태로 검증하고 SEC placeholder와 ALIO 빈 값을 실패시킨다. | - |
| D-01-provider-clusters-r2 | CREATE | `src/company_intel/provider_clusters.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | ProviderCluster, ProviderDisposition, select_operations | - | - | job, requirement, identity, financial, macro, public-demand, activity-proxy와 health-fixture를 분리하고 금지된 cross-cluster 사용을 거부한다. | - |
| D-01-registry-routing-r2 | MODIFY | `src/company_intel/connectors/registry.py` | D-01-source-access-policy | build_probes, production_adapters, select_by_cluster | sha256:8b9f4feb73b124014ae8841c65bfa581f08724cf7143001a1ce942bdfee73f3e | - | health fixture와 production adapter를 분리하고 cluster·region·capability·activation 상태로 선택한다. | - |
| D-02-model-contract-r2 | MODIFY | `src/company_intel/models.py` | D-02-company-capability-taxonomy | SearchVerdict, AtomicFact, ComparabilitySignature, SourceDisposition | sha256:df78975ecedb36bd05d67967552ed16dffdbfec78313478a5f4f6530aa2a0dda | - | 5상태 verdict, 원자 fact, source lifecycle과 비교 가능 signature를 공통 불변 모델로 정의한다. | - |
| D-02-normalization-r2 | MODIFY | `src/company_intel/normalization.py` | D-02-company-capability-taxonomy | AtomicObservationMapper, comparability_signature, deduplication_key | sha256:aa5e5c87ce3ebe464187e07a8a712ad9529d0ba99602297f45a9ee526f7fbf49 | - | job/financial/macro/procurement/activity fact별 원자키와 비교 signature를 생성하고 preview 손실물을 거부한다. | - |
| D-02-identity-r2 | MODIFY | `src/company_intel/identity.py` | D-02-company-capability-taxonomy | CompanyIdentityResolver, ResolutionResult, IdentifierLink | sha256:085083665a28e8a1ac3ce52e18e20764cd95fd144f0d6b18dffb647c75e5e72b | - | CIK·DART corp code·LEI·IČO·기관 ID를 namespace별로 유지하고 resolved/unresolved/conflict와 근거를 반환한다. | - |
| D-02-classification-r2 | MODIFY | `src/company_intel/classification.py` | D-02-company-capability-taxonomy | classify_company, evaluate_analysis_eligibility, CapabilityGate | sha256:0ffb76635f1153c26f49a35d58d5e3c7ebc23e022dd620c67ff016a2dea7b0ba | - | provider cluster와 fact coverage를 기준으로 job-only, financial-only, context-only, proxy-only와 correlation/causal ineligible를 독립 판정한다. | - |
| D-02-warehouse-r2 | MODIFY | `src/company_intel/warehouse.py` | D-02-company-capability-taxonomy | store_atomic_fact, store_source_snapshot, resolve_current_fact, store_verdict | sha256:b9691ca3794875eefc3922d387baa0fcfcc78301db6564ebe073977e5ae5b2ff | - | source snapshot, lossless fact, identity link, verdict와 run을 멱등 복합키로 저장하고 preview artifact를 거부한다. | - |
| D-02-schema-r2 | MODIFY | `sql/duckdb_schema.sql` | D-02-company-capability-taxonomy | source_snapshot, atomic_fact, entity_identifier, search_verdict, fact_revision | sha256:fe701d386efa4dcd77385f8ca4c694a9e1404718d9dd18fae80aceddec9812f2 | - | 원자 fact 유형별 복합키와 lineage, multi-value child row, verdict/exclusion을 additive 테이블로 고정한다. | - |
| D-01-source-tests-r2 | MODIFY | `tests/test_source_catalog.py` | D-01-source-access-policy | test_catalog_probe_semantic_parity, test_disposition_and_activation, test_placeholder_rejected | sha256:e865b19704ee59deaa033c28640406b2d88e1c6ae4f4957812437798cfd46b9e | - | ALIO·OECD·IMF·World Bank·SEC 사례와 cluster/disposition parity를 검증한다. | - |
| D-01-connector-tests-r2 | MODIFY | `tests/test_public_connectors.py` | D-01-source-access-policy, D-02-company-capability-taxonomy | test_lossless_provider_normalizers, test_provider_error_bodies, test_multi_value_preservation | sha256:a613e53829ca7e03c2411261cfb175ba59dabaa7de98f91759840b825e214459 | - | 14개 truncation 사례와 BEA body error, SEC facts, SDMX/JSON-stat, ARES NACE, CNB amount를 최소 fixture로 검증한다. | - |
| D-02-classification-tests-r2 | MODIFY | `tests/test_classification.py` | D-02-company-capability-taxonomy | test_context_and_proxy_not_promoted, test_identity_conflict_blocks_join, test_five_state_capabilities | sha256:10ecd0d514f32a5a7169bdbc26b1f6f1f5df9f0935c069ce85463fa8c4f1b57a | - | context/proxy 격리, unresolved/conflict, correlation/causal 부적격을 검증한다. | - |

### Routed skills

- `c01-r2-tdd` → `tdd` (IMPLEMENT, required): 실제 반환물 모양의 offline fixture로 semantic contract를 먼저 고정
- `c01-r2-research` → `company-intelligence-career-research` (IMPLEMENT, required): 공식 필드 의미와 검색 금지 경계를 유지
- `c01-r2-verify` → `verification-before-completion` (VALIDATE, required): 계획 해시와 source/catalog/connector/classification 테스트 검증

### Completion criteria

- `C-01-r2-semantic-contract-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: catalog parity, nonempty/type/body error, lossless normalization, cluster disposition과 identity/capability 상태가 offline 실제형 fixture에서 통과한다.
