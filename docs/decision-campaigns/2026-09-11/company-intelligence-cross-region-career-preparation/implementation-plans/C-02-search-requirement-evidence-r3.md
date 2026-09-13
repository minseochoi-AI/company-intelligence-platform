# Implementation plan: company-intelligence-cross-region-career-preparation--C-02-search-requirement-evidence--r3

Status: `contract-ready`

## semantic-company-search-profile-r3: 기업 검색에서 이름/식별자와 provider-native taxonomy 조건을 명시적으로 구분하고, 적용되지 않는 legacy job 조건을 조용히 무시하지 않는다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| D-03-company-search-contract-r3 | MODIFY | `src/company_intel/query_contract.py` | D-03-search-profile-and-discovery | AtomicSearchProfile, FieldFilter, FilterMode, FieldVerdict | sha256:7cb1df9dc4a72c495cd25c76d0ba3d81ff117c729218415c59ba202963e5db5e | - | 필드별 ALL/ANY, applicability, no-match/unverifiable/conflict verdict를 가진 검색 계약을 제공한다. | - |
| D-03-company-search-engine-r3 | MODIFY | `src/company_intel/search.py` | D-03-search-profile-and-discovery, D-04-career-requirement-verification | CompanySearchProfile, rank_candidates, apply_country_allocation | sha256:770d932ac63391079567fdb54696c1b31f4733d0d7f55d06e99dedab8c960cc4 | - | 기업 전용 profile로 country, identity, ownership, legal form, industry, market/public-institution taxonomy와 실제 country allocation을 판정한다. | D-03-company-search-contract-r3 |
| D-03-search-profile-tests-r3 | MODIFY | `tests/test_search_profile.py` | D-03-search-profile-and-discovery | test_company_taxonomy_filters, test_country_allocation | sha256:d4854042461f3a1e0748db84664e301b99f6533fe0464d821ef1ac492ace9ece | - | taxonomy filter, allocation, unsupported legacy field, ALL/ANY verdict를 offline으로 검증한다. | D-03-company-search-engine-r3 |
| D-03-query-contract-tests-r3 | CREATE | `tests/test_query_contract.py` | D-03-search-profile-and-discovery | test_field_filter_verdicts | - | - | strict/unverifiable/no-match/conflict와 ALL/ANY 조합을 검증한다. | D-03-company-search-contract-r3 |

### Routed skills

- `search-contract-implementation` → `company-intelligence-career-research` (IMPLEMENT, required): 검색 조건의 원천 의미를 보존한다.
- `search-contract-tests` → `tdd` (VALIDATE, required): offline profile regressions를 실행한다.

### Completion criteria

- `C02-r3-company-search-tests` [planned] `tdd` phase=VALIDATE, depends=-: 기업 taxonomy 조건, allocation, verdict가 실제로 적용된다.

