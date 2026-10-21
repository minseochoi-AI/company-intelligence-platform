---
name: company-intelligence-analysis
description: 선택한 고용주 법인의 과거 공시, 재무 성장과 명시적 미래 가정을 비교할 때 사용한다.
---

# S03 — 법인별 비교 가능한 재무와 가정 시나리오를 구분한다.

고용주와 모회사의 법인 식별자를 분리한다. 기준 시점에 공개된 자료만 known_at_time에 포함한다. 개념·연결범위·통화·단위·기간이 같아야 성장률을 계산한다. 손실·영점 기준 성장률은 미확인이다. 미래 값은 authored scenario이며 고용 안정의 인과 근거가 아니다.

입력: `financial_spec, history, comparability, scenario_ref, source_bindings, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
