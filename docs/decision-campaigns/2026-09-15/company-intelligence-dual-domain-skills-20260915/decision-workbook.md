# company-intelligence-dual-domain-skills-20260915 — 의사결정 워크북

> 이 파일은 `campaign.json`과 `decisions/*.json`에서 생성됩니다.
> JSON 정본의 사람용 서술을 한국어로 수정한 뒤 이 워크북을 다시 생성합니다.

## 캠페인 요약

| 항목 | 값 |
|---|---|
| 목표 | Company Intelligence Platform을 실행 엔진으로 사용하는 기업분석 스킬과 한국형 방어가능 창업분석 스킬을 구현하고, 기존 커리어 스킬과 함께 세 사용자 책임을 유지하며, 버전된 비스킬 계약으로 EvidenceBundle·DomainPlan·DualPathComparison·CampaignLink를 검증한다. |
| 상태 | decision-approved |
| 생성일 | 2026-09-15 |
| 구현 승인 | 승인됨: True<br>승인자: user<br>승인 시각: 2026-09-15T06:55:00.420883+00:00<br>범위: ['D-11']<br>승인된 계획 참조: [{'cohort_id': 'C-06-diagram-toolchain', 'plan_id': 'C-06-diagram-toolchain-plan-r1', 'path': 'docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/implementation-plans/C-06-diagram-toolchain.json', 'sha256': '55f0309057185184b44a159fcf77f9dadc40d901a2f7b06a52e9e2f6b36e19e3'}] |
| Context Index | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/context-index.json |
| 구현 cohort context | {'cohort_id': 'C-01-interop-control', 'decision_ids': ['D-01', 'D-02', 'D-03', 'D-06', 'D-07', 'D-10'], 'status': 'planned', 'context_packet_path': None, 'context_packet_sha256': None, 'implementation_plan_path': None, 'implementation_plan_sha256': None, 'implementation_plan_status': None, 'execution_dependencies': []}<br>{'cohort_id': 'C-02-cil-runtime', 'decision_ids': ['D-09'], 'status': 'planned', 'context_packet_path': None, 'context_packet_sha256': None, 'implementation_plan_path': None, 'implementation_plan_sha256': None, 'implementation_plan_status': None, 'execution_dependencies': ['C-01-interop-control']}<br>{'cohort_id': 'C-03-company-analysis-skill', 'decision_ids': ['D-04'], 'status': 'planned', 'context_packet_path': None, 'context_packet_sha256': None, 'implementation_plan_path': None, 'implementation_plan_sha256': None, 'implementation_plan_status': None, 'execution_dependencies': ['C-01-interop-control', 'C-02-cil-runtime']}<br>{'cohort_id': 'C-04-venture-analysis-skill', 'decision_ids': ['D-05'], 'status': 'planned', 'context_packet_path': None, 'context_packet_sha256': None, 'implementation_plan_path': None, 'implementation_plan_sha256': None, 'implementation_plan_status': None, 'execution_dependencies': ['C-01-interop-control']}<br>{'cohort_id': 'C-05-packaging-validation', 'decision_ids': ['D-08'], 'status': 'planned', 'context_packet_path': None, 'context_packet_sha256': None, 'implementation_plan_path': None, 'implementation_plan_sha256': None, 'implementation_plan_status': None, 'execution_dependencies': ['C-02-cil-runtime', 'C-03-company-analysis-skill', 'C-04-venture-analysis-skill']}<br>{'cohort_id': 'C-06-diagram-toolchain', 'decision_ids': ['D-11'], 'status': 'contract-ready', 'context_packet_path': 'docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/context-packets/C-06-diagram-toolchain-r1.json', 'context_packet_sha256': '28519f24a546ae9cde72ad9560991fdcef66de6ef69f2406c1aa9580454cac47', 'implementation_plan_path': 'docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/implementation-plans/C-06-diagram-toolchain.json', 'implementation_plan_sha256': '55f0309057185184b44a159fcf77f9dadc40d901a2f7b06a52e9e2f6b36e19e3', 'implementation_plan_status': 'contract-ready', 'execution_dependencies': ['C-05-packaging-validation']} |
| 구현 영수증 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/receipts/implementation.json |
| 검증 영수증 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/receipts/validation.json |

## 의사결정 요약

| No | 작업 단위 | 상태 | 핵심 질문 | 권장안 | 선행 결정 | 사용자 결정 |
|---:|---|---|---|---|---|---|
| 1 | skill-portfolio-boundary | accepted | 기업분석과 창업분석을 어떤 독립 스킬로 나누고 기존 취업 조사 스킬과 어떻게 충돌 없이 공존시킬 것인가? | B-SEPARATE-DOMAIN-SKILLS | — | ACCEPT |
| 2 | domain-plan-contract | accepted | 캠페인의 구현 plan SHA를 훼손하지 않으면서 취업·창업 계획을 해시 결속된 도메인 산출물로 어떻게 관리할 것인가? | B-SEPARATE-DOMAIN-PLAN-REF | D-01 | ACCEPT |
| 3 | evidence-interop-contract | accepted | 기업분석·취업·창업 스킬이 런타임 종속 없이 검증된 증거만 선택적으로 교환하려면 어떤 계약이 필요한가? | B-HASHED-EVIDENCE-BUNDLE | D-02 | ACCEPT |
| 4 | company-analysis-skill | accepted | 기업분석 스킬은 CIL의 어떤 기능을 재사용하고 어디까지를 분석 완료로 주장할 것인가? | B-THIN-CIL-ORCHESTRATOR | D-01<br>D-03<br>D-09 | ACCEPT |
| 5 | venture-analysis-skill | accepted | 창업분석 스킬이 시장기회·경쟁·방어력·창업자 자원을 어떻게 판단하고 CIL 기업증거는 언제 선택적으로 사용할 것인가? | B-INDEPENDENT-VENTURE-WITH-OPTIONAL-CIL | D-01<br>D-03<br>D-10 | ACCEPT |
| 6 | free-connector-policy | accepted | 무료 기업·동향 연결 후보 중 무엇을 즉시 의존성으로 채택하고 무엇을 후보 레지스트리로만 유지할 것인가? | B-CANDIDATE-REGISTRY-WITH-GATES | D-03 | ACCEPT |
| 7 | campaign-routing-boundary | accepted | 두 도메인 스킬이 decision-campaign-workbook을 상속·복사하지 않고도 복수 의사결정에 선택적으로 연결되려면 어떻게 해야 하는가? | B-OPTIONAL-ROUTER-NO-INHERITANCE | D-02<br>D-03 | ACCEPT |
| 8 | packaging-validation | accepted | 두 스킬을 실제 Codex에서 발견·선택·실행·연동할 수 있음을 어떤 검증으로 입증할 것인가? | B-STRUCTURAL-AND-BEHAVIORAL-VALIDATION | D-04<br>D-05<br>D-06<br>D-07<br>D-09<br>D-10 | ACCEPT |
| 9 | cil-runtime-readiness | accepted | 기업분석 스킬이 저장소 밖에서도 CIL을 안전하게 실행하고 fixture와 production 결과를 혼동하지 않도록 어떤 실행 계약을 둘 것인가? | B-EXPLICIT-ROOT-AND-PURPOSE-CONTRACT | D-01 | ACCEPT |
| 10 | three-skill-dual-path-ownership | accepted | 기업·취업·창업의 세 책임을 유지하면서 취업과 창업 계획을 비교하는 공통 산출물을 누가 소유할 것인가? | B-THREE-SKILLS-SHARED-COMPARISON-CONTRACT | D-01<br>D-02<br>D-03 | ACCEPT |
| 11 | deterministic-diagram-toolchain | accepted | 캠페인 다이어그램을 저장소 자체에서 검증·컴파일·SVG/PNG 렌더·freshness 검사할 도구체인을 어떤 경계로 소유할 것인가? | B-REPOSITORY-PINNED-TOOLCHAIN | D-08 | ACCEPT |

## 의사결정 상세

## 1. 두 스킬의 제품 경계와 기존 취업 조사 스킬 관계 (`D-01`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업분석과 창업분석을 어떤 독립 스킬로 나누고 기존 취업 조사 스킬과 어떻게 충돌 없이 공존시킬 것인가? |
| 누가 | 기업·공공기관을 비교하려는 사용자, 창업기회를 검증하려는 창업자, 취업 준비 근거를 찾는 구직자와 이를 수행하는 Codex |
| 무엇을 | company-intelligence-analysis와 kr-defensible-venture-discovery를 별도 스킬로 만들고 기존 company-intelligence-career-research의 취업 조사 책임을 유지한다. |
| 어디서 | 저장소의 skills/ 아래 두 신규 패키지와 현재 전역에 설치된 취업 조사 스킬 경계에서 적용한다. |
| 언제 | 스킬 구현·설치 전에 trigger, 입력, 출력, 금지행동과 상호 참조 계약을 먼저 확정한다. |
| 왜 | 기업 사실 검증, 취업 준비, 창업기회 판단은 데이터 일부를 공유해도 질문·실패조건·출력이 달라 하나의 스킬로 합치면 오작동과 과잉 활성화가 생긴다. |
| 어떻게 | 기업분석은 식별된 기업의 CIL 근거를 생성하고, 취업 조사는 채용·요건·커리어 계획을 생성하며, 창업분석은 시장·경쟁·장벽·자원 적합성을 판단하도록 책임을 분리한다. |
| 근거 | EV-USER-SKILL-AUDIT — /home/ubuntu/.codex/attachments/c2ee1c4e-3b8a-473a-8de6-3b1591d1bbcd/pasted-text.txt — 사용자가 기업분석과 창업분석 스킬을 분리하고 선택적 연동을 요구했다.<br>EV-EXISTING-CAREER-SKILL — /home/ubuntu/.codex/skills/company-intelligence-career-research/SKILL.md — 기존 스킬은 미국·한국·체코 기업·직무 요건·자격증·준비사항 조사에 한정된 별도 trigger를 이미 가진다.<br>EV-CIL-CLI-SKILL — .codex/skills/company-intel-cli/SKILL.md — 저장소에는 CIL 명령 사용법을 담당하는 로컬 스킬이 있으나 도메인 판단 스킬은 아니다. |
| 관찰 사실 | CIL CLI 사용 스킬과 취업 조사 스킬이 이미 서로 다른 책임으로 존재한다.<br>창업분석에는 시장경계·경쟁·자원·장벽 판단이 필요하며 이는 기업 조회와 동일하지 않다.<br>신규 스킬을 두 개로 제한해도 기존 취업 스킬을 삭제하거나 신규 스킬에 합칠 필요는 없다. |
| 충돌 | 기업분석 결과는 취업과 창업 양쪽에서 재사용되지만 재사용을 이유로 실행 책임까지 합치면 trigger가 모호해진다.<br>사용자가 말한 두 스킬과 기존 취업 스킬을 합산하면 실제 배포 단위는 세 개가 될 수 있다. |
| 미구현 | 두 신규 스킬 디렉터리와 SKILL.md<br>세 도메인 사이 trigger 충돌 검사<br>공유 artifact의 producer/consumer 책임표 |
| 선택지 | A-MONOLITHIC-ANALYSIS-SKILL: 기업·취업·창업 분석을 하나의 대형 스킬로 합쳐 내부 분기로 처리한다.; B-SEPARATE-DOMAIN-SKILLS: 기업분석과 창업분석을 별도 신규 스킬로 만들고 기존 취업 조사 스킬은 유지하며 파일 계약으로만 연동한다. |
| 권장안 | B-SEPARATE-DOMAIN-SKILLS |
| 권장 근거 | 실행 엔진은 공유할 수 있지만 사용자 질문과 증거의 의미가 달라 독립 trigger·출력·실패계약이 필요하다. |
| 파급효과 | 데이터: 도메인별 근거 최소화와 provenance를 우선한다.<br>스키마/API: DomainPlanRef와 EvidenceBundleRef만 공유한다.<br>사용자 경험: 기업 검증·취업 조사·창업 계획이 구분된다.<br>성능: 필요한 스킬만 로드한다.<br>비용: 세 경계의 유지비가 생긴다.<br>보안: 구직자 정보는 자동 전달하지 않는다.<br>마이그레이션: 기존 스킬을 폐기하지 않는다.<br>테스트: 양성·음성 trigger 검증이 필요하다. |
| 기회비용 | 모든 기능을 한 명령으로 보이는 단순성은 포기한다. |
| 선행 결정 | — |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-SEPARATE-DOMAIN-SKILLS<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/skills/company-intelligence-analysis/SKILL.md<br>.codex/skills/kr-defensible-venture-discovery/SKILL.md<br>.codex/shared/company-intelligence-interop/BOUNDARIES.md |
| 구현 변경 ID | C01-008<br>C03-001<br>C03-002<br>C03-003<br>C03-004<br>C03-005<br>C04-001<br>C04-002<br>C04-003<br>C04-004<br>C04-005<br>C04-006<br>C04-007<br>C04-008 |
| 검증 기준 | 기업·기존 커리어·창업 책임이 서로 배타적인 trigger를 가짐<br>기존 글로벌 커리어 스킬을 저장소 안에 복제하지 않음<br>두 신규 스킬은 파일 계약 없이 서로를 직접 import하지 않음<br>공통 계약은 사용자 대면 스킬로 등록되지 않음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/skill-domain-routing.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.png |
| 구현 맥락 topic | interop-control |

## 2. 구현 plan과 취업·창업 domain plan의 해시 계약 분리 (`D-02`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 캠페인의 구현 plan SHA를 훼손하지 않으면서 취업·창업 계획을 해시 결속된 도메인 산출물로 어떻게 관리할 것인가? |
| 누가 | 캠페인 승인자, 스킬 구현자, 취업·창업 계획을 실행·재현하는 사용자 |
| 무엇을 | implementation_plan_sha256는 코드 변경 권한에 유지하고 career 또는 venture DomainPlan과 DomainPlanRef를 별도 계약으로 만든다. |
| 어디서 | 캠페인의 implementation-plans와 스킬 실행 결과의 domain-plans를 서로 다른 경로와 스키마로 저장한다. |
| 언제 | PREPARE에서 구현 plan을 생성하고 실제 스킬 실행 시 domain plan을 생성할 때 각각 해시한다. |
| 왜 | 한 SHA 필드가 코드 변경 계획과 사용자의 행동 계획을 동시에 뜻하면 권한·재현·stale 판정이 모호해진다. |
| 어떻게 | DomainPlanRef에 plan_kind, plan_id, revision, path, sha256, schema_version, generated_at, evidence_bundle_refs를 두고 캠페인은 별도 link manifest만 참조한다. |
| 근거 | EV-CAMPAIGN-SCHEMA — /home/ubuntu/.codex/skills/decision-campaign-workbook/references/decision-campaign.schema.json — implementation_plan_sha256는 cohort 구현 계획과 exact-plan authorization을 묶으며 campaign.json은 추가 속성을 허용하지 않는다.<br>EV-CAMPAIGN-EVIDENCE-ROUTING — /home/ubuntu/.codex/skills/decision-campaign-workbook/references/evidence-routing.md — plan hash는 정확한 바이트를 결속하고 결과 성공을 뜻하지 않으며 scope·plan·execution result를 구분해야 한다. |
| 관찰 사실 | implementation_plan_sha256는 저장소 구현 권한과 검증 receipt를 연결한다.<br>campaign.json schema는 additionalProperties=false라 임의의 career_plan_sha를 추가할 수 없다.<br>취업·창업 계획은 소스 코드 계획과 수명주기·소비자가 다르다. |
| 충돌 | 사용자는 plan SHA를 도메인 계획 중심으로 바꾸고 싶지만 기존 캠페인 도구는 구현 계획 의미를 전제로 한다.<br>DomainPlan 내부에 자기 파일 해시를 넣으면 self-hash 문제가 생기므로 별도 Ref가 필요하다. |
| 미구현 | domain-plan.schema.json<br>domain-plan-ref.schema.json<br>domain-plan-link.schema.json<br>해시 생성·검증기와 stale 판정 |
| 선택지 | A-REPURPOSE-IMPLEMENTATION-PLAN-SHA: campaign.json의 implementation_plan_sha256를 취업·창업 계획 해시로 재해석한다.; B-SEPARATE-DOMAIN-PLAN-REF: 구현 plan SHA를 유지하고 career\|venture DomainPlan과 외부 DomainPlanRef/Link manifest를 별도 생성한다. |
| 권장안 | B-SEPARATE-DOMAIN-PLAN-REF |
| 권장 근거 | 구현 권한 의미를 보존하면서 취업·창업 계획도 독립적이고 검증 가능한 정본으로 만들 수 있다. |
| 파급효과 | 데이터: DomainPlan은 목표·단계·의존성·근거를 보존하고 Ref가 외부 hash를 보존한다.<br>스키마/API: plan_kind는 career 또는 venture이며 implementation은 캠페인에 남는다.<br>사용자 경험: 코딩 계획과 행동계획을 분리 표시한다.<br>성능: 파일 해시 검증만 추가된다.<br>비용: 공유 계약 구현비가 든다.<br>보안: 민감 입력을 redaction한다.<br>마이그레이션: 기존 plan을 수정하지 않는다.<br>테스트: self-hash·path traversal·hash mismatch·wrong kind를 검증한다. |
| 기회비용 | 단일 plan 필드의 표면적 단순성은 포기한다. |
| 선행 결정 | D-01 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-SEPARATE-DOMAIN-PLAN-REF<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/shared/company-intelligence-interop/domain-plan.schema.json<br>.codex/shared/company-intelligence-interop/domain-plan-ref.schema.json<br>.codex/shared/company-intelligence-interop/interop.py |
| 구현 변경 ID | C01-001<br>C01-002<br>C01-009 |
| 검증 기준 | implementation_plan_sha256가 DomainPlan hash로 재사용되지 않음<br>DomainPlanRef hash 불일치 시 소비 거부<br>career와 venture plan_kind 혼입 거부<br>도메인 계획 승인만으로 구현 권한이 생기지 않음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/plan-evidence-interop.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.png |
| 구현 맥락 topic | interop-control |

## 3. 증거 파일·해시 기반 선택 연동 계약 (`D-03`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업분석·취업·창업 스킬이 런타임 종속 없이 검증된 증거만 선택적으로 교환하려면 어떤 계약이 필요한가? |
| 누가 | 증거를 생성하는 CIL/기업분석 스킬과 이를 선택 소비하는 취업·창업 스킬 |
| 무엇을 | EvidenceBundleManifest와 EvidenceBundleRef로 파일별 hash, schema, producer, source, 관측시각, 권리, redaction, subject identity를 결속한다. |
| 어디서 | 사용자 지정 artifact 디렉터리에 immutable bundle과 외부 ref를 저장한다. |
| 언제 | producer 출력 직후 hash를 만들고 consumer가 읽기 전에 전부 재검증한다. |
| 왜 | 스킬끼리 Python import나 숨은 상태를 공유하면 재현성·선택성·설치 독립성이 깨진다. |
| 어떻게 | consumer는 명시된 path와 sha256만 읽고 schema·identity·freshness·license·redaction gate 중 하나라도 실패하면 unavailable로 남긴다. |
| 근거 | EV-CIL-EXPORT — src/company_intel/exporting.py — CIL export는 표별 파일 hash와 run_manifest_sha256를 생성하고 formula/secret 안전 처리를 한다.<br>EV-CIL-RUN-MANIFEST — src/company_intel/run_manifest.py — CIL은 선택·snapshot·결과 reference를 결속하는 run manifest를 구현했다. |
| 관찰 사실 | CIL은 이미 파일별 hash와 run manifest 기반을 제공한다.<br>현재 형식은 CIL 실행 재현에 초점이 있고 스킬 간 도메인 소비 허용 범위는 정의하지 않는다.<br>hash 일치는 출처의 진실성이나 분석 성공을 자동 증명하지 않는다. |
| 충돌 | 완전 복사 bundle은 재현성이 높지만 개인정보·용량을 늘릴 수 있다.<br>경로 참조만 쓰면 원본 이동·수정에 취약하다. |
| 미구현 | evidence-bundle-manifest.schema.json<br>evidence-bundle-ref.schema.json<br>producer/consumer capability matrix<br>tamper·license·freshness validator |
| 선택지 | A-DIRECT-SKILL-IMPORT: 스킬이 다른 스킬의 스크립트·내부 상태를 직접 import하고 반환 객체를 전달한다.; B-HASHED-EVIDENCE-BUNDLE: 각 스킬은 독립 실행하고 hash 검증된 EvidenceBundleRef만 명시적으로 교환한다. |
| 권장안 | B-HASHED-EVIDENCE-BUNDLE |
| 권장 근거 | CIL의 기존 hash·manifest 강점을 재사용하면서 스킬 설치와 실행을 독립적으로 유지한다. |
| 파급효과 | 데이터: source·dataset·evidence·claim 관계와 파일 hash를 보존한다.<br>스키마/API: CIL run manifest를 바꾸지 않고 상위 bundle manifest로 감싼다.<br>사용자 경험: verified, stale, incompatible, unavailable 상태를 표시한다.<br>성능: 선택한 bundle만 읽는다.<br>비용: 공유 validator 구현이 필요하다.<br>보안: secret·PII 필드 allowlist와 path 제한이 필요하다.<br>마이그레이션: 기존 export는 adapter로 bundle화한다.<br>테스트: byte tamper·wrong subject·unsupported schema·expired evidence를 검증한다. |
| 기회비용 | 자동 연동 대신 명시적 파일 전달이 필요하다. |
| 선행 결정 | D-02 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-HASHED-EVIDENCE-BUNDLE<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/shared/company-intelligence-interop/evidence-bundle.schema.json<br>.codex/shared/company-intelligence-interop/evidence-bundle-ref.schema.json<br>.codex/shared/company-intelligence-interop/interop.py<br>.codex/shared/company-intelligence-interop/BOUNDARIES.md |
| 구현 변경 ID | C01-003<br>C01-004<br>C01-008<br>C01-009 |
| 검증 기준 | 모든 소비 파일의 sha256 재검증<br>허용 경로 밖 reference 거부<br>민감 필드가 bundle에 있으면 redaction 실패<br>hash 일치만으로 claim verified 상태를 만들지 않음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/plan-evidence-interop.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.png |
| 구현 맥락 topic | interop-control |

## 4. 기업분석 스킬의 실행·출력·한계 계약 (`D-04`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업분석 스킬은 CIL의 어떤 기능을 재사용하고 어디까지를 분석 완료로 주장할 것인가? |
| 누가 | 미국·한국·체코의 식별된 기업·공공기관을 비교하는 사용자 |
| 무엇을 | 기업 식별, source capability, 동료군 비교, timeline, valuation scenario, AI-event 분석과 근거 export를 안내·검증한다. |
| 어디서 | CIL CLI/API와 저장된 snapshot·run manifest·export artifact 위에서 동작한다. |
| 언제 | 대상 기업·국가·관측 기준일과 필요한 분석 축이 정해진 뒤 실행한다. |
| 왜 | 스킬이 계산 로직을 복제하면 CIL 테스트와 다른 결과가 생기며, CIL이 제공하지 않는 시장 발견을 과장할 위험이 있다. |
| 어떻게 | thin orchestration으로 CIL 명령을 선택하고 출력 manifest를 검증한 뒤 사실·추론·불가항목·비교 가능 집단을 분리 보고한다. |
| 근거 | EV-CIL-QUERY-CONTRACT — src/company_intel/query_contract.py — provider 원시 필드를 보존하면서 provider-neutral filter와 평가 불가능 상태를 분리한다.<br>EV-CIL-ANALYSIS — src/company_intel/analysis_service.py — 기업 비교·timeline·가치·AI 사건 분석 서비스가 구현되어 있다. |
| 관찰 사실 | CIL은 식별자·capability·비교 규격과 근거 export를 제공한다.<br>CIL의 기업 검색은 원천 coverage에 제한되며 전체 시장 경쟁사를 자동 발견하지 않는다.<br>valuation과 AI-event 결과는 입력 근거·통제군·단위가 없으면 제한적이다. |
| 충돌 | 사용자는 기업가치 분석을 원하지만 재무 원천이 없는 기업은 정렬·평가할 수 없다.<br>실시간 provider 호출은 비용·권한·rate limit 때문에 기본 자동행동이 될 수 없다. |
| 미구현 | company-intelligence-analysis SKILL.md<br>CIL project-root 안정화 안내<br>기업분석 artifact adapter<br>결과 설명 template |
| 선택지 | A-REIMPLEMENT-CIL-IN-SKILL: 스킬 내부 스크립트가 CIL의 정규화·검색·분석 계산을 다시 구현한다.; B-THIN-CIL-ORCHESTRATOR: 스킬은 CIL 명령 선택·입력 검증·근거 해석·보고만 담당하고 계산은 CIL에 위임한다. |
| 권장안 | B-THIN-CIL-ORCHESTRATOR |
| 권장 근거 | 기업분석 수치의 계산 정본을 하나로 유지하고 스킬은 목적 라우팅과 증거 해석에 집중해야 한다. |
| 파급효과 | 데이터: CIL 결과와 source limitations를 그대로 보존한다.<br>스키마/API: known-company analysis 요청·EvidenceBundleRef 출력을 정의한다.<br>사용자 경험: 회사 발견과 회사 검증의 차이를 명시한다.<br>성능: CIL 캐시·snapshot을 재사용한다.<br>비용: 무료 원천 우선이며 외부 호출은 별도 권한이다.<br>보안: 비밀·PII를 보고서에 포함하지 않는다.<br>마이그레이션: repo root 자동 탐색 또는 명시 인자가 필요하다.<br>테스트: CIL 부재·cwd 변경·분석불가·부분 coverage를 검증한다. |
| 기회비용 | 범용 웹 경쟁사 발굴은 이 스킬만으로 완료하지 않는다. |
| 선행 결정 | D-01<br>D-03<br>D-09 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-THIN-CIL-ORCHESTRATOR<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/skills/company-intelligence-analysis/SKILL.md<br>.codex/skills/company-intelligence-analysis/agents/openai.yaml<br>.codex/skills/company-intelligence-analysis/references/analysis-routing.md<br>.codex/skills/company-intelligence-analysis/references/output-contract.md<br>.codex/skills/company-intelligence-analysis/scripts/verify_cil_artifact.py |
| 구현 변경 ID | C03-001<br>C03-002<br>C03-003<br>C03-004<br>C03-005 |
| 검증 기준 | 스킬이 CIL 계산식을 복제하지 않음<br>회사 미식별과 필드 미제공을 0으로 해석하지 않음<br>provider 호출은 명시 승인 없이는 수행하지 않음<br>명시 project root로 repo 밖 cwd에서도 CIL을 실행함<br>고정 probe를 production discovery로 표현하지 않음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/company-analysis-cil-runtime.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.png |
| 구현 맥락 topic | company-analysis-skill |

## 5. 창업분석 스킬의 실행·출력·한계 계약 (`D-05`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 창업분석 스킬이 시장기회·경쟁·방어력·창업자 자원을 어떻게 판단하고 CIL 기업증거는 언제 선택적으로 사용할 것인가? |
| 누가 | 한국에서 방어 가능한 사업기회를 찾고 검증하려는 창업자와 조사 에이전트 |
| 무엇을 | 창업자 제약, 시장유형, 근거·권리, 시장·경쟁, 장벽·자원, gap-driven 증강조사와 venture DomainPlan을 생성한다. |
| 어디서 | 신규 스킬의 schema·workflow 안에서 동작하고 알려진 경쟁사 검증이 필요할 때만 CIL EvidenceBundleRef를 읽는다. |
| 언제 | 문제·고객·지역·기간·가용자원 범위를 잠근 뒤 baseline 조사와 gap 분석을 순차 수행한다. |
| 왜 | 회사 재무 비교만으로 시장 수요·대체수단·조달·규제·현장 실행 가능성을 판단할 수 없다. |
| 어떻게 | 기존 창업 캠페인의 8개 결정 모델을 입력으로 재사용하되 이 저장소에서 독립 구현하고, CIL 연동은 competitor/company evidence가 필요한 gap에만 요청한다. |
| 근거 | EV-VENTURE-CAMPAIGN — /home/ubuntu/root/agents/docs/decision-campaigns/2026-09-15/kr-defensible-venture-discovery-skill-20260915/campaign.json — 창업자 제약·시장유형·증거·경쟁·장벽·증강조사·재사용·검증의 8개 결정이 decision-required 상태로 구성되어 있다.<br>EV-VENTURE-WORKBOOK — /home/ubuntu/root/agents/docs/decision-campaigns/2026-09-15/kr-defensible-venture-discovery-skill-20260915/decision-workbook.md — 시장크기·경쟁도·대체수단과 장벽·자원 적합성을 단일 점수가 아닌 분리 레코드로 다루는 권장안이 정리되어 있다. |
| 관찰 사실 | 기존 창업 캠페인은 설계 근거이며 현재 캠페인의 D-05 승인이 구현 의미의 정본이다.<br>CIL은 식별된 회사 분석에는 유용하지만 시장 문제 발견과 창업자 자원 검증을 소유하지 않는다.<br>공개 기업 자료가 없거나 비상장·수작업·현상유지 경쟁자는 CIL만으로 분석할 수 없다. |
| 충돌 | 기존 /home/ubuntu/root/agents 캠페인을 복사하면 두 정본이 생길 수 있다.<br>창업 스킬이 CIL을 필수로 만들면 CIL coverage 밖 기회를 부당하게 배제한다. |
| 미구현 | kr-defensible-venture-discovery SKILL.md<br>창업 schema·validator<br>venture DomainPlan generator<br>선택적 CIL evidence request/consume 절차 |
| 선택지 | A-CIL-CENTRIC-VENTURE-SKILL: 모든 창업 후보를 CIL 기업·재무 데이터로 평가하고 CIL 결과가 없는 후보는 제외한다.; B-INDEPENDENT-VENTURE-WITH-OPTIONAL-CIL: 창업 스킬은 독립 조사·판단 엔진을 가지며 식별된 경쟁사·기업 검증 gap에만 CIL bundle을 선택 소비한다. |
| 권장안 | B-INDEPENDENT-VENTURE-WITH-OPTIONAL-CIL |
| 권장 근거 | 창업기회 검증의 중심은 시장·고객·장벽·자원이며 기업 데이터는 특정 경쟁사 주장을 보강하는 선택 근거여야 한다. |
| 파급효과 | 데이터: venture evidence와 company evidence를 별도 type으로 보존한다.<br>스키마/API: optional company_evidence_refs와 venture DomainPlan을 정의한다.<br>사용자 경험: 근거 부족·현장검증 필요·blocked 상태를 숨기지 않는다.<br>성능: gap 우선 조사로 호출을 줄인다.<br>비용: 무료 공식 원천을 우선하고 유료 자료를 필수화하지 않는다.<br>보안: 창업자 자원·개인정보를 공개 bundle과 분리한다.<br>마이그레이션: 기존 agents 캠페인은 역사적 근거로 고정하고 본 저장소 캠페인이 구현 정본이 된다.<br>테스트: CIL 없는 독립 실행, 변조 bundle 거부, 대체수단 누락 gate를 검증한다. |
| 기회비용 | 기업 재무 점수 하나로 창업후보를 빠르게 줄이는 방식은 사용하지 않는다. |
| 선행 결정 | D-01<br>D-03<br>D-10 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-INDEPENDENT-VENTURE-WITH-OPTIONAL-CIL<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/skills/kr-defensible-venture-discovery/SKILL.md<br>.codex/skills/kr-defensible-venture-discovery/agents/openai.yaml<br>.codex/skills/kr-defensible-venture-discovery/references/market-archetypes.md<br>.codex/skills/kr-defensible-venture-discovery/references/research-workflow.md<br>.codex/skills/kr-defensible-venture-discovery/references/evidence-and-barriers.md<br>.codex/skills/kr-defensible-venture-discovery/references/venture-session.schema.json<br>.codex/skills/kr-defensible-venture-discovery/references/opportunity-hypothesis.schema.json<br>.codex/skills/kr-defensible-venture-discovery/scripts/venture_artifacts.py |
| 구현 변경 ID | C04-001<br>C04-002<br>C04-003<br>C04-004<br>C04-005<br>C04-006<br>C04-007<br>C04-008 |
| 검증 기준 | CIL 없이도 창업 core workflow가 실행됨<br>CIL bundle은 경쟁사 gap이 있을 때만 요구됨<br>직접 경쟁사 0건이 미개척 확정으로 변환되지 않음<br>venture DomainPlan의 단계마다 evidence 또는 unresolved gate가 존재함 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/venture-discovery-connectors.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.png |
| 구현 맥락 topic | venture-analysis-skill |

## 6. 무료 MCP·외부 연결 후보 채택 정책 (`D-06`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 무료 기업·동향 연결 후보 중 무엇을 즉시 의존성으로 채택하고 무엇을 후보 레지스트리로만 유지할 것인가? |
| 누가 | 기업분석·창업분석 스킬과 CIL provider 운영자 |
| 무엇을 | 무료·무키·공식성·추가 coverage·권리·provenance·중복·유지보수 기준으로 MCP 후보를 판별한다. |
| 어디서 | 무료 connector 후보 레지스트리와 향후 provider governance 결정에서 적용한다. |
| 언제 | 스킬 구현 전에는 dependency-free 기본값을 정하고 각 connector 채택 시 별도 검증한다. |
| 왜 | 무료 표방은 무제한·무계정·재배포 가능·공식 데이터와 같지 않으며 중복 래퍼는 공격면만 늘릴 수 있다. |
| 어떻게 | 현재는 즉시 채택 0개로 두고 ARES/OpenDART MCP를 중복 후보, Octagon/Tako를 약관·coverage 보류, Yahoo 직접 접근을 비공식 참고로 분류한다. |
| 근거 | EV-FREE-CONNECTOR-AUDIT — docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/evidence/free-connector-candidate-audit.json — 즉시 채택 0개, 무료 공식원천 래퍼 후보 2개, hosted 보류 2개, 방법 참고 1개로 판별했다.<br>EV-PROVIDER-CLUSTERS — src/company_intel/provider_clusters.py — CIL은 wire format이 아니라 질문별 provider 역할과 production disposition을 이미 분리한다. |
| 관찰 사실 | 체코 ARES 무료·무키 MCP와 한국 OpenDART 무료키 MCP 후보가 존재한다.<br>두 후보 모두 CIL이 직접 사용하는 원천과 중복된다.<br>Octagon과 Tako의 무료 tier는 영구 무료 범위·재배포·세 국가 coverage가 확정되지 않았다.<br>현재 세션에는 이들 기업분석 MCP가 연결되어 있지 않다. |
| 충돌 | MCP는 에이전트 사용성을 높일 수 있지만 CIL 내부 adapter보다 필드 통제와 공급망 위험이 늘 수 있다.<br>무료 Yahoo 데이터는 coverage가 넓지만 비공식 endpoint라 production evidence로 약하다. |
| 미구현 | connector-candidate.schema.json<br>중복 필드 diff·license·security·rate-limit gate<br>MCP adapter sandbox test |
| 선택지 | A-INSTALL-FREE-CANDIDATES-NOW: 무료 표방 후보를 스킬의 기본 MCP dependency로 즉시 설치한다.; B-CANDIDATE-REGISTRY-WITH-GATES: 신규 스킬은 외부 MCP 비종속으로 만들고 무료 후보는 중복·추가가치·약관·보안 검증 후에만 별도 채택한다. |
| 권장안 | B-CANDIDATE-REGISTRY-WITH-GATES |
| 권장 근거 | 현재 발견된 무료 MCP는 새로운 원천이 아니라 대부분 기존 공식 API의 래퍼이므로 설치 이득이 종속성 비용보다 크다는 증거가 없다. |
| 파급효과 | 데이터: 공식 직접 원천 우선순위를 유지한다.<br>스키마/API: connector candidate와 production provider를 분리한다.<br>사용자 경험: 연결 없음·보류·사용 가능 상태를 명시한다.<br>성능: 기본 실행에 외부 MCP hop이 없다.<br>비용: 유료·freemium 의존성을 강제하지 않는다.<br>보안: MCP 공급망 감사 전 실행하지 않는다.<br>마이그레이션: 추가가치가 입증된 connector만 별도 결정으로 승격한다.<br>테스트: no-MCP 기본 동작과 connector capability diff를 검증한다. |
| 기회비용 | 현재 즉시 가져올 새 연결구는 0개로 남는다. |
| 선행 결정 | D-03 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-CANDIDATE-REGISTRY-WITH-GATES<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/shared/company-intelligence-interop/connector-candidates.json<br>.codex/shared/company-intelligence-interop/BOUNDARIES.md |
| 구현 변경 ID | C01-007<br>C01-008 |
| 검증 기준 | 무료 표방만으로 production 승격되지 않음<br>기존 CIL과 중복 시 필드 또는 운영상 추가가치를 요구<br>비공식 endpoint는 authoritative fact 단독 근거가 아님<br>연결 MCP 0개 환경에서도 두 스킬 core 동작 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/venture-discovery-connectors.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/venture-discovery-connectors.png |
| 구현 맥락 topic | interop-control |

## 7. decision-campaign-workbook 라우팅과 비복제 경계 (`D-07`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 두 도메인 스킬이 decision-campaign-workbook을 상속·복사하지 않고도 복수 의사결정에 선택적으로 연결되려면 어떻게 해야 하는가? |
| 누가 | 기업·창업 분석 사용자, 도메인 스킬, decision-campaign-workbook control plane |
| 무엇을 | 도메인 스킬은 단일 분석을 독립 수행하고 복수 결정·승인·cohort가 필요할 때만 캠페인 라우팅 제안을 생성한다. |
| 어디서 | 스킬의 routing-boundary 문서와 CampaignLink artifact에 적용한다. |
| 언제 | 상충하는 대안, 복수 승인자, 단계별 구현·검증, scope revision이 필요한 경우에만 라우팅한다. |
| 왜 | 캠페인 스킬을 복사하거나 상속하면 scope lock·승인·receipt 정본이 여러 개 생기고 단순 분석도 과도하게 무거워진다. |
| 어떻게 | 새 스킬은 캠페인 도구를 내부 호출하지 않고 campaign proposal 또는 CampaignLink를 출력하며, 실제 캠페인 동작은 사용자가 decision-campaign-workbook을 명시했을 때 그 스킬만 수행한다. |
| 근거 | EV-DECISION-CAMPAIGN-SKILL — /home/ubuntu/.codex/skills/decision-campaign-workbook/SKILL.md — 이 스킬은 명시 호출 시에만 여러 제품 결정·scope·승인·cohort·receipt의 control plane을 소유한다.<br>EV-PLAN-BOUNDARY-D02 — /home/ubuntu/.codex/skills/decision-campaign-workbook/references/decision-campaign.schema.json — 캠페인 JSON의 정식 cohort plan과 구현 권한 필드가 도메인 계획 파일과 분리되어 있다. |
| 관찰 사실 | decision-campaign-workbook은 명시 호출 전용이며 다른 스킬의 하위 실행 ledger가 아니다.<br>도메인 분석 한 건이 항상 복수 제품 결정이나 코드 구현을 포함하는 것은 아니다.<br>CampaignLink는 외부 campaign_id·scope_sha·decision_ids·artifact hashes를 참조할 수 있다. |
| 충돌 | 자동 라우팅은 편리하지만 사용자의 명시 호출 조건과 승인 경계를 넘을 수 있다.<br>복사는 독립 배포를 쉽게 보이게 하지만 control-plane drift를 만든다. |
| 미구현 | campaign-routing-policy.md<br>campaign-link.schema.json<br>campaign proposal template<br>잘못된 자동 승인 방지 테스트 |
| 선택지 | A-COPY-OR-INHERIT-CAMPAIGN-SKILL: 각 도메인 스킬 안에 decision-campaign-workbook의 지침·도구·상태머신을 복사하거나 상속한다.; B-OPTIONAL-ROUTER-NO-INHERITANCE: 도메인 스킬은 독립 실행하고 필요 시 캠페인 proposal/Link만 만들며 승인·cohort·구현 원장은 decision-campaign-workbook에만 둔다. |
| 권장안 | B-OPTIONAL-ROUTER-NO-INHERITANCE |
| 권장 근거 | 상속·복사보다 하나의 control plane과 명시적 artifact reference가 승인·scope·receipt 의미를 보존한다. |
| 파급효과 | 데이터: CampaignLink에는 최소 ID·path·hash만 둔다.<br>스키마/API: domain plan과 campaign implementation plan을 교차 참조하되 합치지 않는다.<br>사용자 경험: 캠페인이 필요한 이유와 다음 명령을 제안한다.<br>성능: 불필요한 캠페인 문서 생성을 피한다.<br>비용: 새 control plane을 만들지 않는다.<br>보안: 도메인 스킬이 승인이나 구현 권한을 생성하지 못한다.<br>마이그레이션: 상위 스킬 변경을 복제할 필요가 없다.<br>테스트: 명시 호출·권한 없음·잘못된 scope SHA를 검증한다. |
| 기회비용 | 도메인 스킬 하나만으로 캠페인 승인을 자동 완료하지 않는다. |
| 선행 결정 | D-02<br>D-03 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-OPTIONAL-ROUTER-NO-INHERITANCE<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/shared/company-intelligence-interop/campaign-link.schema.json<br>.codex/shared/company-intelligence-interop/BOUNDARIES.md |
| 구현 변경 ID | C01-006<br>C01-008 |
| 검증 기준 | 도메인 스킬이 decision disposition을 자동 기록하지 않음<br>CampaignLink scope SHA 불일치 시 stale<br>캠페인 미사용 단순 분석이 정상 동작<br>decision-campaign-workbook 지침을 복사한 파일이 없음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/skill-domain-routing.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.png |
| 구현 맥락 topic | interop-control |

## 8. 패키징·발견성·행동 검증 계약 (`D-08`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 두 스킬을 실제 Codex에서 발견·선택·실행·연동할 수 있음을 어떤 검증으로 입증할 것인가? |
| 누가 | 스킬 작성자, 미래 Codex 에이전트와 사용자 |
| 무엇을 | 구조 감사, trigger 행동시험, CIL 실행경로, artifact 변조·stale·fallback, campaign routing을 검증한다. |
| 어디서 | 저장소 skill 패키지, 격리된 테스트 환경, CIL 프로젝트 안팎 cwd에서 수행한다. |
| 언제 | 두 스킬과 공유 계약 구현 뒤 설치·배포 주장 전에 수행한다. |
| 왜 | SKILL.md가 존재하거나 정적 schema를 통과하는 것만으로 실제 활성화·비활성화·도구 실행·안전한 실패를 증명하지 못한다. |
| 어떻게 | skill-creator로 작성하고 skill2-audit와 skill2-test를 각각 구조·행동 검증에 사용하며 CIL offline fixtures와 tamper fixtures를 실행한다. |
| 근거 | EV-CIL-CONFIG-CWD — src/company_intel/config.py — Settings.from_env는 명시 project_root가 없으면 Path.cwd()를 사용하므로 설치된 CLI/스킬의 cwd 독립성을 별도 검증해야 한다.<br>EV-CIL-CLI-CWD — src/company_intel/cli.py — 현재 CLI main은 Settings.from_env(Path.cwd())를 호출한다.<br>EV-CIL-PROJECT-METADATA — pyproject.toml — CIL 패키지와 console entrypoint의 설치·실행 기반이 정의되어 있다. |
| 관찰 사실 | 저장소 로컬 company-intel-cli 스킬은 현재 세션의 사용 가능 스킬 목록에 자동 노출되지 않았다.<br>설치된 company-intel 명령은 cwd에 따라 config 경로가 달라질 수 있다.<br>구조 검증과 trigger 행동 검증은 서로 다른 증거다. |
| 충돌 | repo 안에서만 통과하는 smoke는 전역 사용을 증명하지 못한다.<br>provider live test는 외부 권한·키·변동성 때문에 스킬 core 검증과 분리해야 한다. |
| 미구현 | 두 스킬 구조·행동 test matrix<br>격리 설치 smoke<br>cwd 독립 CIL launcher 또는 명시 root 계약<br>artifact tamper fixtures<br>turnover receipt |
| 선택지 | A-STRUCTURE-ONLY-VALIDATION: SKILL.md frontmatter와 파일 존재만 검사해 완료로 판정한다.; B-STRUCTURAL-AND-BEHAVIORAL-VALIDATION: 구조 감사와 격리 trigger·CLI·artifact·routing 행동시험을 분리 실행한다. |
| 권장안 | B-STRUCTURAL-AND-BEHAVIORAL-VALIDATION |
| 권장 근거 | 사용자가 실제 구성 가능한 스킬을 원하므로 파일 존재가 아니라 올바른 활성화·실행·증거 거부·독립성까지 입증해야 한다. |
| 파급효과 | 데이터: 테스트 fixture와 receipt가 plan SHA에 결속된다.<br>스키마/API: 각 공유 schema validator를 실행한다.<br>사용자 경험: 한국어 실패 설명과 다음 행동을 검증한다.<br>성능: offline core와 optional provider test를 분리한다.<br>비용: 무료·offline 기본 검증을 우선한다.<br>보안: secret·PII·path traversal·hash tamper를 검사한다.<br>마이그레이션: 전역 설치 전 프로젝트 로컬 발견성부터 검증한다.<br>테스트: skill2-audit, skill2-test, pytest, cwd smoke, interop replay가 필요하다. |
| 기회비용 | 외부 provider live 증거가 없는 상태에서는 해당 connector 지원을 완료로 주장하지 않는다. |
| 선행 결정 | D-04<br>D-05<br>D-06<br>D-07<br>D-09<br>D-10 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-STRUCTURAL-AND-BEHAVIORAL-VALIDATION<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | tests/skills/test_company_intelligence_analysis_skill.py<br>tests/skills/test_venture_discovery_skill.py<br>tests/skills/test_skill_artifact_interop.py |
| 구현 변경 ID | C05-001<br>C05-002<br>C05-003 |
| 검증 기준 | 두 신규 스킬이 skill-creator quick_validate와 skill2-audit를 통과함<br>기존 커리어 스킬과 두 신규 스킬의 양성·음성·교차 trigger 경계가 검토됨<br>repo 밖 cwd CIL 호출이 명시 root로 성공함<br>변조·stale·wrong-kind bundle과 DomainPlanRef를 거부함<br>외부 MCP 없이 창업 core workflow와 DualPathComparison을 검증함 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/flowchart-source-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/flowchart-design-review.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/flowchart-semantic-review.md<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/validation-pipeline.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.png |
| 구현 맥락 topic | packaging-validation |

## 9. CIL 실행 위치·출력·fixture 경계 (`D-09`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업분석 스킬이 저장소 밖에서도 CIL을 안전하게 실행하고 fixture와 production 결과를 혼동하지 않도록 어떤 실행 계약을 둘 것인가? |
| 누가 | CIL을 thin orchestrator로 호출하는 기업분석 스킬과 그 결과를 소비하는 사용자 |
| 무엇을 | 명시적 project root, versioned JSON 결과, fixture/production 구분과 실패 envelope를 제공한다. |
| 어디서 | CIL CLI 설정·명령 파서와 저장소 밖 cwd smoke test에 적용한다. |
| 언제 | company-intelligence-analysis 스킬 구현과 행동시험보다 먼저 적용한다. |
| 왜 | 현재 CLI는 Path.cwd()를 project root로 고정해 저장소 밖에서 실패하고 고정 probe가 제품 분석으로 오인될 수 있다. |
| 어떻게 | --project-root/--프로젝트-경로와 COMPANY_INTEL_PROJECT_ROOT를 지원하고 probe 목적을 결과에 보존하며 구조화 오류를 반환한다. |
| 근거 | EV-D09-CONFIG — src/company_intel/config.py — Settings.from_env는 명시값이 없을 때 Path.cwd()를 root로 사용한다.<br>EV-D09-CLI — src/company_intel/cli.py — CLI main은 Settings.from_env(Path.cwd())를 직접 호출한다.<br>EV-D09-PROVIDERS — config/providers.json — semantic_contract는 고정 기업 probe가 connector health fixture이며 production discovery가 아니라고 선언한다. |
| 관찰 사실 | 저장소 밖 cwd에서 company-intel 원천-상태가 FileNotFoundError로 실패한다.<br>connector registry에는 probe와 production 선택 경계가 이미 존재한다.<br>기존 97개 테스트는 통과하지만 저장소 밖 cwd 계약은 포함하지 않는다. |
| 충돌 | 패키지 위치를 자동 탐색하면 편리하지만 여러 checkout이 있을 때 모호해진다.<br>stack trace는 개발에는 유용하지만 스킬 소비자에게 안정된 실패 계약이 아니다. |
| 미구현 | 전역 project-root 인자와 환경변수 우선순위<br>저장소 밖 cwd 회귀시험<br>기업분석 스킬용 구조화 실행 실패 계약 |
| 선택지 | A-SKILL-CWD-WORKAROUND: 스킬이 매번 저장소로 cd한 뒤 CIL을 호출하고 CIL 자체 계약은 바꾸지 않는다.; B-EXPLICIT-ROOT-AND-PURPOSE-CONTRACT: CIL에 명시적 root 해석과 구조화 실패를 추가하고 fixture/production 목적을 보존한다. |
| 권장안 | B-EXPLICIT-ROOT-AND-PURPOSE-CONTRACT |
| 권장 근거 | thin skill의 계산 정본을 CIL로 유지하려면 CIL 자체가 호출 위치와 분석 목적을 명시적으로 받아야 한다. |
| 파급효과 | 데이터: project root와 artifact root가 재현 가능해진다.<br>스키마/API: 기존 명령과 호환되는 전역 인자를 추가한다.<br>사용자 경험: 저장소 밖에서도 명시 root로 실행한다.<br>성능: 영향은 무시할 수준이다.<br>비용: 세 파일과 회귀시험 범위다.<br>보안: 외부 provider 호출 권한은 추가하지 않는다.<br>마이그레이션: 기존 cwd 동작을 fallback으로 유지한다.<br>테스트: repo 외부 cwd와 잘못된 root를 검증한다. |
| 기회비용 | 자동 checkout 탐색은 제공하지 않아 사용자가 root를 지정해야 할 수 있다. |
| 선행 결정 | D-01 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-EXPLICIT-ROOT-AND-PURPOSE-CONTRACT<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | src/company_intel/config.py<br>src/company_intel/cli.py<br>.codex/skills/company-intel-cli/SKILL.md<br>tests/test_cli_project_root.py |
| 구현 변경 ID | C02-001<br>C02-002<br>C02-003<br>C02-004 |
| 검증 기준 | 명시 root로 저장소 밖 cwd에서 원천-상태가 실행됨<br>환경변수보다 CLI 인자가 우선함<br>잘못된 root는 config 경로를 포함한 명확한 오류를 냄<br>기존 저장소 cwd 동작과 97개 회귀시험이 유지됨 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/company-analysis-cil-runtime.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/company-analysis-cil-runtime.png |
| 구현 맥락 topic | cil-runtime-readiness |

## 10. 3개 사용자 스킬과 DualPathComparison 소유권 (`D-10`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업·취업·창업의 세 책임을 유지하면서 취업과 창업 계획을 비교하는 공통 산출물을 누가 소유할 것인가? |
| 누가 | 기업분석·기존 커리어 조사·창업분석 스킬과 두 경로를 비교하는 사용자 |
| 무엇을 | 세 사용자 스킬은 독립 유지하고 DualPathComparison은 호출 가능한 버전드 비스킬 interop 계약으로 둔다. |
| 어디서 | 저장소의 .codex/skills 두 신규 스킬과 .codex/shared/company-intelligence-interop에 적용한다. |
| 언제 | CareerDomainPlan과 VentureDomainPlan이 모두 존재할 때만 비교 산출물을 생성한다. |
| 왜 | 네 번째 라우터 스킬은 트리거와 책임을 늘리고 campaign 상속은 승인 원장을 중복시킨다. |
| 어떻게 | 공통 validator가 plan hash·기간·통화·근거를 확인하고 비교 가능한 축과 미해결 축만 DualPathComparison으로 만든다. |
| 근거 | EV-D10-CAREER-SKILL — /home/ubuntu/.codex/skills/company-intelligence-career-research/SKILL.md — 기존 커리어 스킬은 기업·직무 요건·자격증·준비사항 조사라는 독립 trigger를 가진다.<br>EV-D10-CAMPAIGN-BOUNDARY — /home/ubuntu/.codex/skills/decision-campaign-workbook/SKILL.md — decision-campaign-workbook은 명시 호출 전용 control plane이며 도메인 런타임을 소유하지 않는다. |
| 관찰 사실 | 기업분석과 창업분석 두 신규 스킬, 기존 커리어 스킬을 합치면 사용자 대면 책임은 세 개다.<br>두 DomainPlan의 해시·기간·근거가 일치해야 비교가 재현 가능하다.<br>공통 계약과 validator는 사용자 요청을 직접 받는 스킬이 아니다. |
| 충돌 | 네 번째 synthesis 스킬은 발견성을 높일 수 있지만 초기에는 trigger 중복과 유지비가 더 크다.<br>기존 글로벌 커리어 스킬은 현재 저장소의 구현 권한 밖이므로 이번 실행에서 복제하거나 수정하지 않는다. |
| 미구현 | DualPathComparison schema<br>career/venture DomainPlan 검증과 비교 CLI<br>세 스킬 경계 및 비교 불가 상태 시험 |
| 선택지 | A-FOURTH-SYNTHESIS-SKILL: 취업·창업 통합 비교만 담당하는 네 번째 사용자 스킬을 추가한다.; B-THREE-SKILLS-SHARED-COMPARISON-CONTRACT: 세 사용자 스킬을 유지하고 DualPathComparison은 비스킬 공통 계약·CLI가 소유한다. |
| 권장안 | B-THREE-SKILLS-SHARED-COMPARISON-CONTRACT |
| 권장 근거 | 현재는 세 책임이 이미 구분되며 비교는 두 산출물의 검증 가능한 조합이므로 네 번째 스킬보다 작은 공통 계약이 적합하다. |
| 파급효과 | 데이터: CareerDomainPlan·VentureDomainPlan·DualPathComparison이 독립 hash를 가진다.<br>스키마/API: plan_kind와 comparison status를 제한한다.<br>사용자 경험: 비교 불가 이유를 unresolved로 반환한다.<br>성능: 중복 도메인 조사를 하지 않는다.<br>비용: 공통 표면을 최소화한다.<br>보안: 개인 원문은 bundle에 복사하지 않는다.<br>마이그레이션: 향후 반복 수요가 입증되면 네 번째 스킬을 별도 결정한다.<br>테스트: 세 스킬 경계와 비교 validator를 시험한다. |
| 기회비용 | 한 번의 암묵적 스킬 호출로 세 도메인을 모두 실행하지 않는다. |
| 선행 결정 | D-01<br>D-02<br>D-03 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-THREE-SKILLS-SHARED-COMPARISON-CONTRACT<br>규칙: 사용자의 FULL_EXECUTION 요청에 따라 각 결정의 B 권장안을 승인한다.<br>근거: 비판적 검증에서 확인된 수정사항과 D-09·D-10을 포함한 개정 범위를 구현한다.<br>결정자: user<br>결정 시각: 2026-09-15T05:28:25.724684+00:00 |
| 구현 대상 | .codex/shared/company-intelligence-interop/domain-plan.schema.json<br>.codex/shared/company-intelligence-interop/domain-plan-ref.schema.json<br>.codex/shared/company-intelligence-interop/dual-path-comparison.schema.json<br>.codex/shared/company-intelligence-interop/interop.py<br>.codex/shared/company-intelligence-interop/BOUNDARIES.md |
| 구현 변경 ID | C01-002<br>C01-005<br>C01-008<br>C01-009<br>C05-003 |
| 검증 기준 | career와 venture 계획이 모두 없으면 비교 생성 거부<br>입력 plan hash 불일치 시 stale 반환<br>비교 불가능한 단위·기간을 점수로 강제 변환하지 않음<br>네 번째 사용자 스킬이나 campaign 지침 복제본을 만들지 않음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/skill-domain-routing.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/skill-domain-routing.png<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/plan-evidence-interop.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/plan-evidence-interop.png |
| 구현 맥락 topic | interop-control |

## 11. 결정론적 다이어그램 검증·렌더링 도구체인 (`D-11`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 캠페인 다이어그램을 저장소 자체에서 검증·컴파일·SVG/PNG 렌더·freshness 검사할 도구체인을 어떤 경계로 소유할 것인가? |
| 누가 | 캠페인 다이어그램 작성 에이전트와 저장소 검증 실행자 |
| 무엇을 | 저장소 로컬 Python 검증·컴파일 CLI와 정확히 고정된 Mermaid CLI 렌더러를 추가한다. |
| 어디서 | tools/flowchart_matrix.py, tools/mermaid-renderer, tests/tools에 둔다. |
| 언제 | 승인된 flowchart-design-review와 flowchart matrix를 파생 Mermaid·SVG·PNG로 만들거나 freshness를 확인할 때 실행한다. |
| 왜 | 외부 스킬 경로와 전역 도구에 의존하면 저장소 단독 재현, exact plan SHA, 결과 receipt 결속을 보장할 수 없다. |
| 어떻게 | Python은 의미·그래프·coverage와 파생물 freshness를 검증하고, lockfile로 고정된 mmdc CLI가 명시된 로컬 Chrome으로 SVG와 PNG를 렌더한다. |
| 근거 | EV-D11-DEPENDENCY-CATALOG — docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/evidence/diagram-toolchain-dependency-catalog.json — 저장소에는 다이어그램 도구나 Node manifest가 없고 외부 스킬 validator와 시스템 Chrome만 관찰되었다.<br>EV-D11-INTEGRATION-MATRIX — docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/evidence/diagram-toolchain-integration-matrix.md — Mermaid CLI의 semver 적용 CLI 경계, mmdc 옵션, Puppeteer config, SVG/PNG 및 실패 검증 조건이 ready-for-implementation으로 정리되었다.<br>EV-D11-EXTERNAL-VALIDATOR — /home/ubuntu/.codex/skills/flowchart-matrix-validation/scripts/validate_flowchart_matrix.py — 외부 스킬에는 evidence, design, matrix 검증과 Mermaid 컴파일 구현이 있지만 저장소에는 해당 실행 파일이 없다. |
| 관찰 사실 | 현재 저장소에는 tools/flowchart_matrix.py, package.json, package-lock.json, mmdc가 없다.<br>현재 실행 환경에는 Node 22.21.0과 /usr/bin/google-chrome가 존재한다.<br>공식 npm 조회에서 @mermaid-js/mermaid-cli 최신 버전은 11.17.0, 라이선스는 MIT, Node 요구사항은 ^18.19 또는 >=20.0이다.<br>Mermaid CLI는 .mmd에서 SVG와 PNG를 생성하며 잘못된 Mermaid 입력에서 non-zero 오류를 낸다.<br>Node 프로그램 API는 semver 대상이 아니므로 CLI 경계가 더 안정적이다. |
| 충돌 | 시스템 Chrome을 쓰면 브라우저 다운로드를 피하지만 Chrome 업데이트가 결과 바이트에 영향을 줄 수 있으므로 환경 receipt와 freshness 검사가 필요하다.<br>SVG와 PNG byte 비교는 강한 재현성 검사지만 렌더러 또는 브라우저 버전 변경 시 의도적인 재생성과 새 승인이 필요하다. |
| 미구현 | 저장소 로컬 evidence/design/matrix validator와 Mermaid compiler<br>정확한 Mermaid CLI dependency와 lockfile<br>SVG·PNG 렌더 및 byte-for-byte freshness 검사<br>유효·무효·stale 입력과 renderer preflight에 대한 테스트 |
| 선택지 | A-EXTERNAL-SKILL-ONLY: 외부 flowchart skill 스크립트와 사용 시점의 전역/npx 렌더러만 사용한다.; B-REPOSITORY-PINNED-TOOLCHAIN: 저장소 로컬 Python CLI, pinned Mermaid CLI lockfile, 명시적 Chrome config와 양·음성·freshness 시험을 추가한다. |
| 권장안 | B-REPOSITORY-PINNED-TOOLCHAIN |
| 권장 근거 | 캠페인의 exact-plan·source-hash·receipt 원칙을 다이어그램에도 적용하려면 외부 스킬이나 전역 도구가 아니라 저장소가 검증 CLI와 렌더러 버전을 소유해야 한다. |
| 파급효과 | 데이터: 다이어그램 evidence, design, matrix, Mermaid, SVG, PNG 사이의 파생 관계와 hash를 검증한다.<br>스키마/API: 저장소 로컬 diagram CLI 명령과 구성 파일을 추가한다.<br>사용자 경험: 작성자는 외부 스킬 경로 대신 저장소 명령을 실행한다.<br>성능: 브라우저 다운로드 없이 로컬 Chrome으로 다섯 diagram을 순차 렌더한다.<br>비용: 라이선스 비용은 없고 Node 설치·업데이트 유지비만 발생한다.<br>보안: 외부 데이터 전송 없이 strict Mermaid 설정과 고정 dependency integrity를 사용한다.<br>마이그레이션: 현재 다이어그램 경로는 유지하고 생성 도구만 새 정본으로 도입한다.<br>테스트: Python 단위시험과 실제 mmdc SVG/PNG 통합시험을 분리한다. |
| 기회비용 | 도구체인 승인을 위한 별도 cohort와 plan SHA가 필요하다. |
| 선행 결정 | D-08 |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-REPOSITORY-PINNED-TOOLCHAIN<br>규칙: 사용자가 D-11의 B 권장안 승인, PREPARE, 생성 Plan SHA 결속, IMPLEMENT와 VALIDATE를 명시적으로 승인했다.<br>근거: 저장소 소유 검증·렌더링 도구체인으로 다이어그램의 plan SHA와 결과 receipt 재현성을 확보한다.<br>결정자: user<br>결정 시각: 2026-09-15T00:00:00+09:00 |
| 구현 대상 | .gitignore<br>tools/flowchart_matrix.py<br>tools/mermaid-renderer/package.json<br>tools/mermaid-renderer/package-lock.json<br>tools/mermaid-renderer/mermaid.config.json<br>tools/mermaid-renderer/puppeteer.local.json<br>tests/tools/test_flowchart_matrix.py<br>tests/tools/test_mermaid_renderer.py |
| 구현 변경 ID | file-change-11fe041e9525<br>file-change-2cb2323e87c8<br>file-change-368e35f4988c<br>file-change-46574042dc93<br>file-change-970fbb67544b<br>file-change-b9c763c03407<br>file-change-bc37d034bad5<br>file-change-cadd50729db0 |
| 검증 기준 | 저장소 외부 스킬 경로가 없어도 evidence·design·matrix 검증과 Mermaid 컴파일이 동작함<br>고정된 mmdc 11.17.0과 /usr/bin/google-chrome로 SVG 및 PNG를 생성함<br>유효하지 않은 evidence·design·matrix·Mermaid가 non-zero로 거부됨<br>생성물 누락·변조·source 또는 config 변경을 --check가 stale로 거부함<br>두 번 연속 렌더한 SVG와 PNG가 byte-for-byte 동일함<br>node_modules는 Git 추적 대상이 아니며 런타임 provider·secret·network가 필요 없음 |
| 다이어그램 영향 | docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/matrices/validation-pipeline.flowchart-matrix.json<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.mmd<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.svg<br>docs/decision-campaigns/2026-09-15/company-intelligence-dual-domain-skills-20260915/diagrams/mermaid/validation-pipeline.png |
| 구현 맥락 topic | diagram-toolchain<br>diagram-validation<br>mermaid-renderer |
