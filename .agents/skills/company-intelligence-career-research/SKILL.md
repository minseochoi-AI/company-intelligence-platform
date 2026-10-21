---
name: company-intelligence-career-research
description: 선택한 채용 공고의 필수·우대·결격 조건, 전형별 경쟁 근거와 공고 급여를 조사할 때 사용한다.
---

# S02 — 공고 요건과 사용자 증빙을 대조한다.

필수·우대·결격을 분리한다. 검토 전 AI 추출문은 미확인이다. 공식 지원자/모집인원 또는 합격자/응시인원은 동일 회차·직무·지역·단계·마감시각으로만 나눈다. 클릭 수는 지원자 수가 아니다. 개인 합격확률을 산출하지 않는다.

입력: `subject_refs, profile_ref, requirement_policy, competition_spec, history, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
