---
name: company-intel-cli
description: 선택한 채용 공고나 기업을 여러 목적에서 조사하고 재현 가능한 Excel을 만들 때 사용한다.
---

# S01 — 목적과 입력을 확정하고 필요한 스킬만 선택한다.

최소 호출은 S01 → 해당 목적 스킬 → S08. financial은 S03만, path는 S02·S05, work-future는 S02·S04를 선택한다. 선택한 공고의 provider_id·posting_id·revision은 명시한 원문으로 확정한다.

입력: `purpose, question, cohort_signature, subject_refs, as_of, field_filters, source_bindings, argument_origins, execution_limits`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
