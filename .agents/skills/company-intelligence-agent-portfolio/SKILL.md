---
name: company-intelligence-agent-portfolio
description: 선택 공고의 업무·역량 공백과 공개된 문제 근거를 바탕으로 차별화된 에이전트 포트폴리오 실험을 설계할 때 사용한다.
---

# S06 — 관측된 업무와 작성한 개발 실험을 연결한다.

대상 업무·gap_refs·기존 방식 baseline·평가 데이터·지표·실패 조건·데이터 권리·예산 통화를 기록한다. 공개 이슈는 문제 근거이며 유료 수요 증거가 아니다. 개발 완료·채용 성공으로 보고하지 않는다. 실제 구현은 별도 사용자 작업 범위다.

입력: `portfolio_spec, profile_ref, subject_refs, role_mapping_ref, as_of`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
