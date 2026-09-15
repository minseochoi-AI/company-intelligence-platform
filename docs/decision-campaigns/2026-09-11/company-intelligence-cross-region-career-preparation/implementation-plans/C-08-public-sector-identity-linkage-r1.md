# Implementation plan: company-intelligence-cross-region-career-preparation--C-08-public-sector-identity-linkage--r1

Status: `contract-ready`

## public-sector-identity-evidence-linkage: MPM 기관명과 ALIO 기관을 검증·후보·미연결로 결합하고 MPSV IČO와 ARES를 exact join하면서 공고 맥락·기관유형·법적형태·소유부문을 분리한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-068da823a7c2 | CREATE | `src/company_intel/public_identity.py` | D-13-public-sector-identity-linkage | IdentityLink, link_mpm_alio, link_mpsv_ares, classify_link_status | - | - | 공식 ID exact, 검증된 alias, 이름 후보, unresolved, conflict를 분리하고 축별 provenance를 반환한다. | - |
| file-change-d8bc97a982b6 | MODIFY | `src/company_intel/taxonomy.py` | D-13-public-sector-identity-linkage | TaxonomyFact, normalize_alio_taxonomy, normalize_ares_taxonomy, link_status | sha256:6e3631645577f727e6cc158c2e5a3858a1e6050c24ec705670654edce940b401 | - | 각 taxonomy fact가 entity link evidence와 namespace를 보존하고 미연결 축은 unavailable로 남는다. | file-change-068da823a7c2 |
| file-change-c2dd27200b1c | MODIFY | `src/company_intel/classification.py` | D-13-public-sector-identity-linkage | classify_company, identity_eligibility, public_sector_axes | sha256:0c145eed1c441a62369b28ef8a8fd81423ea8358e2d8e2a2ab56dc919e4fb428 | - | linked/candidate/unresolved/conflict 상태에 따라 축별 filterability와 분석 적격성을 계산한다. | file-change-d8bc97a982b6 |
| file-change-ec13a6928783 | CREATE | `tests/test_public_identity.py` | D-13-public-sector-identity-linkage | test_mpsv_ico_exact_ares_join, test_mpm_name_candidate_not_auto_linked, test_conflicting_links | - | - | exact ID, verified alias, fuzzy candidate, unresolved, conflict와 축 분리를 offline fixture로 검증한다. | file-change-068da823a7c2, file-change-c2dd27200b1c |
| file-change-4e2a56e63819 | MODIFY | `tests/test_taxonomy.py` | D-13-public-sector-identity-linkage | test_public_axes_remain_separate, test_link_status_controls_filterability | sha256:9399e350d9bf1494f84f25183eac4c18c924dc6e6e0f15c11bc5c54b592d5870 | - | 공공행정·공공기관유형·legal form·ownership이 독립이며 link 상태가 선택 가능성을 제한하는지 검증한다. | file-change-d8bc97a982b6 |

### Routed skills

- `c08-identity-semantics` → `company-intelligence-career-research` (IMPLEMENT, required): 한국·체코 공공 원천의 서로 다른 법적 의미를 보존한다.
- `c08-verification` → `verification-before-completion` (VALIDATE, required): identity와 taxonomy 경계를 독립 검증한다.

### Completion criteria

- `C-08-public-identity-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: MPM↔ALIO와 MPSV↔ARES 연결이 근거 수준과 독립 taxonomy 축을 보존한다.
