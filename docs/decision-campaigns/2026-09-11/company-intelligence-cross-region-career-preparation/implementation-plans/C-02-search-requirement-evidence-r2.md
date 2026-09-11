# Implementation plan: company-intelligence-cross-region-career-preparation--C-02-search-requirement-evidence--r2

Status: `contract-ready`

## atomic-profile-requirement-verdict-r2: 현재 17개 검색 변수를 직무·위치·근로계약·언어·급여·기업·요건의 독립 축으로 확장하고 모든 조건을 MATCH/NO_MATCH/UNKNOWN/CONFLICT/NOT_APPLICABLE로 판정한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-03-query-contract-r2 | CREATE | `src/company_intel/query_contract.py` | D-03-search-profile-and-discovery, D-04-career-requirement-verification | AtomicSearchProfile, FilterVerdict, UnknownPolicy, combine_verdicts, ComparabilityPolicy | - | - | 제목/본문/직업코드, 다중 위치/remote 범위, 근로시간/계약기간, 공고언어/요구언어, 급여 basis/gross-net/FX와 source policy를 독립 필드로 정의한다. | - |
| D-03-company-search-r2 | MODIFY | `src/company_intel/search.py` | D-03-search-profile-and-discovery | validate_search_profile, build_company_universe, rank_candidates, explain_candidate | sha256:c7496575fd22bfe1b7dd99887a36fcf08352f87b273ac4b4d8ac835a7944a8c5 | - | identity-resolved 회사 universe에만 company 필터를 적용하고 strict/unverifiable/conflict/excluded 후보를 분리하며 각 판정 근거를 반환한다. | - |
| D-04-requirement-contract-r2 | MODIFY | `src/company_intel/career_requirements.py` | D-04-career-requirement-verification | RequirementKind, RequirementNecessity, verify_requirement, requirement_overlap | sha256:2eee38f22c88fff195e85102161f1d8f80c1d22c1ec3a0b7eecfc39c331ac47c | - | 요건 종류, required/preferred/unknown, proficiency/value, evidence span, jurisdiction과 confidence를 원자 행으로 만들고 부재·미기재·미추출을 분리한다. | - |
| D-03-search-tests-r2 | MODIFY | `tests/test_search_profile.py` | D-03-search-profile-and-discovery | test_legacy_profile_warnings, test_five_state_combination, test_cluster_routing, test_identity_conflict | sha256:0adc5640d47981ca88156de77c39a16e3fe56cbea6a957091e97fea65932a663 | - | 모든 원자 축, ANY/ALL, strict/unverifiable/conflict 분리와 legacy warning을 검증한다. | - |
| D-04-requirement-tests-r2 | MODIFY | `tests/test_career_requirements.py` | D-04-career-requirement-verification | test_unknown_not_required, test_posting_vs_required_language, test_certification_vs_license, test_requirement_dedupe_key | sha256:aa5b355da9220b0f836324244bced0021cbe4fcb5749986f14c818a418408694 | - | 실제형 ATS/MPSV fixture에서 필요도·관할·proficiency·evidence span과 중복키를 검증한다. | - |

### Routed skills

- `c02-r2-tdd` → `tdd` (IMPLEMENT, required): 5상태 진리표와 요건 의미를 테스트 우선 고정
- `c02-r2-research` → `company-intelligence-career-research` (IMPLEMENT, required): 국가별 자격·직업 codebook 의미 검증
- `c02-r2-verify` → `verification-before-completion` (VALIDATE, required): 검색·요건 계약 독립 검증

### Completion criteria

- `C-02-r2-search-requirement-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: 원자 profile, 5상태 조합, 법인 충돌, 요구언어, 자격/면허, unknown 필요도가 offline fixture에서 통과한다.
