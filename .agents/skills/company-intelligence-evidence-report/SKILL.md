---
name: company-intelligence-evidence-report
description: 봉인된 조사 Excel과 구조화된 표를 읽어 근거·숫자를 연결한 별도 AI 해석 보고서를 만들 때 사용한다.
---

# S08 — 사실 입력을 변경하지 않고 AI 해석을 작성·검증한다.

먼저 manifest와 각 파일 해시를 확인한다. ai-input.json의 허용 자료로 report.md와 research-claims-v1 claims.json을 작성한다. 본문의 모든 실질적인 문장을 claims에 등록하고 table_id·row_id·column_id에 연결한다. 수치·단위는 봉인된 값과 같아야 한다. 추론·가정·제안은 assumptions를 붙인다. fixture/demo는 시연이라고 밝힌다. 검증기는 참조·숫자·변조만 확인하며 문장 전체 의미의 진실성을 보장하지 않는다.

입력: `sealed bundle path, manifest_sha256, narrative, claims, report_spec`. API 추가는 capability operation·schema version·field semantics·권리·자료 시점 등록이 선행한다. 등록만으로 실시간 가용성이나 모든 응답 키가 검증되었다고 보고하지 않는다.

AI는 사용자의 질문에서 목적·필터·분석 방법 후보를 제안할 수 있다. `argument_origins`에는 실제 출처를 기록한다. 개인 자격·법인/공고 식별자·기준 시점·자료 바인딩은 사용자 명시 또는 출처 근거로 확정한다. 미확정이면 NEEDS_INPUT/NEEDS_EVIDENCE를 반환한다. 개인 학위·원자력·에너지·국가 선호는 전역 기본값이 아니다.

실행·해석은 [조사 계약](references/research-contract.md)을 따른다. 로컬 저장 자료가 기본이다. 외부 API 갱신·지원서 제출·게시·배포를 이 스킬 호출만으로 수행하지 않는다.
