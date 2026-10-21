---
name: company-intelligence-work-future
description: 선택 직무의 업무별 AI 노출, 매핑 범위와 지역·기간별 임금 분포를 비교할 때 사용한다.
---

# S04 — 업무 노출과 직종 임금의 비교 범위를 확인한다.

업무 가중치·연구 방법·버전·척도를 기록한다. 미매핑 비중은 0으로 채우지 않는다. 노출을 개인 대체확률 또는 1−노출 생존률로 해석하지 않는다. 시간급 연환산은 명시한 유급 시간 가정이 필요하다. 통화·세전후·급여 주기를 유지한다.

입력: `role_mapping_ref, task_weights_ref, exposure_method, wage_comparison, history, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
