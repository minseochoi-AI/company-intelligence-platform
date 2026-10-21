# Codex 조사 스킬 프로토콜

정본은 저장소 `.agents/skills/`의 S01~S08이다. `.codex/skills/`는 예전 경로를 위한 포인터다. 홈에 설치된 동명 스킬은 이 저장소 정본과 별개다. 해당 세션에서 저장소 경로를 명시해 읽으며 홈 설정을 몰래 변경하지 않는다.

S01 목적 확정 → 필요한 S02 채용/S03 재무/S04 업무 미래/S05 내부 경로/S06 포트폴리오/S07 창업 → 결정론적 run → S08 AI 보고서. 8개 스킬을 매번 모두 호출하지 않는다. 모든 인자는 출처를 갖고, 추가 API는 버전별 capability registry를 통과한다.

v1 EvidenceBundle·DomainPlan 검증기는 기존 의미를 유지한다. v2는 명시 버전으로만 소비한다. confidence가 없는 사실을 임의의 신뢰 점수로 채우지 않는다. Money는 통화를 필수로 갖는다. 조사 제안 DomainPlan은 DCW 코드 구현 Plan이나 실행 권한이 아니다.
