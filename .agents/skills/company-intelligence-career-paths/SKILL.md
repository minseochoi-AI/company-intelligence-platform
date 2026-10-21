---
name: company-intelligence-career-paths
description: 선택 기업 입사 후 역할과 이동 경로를 회사 근거·직업 프레임워크·제안으로 구별해 설계할 때 사용한다.
---

# S05 — 구조·역할·이동 관계를 독립 축으로 구성한다.

구조는 single_ladder/dual_ladder/career_lattice. 역할은 IC_specialist/technical_leadership/people_management/project_product_program. 이동은 promotion/lateral/diagonal/rotation/secondment/project_assignment/track_switch 등이다. 외부 직업 유사도나 프레임워크를 해당 회사 승진 규정으로 바꾸지 않는다. 공식 회사 정책은 고용주 일치·source_id가 필요하다. 제안은 ProposedPaths에만 보관한다.

입력: `career_spec, role_mapping_ref, profile_ref, subject_refs, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
