---
name: kr-defensible-venture-discovery
description: 선택 업무의 공개 문제·구매자·대체재 근거로 창업 실험과 차별성 가설을 검토할 때 사용한다.
---

# S07 — 문제 증거와 사업 가설·지불 검증을 구별한다.

buyer·user·payer·problem·substitutes·pilot·kill_criteria·jurisdictions·budget 통화를 기록한다. 한국 규정이나 개인 자격은 선택 인스턴스 조건으로만 넣는다. payment_evidence_refs 없는 매출을 observed로 표시하지 않는다. 창업 가설은 사업자 등록이나 판매 실행 권한이 아니다.

입력: `venture_spec, subject_refs, profile_ref, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
