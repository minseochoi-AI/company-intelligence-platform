# company-intelligence-cross-region-career-preparation — 의사결정 워크북

> 이 파일은 `campaign.json`과 `decisions/*.json`에서 생성됩니다.
> JSON 정본의 사람용 서술을 한국어로 수정한 뒤 이 워크북을 다시 생성합니다.

## 캠페인 요약

| 항목 | 값 |
|---|---|
| 목표 | 미국·한국·EU/체코의 공개·무료 접근 가능 데이터로 국가별 기업·공고·요건을 근거 기반으로 분리·검색·내보내고, 동료군 순위·시간축 거시 비교·미래가치·AI 사건 검증까지 10개 사용자 기능으로 제공하는 설계를 고정한다. |
| 상태 | decision-approved |
| 생성일 | 2026-09-11 |
| 구현 승인 | 승인됨: True<br>승인자: user<br>승인 시각: 2026-09-13T08:19:05.623666+00:00<br>범위: ['D-01-source-access-policy', 'D-02-company-capability-taxonomy', 'D-03-search-profile-and-discovery', 'D-04-career-requirement-verification', 'D-05-spreadsheet-output-contract', 'D-06-peer-screener-ranking', 'D-07-company-timeline-macro-comparison', 'D-08-future-value-scenarios', 'D-09-ai-event-effect-validation', 'D-10-job-availability-filtered-discovery']<br>승인된 계획 참조: [{'cohort_id': 'C-01-source-identity-foundation', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-01-source-identity-foundation--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-01-source-identity-foundation-r3.json', 'sha256': '29b89c280e2598784e20d9ef213f83212b4cc62787e85e93fa0be336777cfd88'}, {'cohort_id': 'C-02-search-requirement-evidence', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-02-search-requirement-evidence--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-02-search-requirement-evidence-r3.json', 'sha256': 'c988fec11105b80a25a48e8bc881c8f98b26f9b2f14580d61c95637faf47d59c'}, {'cohort_id': 'C-03-evidence-export-delivery', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-03-evidence-export-delivery--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-03-evidence-export-delivery-r3.json', 'sha256': 'fa2933fb85bbcd306c70dfab4f10acc70968bcdcb9adc3bbbaa861a7022b4a8d'}, {'cohort_id': 'C-04-peer-screener-ranking', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-04-peer-screener-ranking--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-04-peer-screener-ranking-r3.json', 'sha256': 'a70a138b32038c0570d6c96466fdef0343448aadc583d4fb32b6bf68f733564c'}, {'cohort_id': 'C-05-timeline-valuation-event-analysis', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-05-timeline-valuation-event-analysis--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-05-timeline-valuation-event-analysis-r3.json', 'sha256': '0628be1faaa8c4b7cff99ad5e4a818848dd85d24d9e045a2d5bdb322cc1f88da'}, {'cohort_id': 'C-06-job-availability-filtered-discovery', 'plan_id': 'company-intelligence-cross-region-career-preparation--C-06-job-availability-filtered-discovery--r3', 'path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-06-job-availability-filtered-discovery-r3.json', 'sha256': 'aa1c4aa49fbcd3fe2e05a233c789b6b3588d3cc5d9588476aaec26c301ea8606'}] |
| Context Index | docs/implementation-context-index-cli-r2.json |
| 구현 cohort context | {'cohort_id': 'C-01-source-identity-foundation', 'decision_ids': ['D-01-source-access-policy', 'D-02-company-capability-taxonomy'], 'status': 'contract-ready', 'execution_dependencies': [], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-01-source-identity-foundation-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': '29b89c280e2598784e20d9ef213f83212b4cc62787e85e93fa0be336777cfd88', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-01-source-identity-foundation-r3.json', 'context_packet_sha256': '7f3fe344358072abf2ba0fc3fca6764dc79955f17a37c742cf1fb6405e67ad56'}<br>{'cohort_id': 'C-02-search-requirement-evidence', 'decision_ids': ['D-03-search-profile-and-discovery', 'D-04-career-requirement-verification'], 'status': 'contract-ready', 'execution_dependencies': ['C-01-source-identity-foundation'], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-02-search-requirement-evidence-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': 'c988fec11105b80a25a48e8bc881c8f98b26f9b2f14580d61c95637faf47d59c', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-02-search-requirement-evidence-r3.json', 'context_packet_sha256': 'c544a2291eebc94c1112486b8119f9c7d39ef0c45f665659f540a2b35f713cb3'}<br>{'cohort_id': 'C-03-evidence-export-delivery', 'decision_ids': ['D-05-spreadsheet-output-contract'], 'status': 'contract-ready', 'execution_dependencies': ['C-02-search-requirement-evidence'], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-03-evidence-export-delivery-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': 'fa2933fb85bbcd306c70dfab4f10acc70968bcdcb9adc3bbbaa861a7022b4a8d', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-03-evidence-export-delivery-r3.json', 'context_packet_sha256': '088b91f553349f61fe505d79cec02781d4451c2a92bf8c5ce331812b3e7ca5df'}<br>{'cohort_id': 'C-04-peer-screener-ranking', 'decision_ids': ['D-06-peer-screener-ranking'], 'status': 'contract-ready', 'execution_dependencies': ['C-01-source-identity-foundation'], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-04-peer-screener-ranking-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': 'a70a138b32038c0570d6c96466fdef0343448aadc583d4fb32b6bf68f733564c', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-04-peer-screener-ranking-r3.json', 'context_packet_sha256': '9a22f5e68ac3d652a014c33925016c2d3cf00165bc2e6bd3f6f73ae0924c04ef'}<br>{'cohort_id': 'C-05-timeline-valuation-event-analysis', 'decision_ids': ['D-07-company-timeline-macro-comparison', 'D-08-future-value-scenarios', 'D-09-ai-event-effect-validation'], 'status': 'contract-ready', 'execution_dependencies': ['C-04-peer-screener-ranking'], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-05-timeline-valuation-event-analysis-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': '0628be1faaa8c4b7cff99ad5e4a818848dd85d24d9e045a2d5bdb322cc1f88da', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-05-timeline-valuation-event-analysis-r3.json', 'context_packet_sha256': 'd7dc311e718c3e2c11dde3c208026e531d009997601adc7d0aad409833d369f8'}<br>{'cohort_id': 'C-06-job-availability-filtered-discovery', 'decision_ids': ['D-10-job-availability-filtered-discovery'], 'status': 'contract-ready', 'execution_dependencies': ['C-02-search-requirement-evidence', 'C-03-evidence-export-delivery', 'C-04-peer-screener-ranking', 'C-05-timeline-valuation-event-analysis'], 'implementation_plan_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/implementation-plans/C-06-job-availability-filtered-discovery-r3.json', 'implementation_plan_status': 'contract-ready', 'implementation_plan_sha256': 'aa1c4aa49fbcd3fe2e05a233c789b6b3588d3cc5d9588476aaec26c301ea8606', 'context_packet_path': 'docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/context-packets/C-06-job-availability-filtered-discovery-r3.json', 'context_packet_sha256': 'cb1f78d6900b7d6e31d4b1070a8927de394b64aae78b7df0c14ae27590a42c4f'} |
| 구현 영수증 | docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/receipts/implementation.json |
| 검증 영수증 | docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/receipts/validation-r3-offline-20260913.json |

## 의사결정 요약

| No | 작업 단위 | 상태 | 핵심 질문 | 권장안 | 선행 결정 | 사용자 결정 |
|---:|---|---|---|---|---|---|
| 1 | source-access-policy | accepted | 미국·한국·EU/체코 원천을 어떤 접근·권한·데이터 역할 기준으로 등록하고, 어떤 상태에서만 connector를 활성화할 것인가? | B-versioned-source-catalog | — | ACCEPT |
| 2 | company-capability-taxonomy | accepted | 기업별 재무·고용·채용·시장·거시 연결과 상관·인과 분석 가능 여부를 어떤 다축 taxonomy와 증거 기준으로 분류할 것인가? | B-multiaxis-capability-and-gates | D-01-source-access-policy | ACCEPT |
| 3 | search-profile-and-discovery | accepted | 사용자 목적에 맞는 기업을 재현 가능하게 찾기 위해 어떤 검색 프로필·후보 발견·적합성 설명 계약을 사용할 것인가? | B-explicit-profile-and-evidence-matching | D-02-company-capability-taxonomy | ACCEPT |
| 4 | career-requirement-verification | accepted | 기업별 채용공고의 자격증·학력·경력·언어·기술·준비사항을 어떤 원문·국가 기준·검증 상태로 구조화해 정확하게 반환할 것인가? | B-evidence-level-requirements | D-03-search-profile-and-discovery | ACCEPT |
| 5 | spreadsheet-output-contract | accepted | 기업·가용성·채용공고·자격요건·원천 근거·제외 사유를 어떤 스프레드시트 계약으로 반환해 사용자가 직접 검토하고 재현할 수 있게 할 것인가? | B-evidence-first-workbook-bundle | D-04-career-requirement-verification | ACCEPT |
| 6 | peer-screener-ranking | accepted | 사용자가 국가·산업·규모와 분석 변수를 선택해 비교 가능한 동료군 안에서 기업을 필터링·내림차순 정렬하려면 어떤 입력·동료군·결과 계약을 채택할 것인가? | B-peer-scoped-evidence-screener | D-02-company-capability-taxonomy | ACCEPT |
| 7 | company-timeline-macro-comparison | accepted | 한 기업의 재무·인력·채용공고·시장가격 변화를 국가·산업 거시 변수와 같은 시간축에서 어떤 시점 규칙으로 비교할 것인가? | B-point-in-time-multiaxis-comparison | D-02-company-capability-taxonomy | ACCEPT |
| 8 | future-value-scenarios | accepted | 사용자가 선택한 기업의 미래가치를 단일 예측값이 아닌 어떤 재무 근거·가정·낙관/기준/침체 시나리오·데이터 신뢰도와 함께 반환할 것인가? | B-evidence-bound-scenarios | D-06-peer-screener-ranking<br>D-07-company-timeline-macro-comparison | ACCEPT |
| 9 | ai-event-effect-validation | accepted | 특정 AI 모델의 보급·기업 도입 이후 채용공고·직원 수·수익성·시장 반응 변화를 어떤 사건 근거·대조군·거시 통제로 검증하되 인과로 과장하지 않을 것인가? | B-evidence-bound-candidate-analysis | D-07-company-timeline-macro-comparison | ACCEPT |
| 10 | job-availability-filtered-discovery | accepted | 사용자가 실제 공개 채용공고를 국가·산업·직무·근무형태·언어·검증된 required/preferred 요건으로 필터링해 기업과 공고를 함께 확인하려면 어떤 검색 계약을 완성할 것인가? | B-evidence-filtered-job-discovery | D-03-search-profile-and-discovery<br>D-04-career-requirement-verification | ACCEPT |

## 의사결정 상세

## 1. 무료·공개 API 접근 정책 (`D-01-source-access-policy`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 미국·한국·EU/체코 원천을 어떤 접근·권한·데이터 역할 기준으로 등록하고, 어떤 상태에서만 connector를 활성화할 것인가? |
| 누가 | 플랫폼 운영자와 데이터 연구자 |
| 무엇을 | 무료·공개 원천의 접근 상태, 데이터 역할, 쿼터·약관, 확인일을 보존하는 source catalog |
| 어디서 | config/providers.json, connector registry, 이후의 provider adapter |
| 언제 | 새 원천을 추가하거나 정기 수집을 실행하기 전과 공식 약관 변경 확인 시 |
| 왜 | 표본 endpoint 성공을 기업 전체 커버리지·재배포 권한·분석 적격성으로 오해하지 않기 위해 |
| 어떻게 | KEYLESS_PUBLIC·FREE_REGISTERED·APPROVAL_REQUIRED·DOCUMENT_ONLY·AGGREGATE_ONLY·EXTRACTION_RESTRICTED와 last_verified를 source별로 기록하고 승인된 상태만 실행한다. |
| 근거 | E-D01-source-verification — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:7-68 — 공식 문서 확인 결과, SEC·OpenDART·ARES·MPSV 등은 서로 다른 접근·데이터 역할을 가지며 EURES 원시 공고는 일반 자동 추출 대상으로 제외해야 한다.<br>E-D01-repo-provider-config — config/providers.json:1-20 — 현재 저장소 설정은 10개 keyed provider record와 17개 keyless provider 이름을 보존하고, connector registry가 이를 28개 원자 Probe로 확장한다.<br>E-D01-readme-limits — README.md:1-43 — README는 10개 키 기반 작업군과 18개 무키 Probe 범위, ALIO Plus HTTP 제약, MPM 권한, Alpha Vantage 한계를 명시한다. |
| 관찰 사실 | 현재 실행 인벤토리는 28개 원자 API 작업이며, 18개는 키 없이 호출하고 10개는 무료 등록 키를 사용한다.<br>2026-09-11 실제 재검증에서 키 없는 18개 작업은 모두 HTTP 200과 required_paths를 통과했고, ALIO Plus 4개와 인사혁신처 공공취업정보 목록도 각 키로 필수 필드를 통과했다.<br>ALIO Plus 시설·행사·사업·기관은 공공기관 맥락 정보이지 채용공고나 고용 완료 정보가 아니며, 공식 가이드 v1.6의 HTTP form 제약을 가진다.<br>인사혁신처 공공취업정보 목록은 idx·기관명·제목·유형·등록일·마감일을 제공하지만 현재 프로브만으로 자격증·학력·기술 상세를 증명하지 못한다.<br>SEC_USER_AGENT는 유료 sec-api.io 키가 아니라 공식 SEC 호출 식별 헤더이고, DATABASE_URL은 현재 외부 공급자가 아닌 로컬 DuckDB 경로다.<br>현재 registry는 keyed_probes와 keyless_probes를 결합하지만 원자 작업별 접근 상태·역할·필드 계약·운영 활성화 정책을 검사하지 않는다. |
| 충돌 | HTTP 200과 표본 required_paths 통과는 현재 endpoint 접근성과 최소 필드 계약만 증명하며 전체 기업 커버리지·장기 무료 쿼터·재배포 권한을 보장하지 않는다.<br>검증용 고정 표본 Probe와 사용자가 지정한 기업을 탐색하는 production adapter는 역할이 다르므로 동일한 활성화 상태로 취급하면 안 된다.<br>ALIO Plus의 평문 HTTP 제약은 비밀키와 개인정보 검색어를 일반 네트워크에서 전송하지 않도록 별도 실행 경계를 요구한다. |
| 미구현 | 28개 원자 작업별 access_mode, data_role, required_paths, field_semantics, quota strategy, license_attribution_status, last_verified를 가진 versioned source catalog가 없다.<br>connector 실행 전에 등록·승인·추출 제한·평문 전송·비밀 존재 여부를 판정하는 policy gate가 없다.<br>표본 probe와 범용 기업·공고 discovery adapter를 분리하고 운영 상태·staleness·부분 장애를 기록하는 provider health 계약이 없다.<br>MPM 상세 공고·미국 기업별 공고·체코 MPSV/NSP 같은 후속 원천을 현재 28개 작업과 구분해 검토·등록하는 onboarding 절차가 없다. |
| 선택지 | A-probe-success-enables: 기존처럼 endpoint 응답과 필수 필드 통과를 주된 채택 기준으로 사용한다.; B-versioned-source-catalog: 공식 문서 근거를 가진 versioned source catalog와 실행 전 policy gate를 도입하고, 승인된 접근 상태만 connector를 활성화한다. |
| 권장안 | B-versioned-source-catalog |
| 권장 근거 | 원천 접근권·데이터 역할·추출 제한·확인일을 분리해야 무료 endpoint라는 표현을 실제 운영 가능성으로 오해하지 않고, 국가별 기업 분류와 이후 스프레드시트 근거를 재현할 수 있다. |
| 파급효과 | 데이터: 원천별 접근 상태·데이터 역할·확인일을 보존해 재무·고용·공고·거시 데이터를 섞지 않는다.<br>스키마/API: Source catalog와 connector policy gate를 도입하고 기존 Probe를 catalog ID에 연결한다.<br>사용자 경험: 기업 결과에 원천별 지원 범위와 제한 사유를 표시할 기반이 생긴다.<br>성능: 캐시·직렬 호출·quota backoff를 원천 정책으로 제어한다.<br>비용: 무료 등록·승인 절차와 유지보수 비용은 명시되지만 무효 호출을 줄인다.<br>보안: 키·승인 필요 원천을 실행 전에 차단하고 로그·출력에서 비밀을 제외한다.<br>마이그레이션: 기존 28개 Probe ID를 보존하면서 source catalog record와 일대일 연결하고, Work24 및 sec-api.io 이름은 실행 네임스페이스에 다시 도입하지 않는다.<br>테스트: catalog schema·현재성·connector activation 경계를 단위 테스트한다. |
| 기회비용 | 등록·승인·약관 확인을 생략하는 빠른 connector 추가는 허용하지 않는다.<br>최신 공식 문서가 없는 원천은 실행 대상이 아니라 조사 후보로만 남긴다. |
| 선행 결정 | — |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-versioned-source-catalog<br>규칙: 사용자가 2026-09-11 요청에서 APPROVE로 5개 권장안 B를 결속하라고 명시했다.<br>근거: 무료·공개 API도 접근 상태·데이터 역할·필드 의미·쿼터·제한을 versioned source catalog로 관리한다.<br>결정자: user<br>결정 시각: 2026-09-11T06:25:49.898Z |
| 구현 대상 | config/providers.json — 28개 원자 작업별 access_mode·data_role·required_paths·field_semantics·quota·license·last_verified·activation_policy 계약 추가<br>src/company_intel/models.py — source policy, atomic field contract, provider health 모델 추가<br>src/company_intel/source_catalog.py (new) — catalog 로드·검증·실행 가능 상태·staleness 판정<br>src/company_intel/connectors/registry.py — catalog 승인 상태와 probe/production 용도에 따라 adapter 선택<br>src/company_intel/validation.py — 접근성·필드 계약·provider error를 분리한 상태와 redacted receipt 생성<br>tests/test_source_catalog.py (new) — 28개 작업 완전성, activation gate, HTTP-only 경계, 비밀 마스킹 검증 |
| 구현 변경 ID | D-01-field-capability-catalog-r3<br>D-01-nested-field-resolution-r3 |
| 검증 기준 | 코드의 28개 Probe ID와 source catalog record가 누락·중복 없이 일대일 대응하는지 검증한다.<br>KEYLESS_PUBLIC 18개와 FREE_REGISTERED 10개가 서로 다른 인증·쿼터 정책으로 실행되는지 검증한다.<br>APPROVAL_REQUIRED·EXTRACTION_RESTRICTED·DOCUMENT_ONLY 또는 stale 원천이 명시적 허용 없이 production discovery에 들어가지 않는지 검증한다.<br>ALIO Plus 평문 HTTP 작업이 신뢰 실행 경계 밖에서 차단되고 비밀·개인정보가 URL·로그·보고서에 남지 않는지 검증한다.<br>Work24와 sec-api.io가 실행 코드·설정에 없고 SEC_USER_AGENT와 로컬 DuckDB 의미가 잘못 변환되지 않았는지 검증한다. |
| 다이어그램 영향 | 원천 문서 검증 → source catalog → connector policy gate → 수집/분류/스프레드시트 흐름을 후속 다이어그램에 반영한다. |
| 구현 맥락 topic | source-identity-capability |

## 2. 기업별 데이터 가용성·분석 적격성 분류 (`D-02-company-capability-taxonomy`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업별 재무·고용·채용·시장·거시 연결과 상관·인과 분석 가능 여부를 어떤 다축 taxonomy와 증거 기준으로 분류할 것인가? |
| 누가 | 플랫폼 사용자, 데이터 연구자, 분석 API 소비자 |
| 무엇을 | 기업별 source capability와 analysis eligibility를 분리하는 다축 분류 계약 |
| 어디서 | entity·financial_fact·workforce_fact·job_posting_snapshot·market_price·macro_observation과 분석 진입점 |
| 언제 | 기업을 검색·수집·스프레드시트에 내보내기 전과 분석 실행 직전 |
| 왜 | 재무 전용·고용 전용·공고 전용·시장 제한·상관분석 불가 기업을 같은 점수나 결론으로 표현하지 않기 위해 |
| 어떻게 | 식별자 해소, 원천별 관측 범위, 기간·빈도, 산업·지역 매핑, point-in-time 가용성, 라이선스 상태를 각각 기록하고 조합 규칙으로 eligibility를 계산한다. |
| 근거 | E-D02-existing-schema — sql/duckdb_schema.sql:4-180 — 현재 스키마에는 entity·financial_fact·workforce_fact·job_posting_snapshot·market_price·macro_observation·evidence가 있으나 기업별 capability 또는 분석 적격성 테이블은 없다.<br>E-D02-sample-ingestion — src/company_intel/warehouse.py:85-262 — 정규화 적재는 삼성전자·Airtable·Spotify·IBM 등 하드코드된 예시 법인과 probe 파일명을 기준으로 동작한다.<br>E-D02-protection-rules — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:44-68 — 공식 원천 근거는 공고와 실제 채용을 분리하고, 문서형 재무·분석 적격성·직업 자격 baseline을 별도 축으로 기록하도록 요구한다. |
| 관찰 사실 | 현재 28개 원자 API 작업은 법인 식별·재무·공고·공공기관 맥락·조달·거시·시장·활동 대리 신호로 역할이 다르다.<br>공통 호환 계약은 source_name, source_record_id, entity_external_id, subject_type, country_code, observation_date, available_at, collected_at, source_url, classification_reason을 서로 다른 의미로 보존해야 한다.<br>기존 스키마에는 entity·financial_fact·workforce_fact·job_posting_snapshot·market_price·macro_observation이 있지만 기업별 source capability·field availability·analysis eligibility 이력이 없다.<br>현재 정규화 적재는 삼성전자·Airtable·Spotify·IBM 표본에 결합되어 일반 기업 universe와 identifier resolution을 제공하지 않는다.<br>공고 수는 채용 완료 인원이나 직원 수가 아니고 거시·조달·GitHub·OpenAlex 신호는 기업 재무 fact가 아니다. |
| 충돌 | workforce_fact 테이블이 존재해도 공개 원천에 기업별 직원 수가 있다는 뜻은 아니다.<br>공고에 있는 기업 정보는 공고 제공 값이므로 감사 재무 또는 실제 인력 증감과 같은 신뢰도로 취급할 수 없다.<br>문서가 공개된 체코 법인이라도 구조화·검증된 재무 line item이 있다고 가정할 수 없다. |
| 미구현 | company_source_capability, identifier_mapping, field_availability, classification_history와 evidence foreign key가 없다.<br>CIK·DART corp_code·IČO·LEI·ISIN·ALIO apbaId·ATS employer ID를 네임스페이스별로 해소하고 confidence를 기록하는 resolver가 없다.<br>원천별 필드를 공통 10개 provenance 속성으로 정규화하면서 원천 ID·단위·시간 의미를 보존하는 mapper와 중복 제거 키가 없다.<br>financial_only·workforce_only·job_only·public_context_only·market_limited·correlation_ineligible·causal_analysis_ineligible 판정 함수가 없다.<br>분석 endpoint가 identifier·기간·빈도·산업/지역·available_at 조건을 검사해 부적격 회귀·이벤트 스터디를 막지 않는다. |
| 선택지 | A-single-availability-score: 기업마다 단일 data_available 또는 coverage score를 계산하고 누락 항목은 점수 감소로만 표현한다.; B-multiaxis-capability-and-gates: 기업 식별·재무·고용·공고·시장·거시·직무요건의 capability와 source evidence를 독립 저장하고, 명시적 규칙으로 correlation·causal eligibility를 계산한다. |
| 권장안 | B-multiaxis-capability-and-gates |
| 권장 근거 | 사용자가 요청한 재무 전용·고용 전용·채용 전용·경제변수 상관분석 불가 분류는 하나의 score가 아니라 source별 사실과 규칙 기반 eligibility를 동시에 보존해야 정확하게 표현된다. |
| 파급효과 | 데이터: 기업별 coverage·기간·원천·신뢰도·제한 사유를 독립 보존한다.<br>스키마/API: capability history와 identifier mapping, classification API·export 필드를 추가한다.<br>사용자 경험: 사용자는 가능한 분석과 불가능한 분석을 혼동하지 않고 후보를 필터할 수 있다.<br>성능: 분석 전에 eligibility를 계산해 무의미한 고비용 실행을 차단한다.<br>비용: 초기 스키마와 fixture 구축 비용이 있지만 사후 해석 오류를 줄인다.<br>보안: 접근·라이선스 상태를 정책 계층에서 통제하고 개인·비밀 데이터를 capability에 넣지 않는다.<br>마이그레이션: 기존 entity·관측 테이블을 파괴하지 않는 additive migration으로 진행한다.<br>테스트: 국가·원천·누락 조건별 분류와 analysis gate 검증을 추가한다. |
| 기회비용 | 충분한 증거가 없는 기업은 단일 순위 또는 회귀 결과에서 제외되며, 이는 데이터 공백을 숨기는 것보다 우선한다.<br>법인 해소가 안 된 공고는 익명 수요 집계로만 보존하고 회사 분석 후보에 넣지 않는다. |
| 선행 결정 | D-01-source-access-policy |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-multiaxis-capability-and-gates<br>규칙: 사용자가 2026-09-11 요청에서 APPROVE로 5개 권장안 B를 결속하라고 명시했다.<br>근거: 기업별 재무·공고·고용·시장·거시 capability를 분리하고 근거가 부족한 상관·인과 분석을 gate로 차단한다.<br>결정자: user<br>결정 시각: 2026-09-11T06:25:49.898Z |
| 구현 대상 | sql/duckdb_schema.sql — company_source_capability, identifier_mapping, field_availability, classification_history 및 evidence 연결을 additive하게 추가<br>src/company_intel/models.py — capability·classification·eligibility·provenance value object 정의<br>src/company_intel/identity.py (new) — CIK·DART·IČO·LEI·ISIN·ALIO·ATS 식별자 해소와 confidence 기록<br>src/company_intel/normalization.py (new) — 원자 필드 의미·단위·시간·중복 제거 키를 보존하는 mapper<br>src/company_intel/classification.py (new) — 기업 분류와 correlation·causal eligibility 규칙<br>src/company_intel/warehouse.py — 범용 entity·capability 적재와 예시 하드코딩 분리<br>src/company_intel/api.py — 분류·필드 가용성·제외 사유 조회 endpoint<br>tests/test_classification.py (new) — 재무 전용·공고 전용·공공기관 맥락·문서형·상관 불가 fixture 검증 |
| 구현 변경 ID | D-01-field-capability-catalog-r3<br>D-01-nested-field-resolution-r3<br>D-02-classification-tests-r3<br>D-02-facet-catalog-r3<br>D-02-facet-tests-r3<br>D-02-taxonomy-classification-r3<br>D-02-taxonomy-model-r3<br>D-02-taxonomy-module-r3<br>D-02-taxonomy-tests-r3 |
| 검증 기준 | 동일 원천 레코드 재수집이 source_name·source_record_id·observation_date 기준으로 중복되지 않고 revision/collected 시각만 올바르게 보존되는지 검증한다.<br>재무만 있는 기업은 company_financial_disclosure과 correlation_ineligible을 동시에 가질 수 있는지 fixture로 검증한다.<br>공고만 있고 법인 ID가 없는 레코드는 identity_unresolved 또는 employer_redacted이며 회사 분석 후보에서 제외되는지 검증한다.<br>공공기관 시설·행사·사업·기관 데이터가 job_available이나 workforce_available로 승격되지 않는지 검증한다.<br>기간·단위·산업/지역·point-in-time 중 하나라도 없으면 correlation_candidate가 false인지 검증한다.<br>causal analysis가 correlation candidate보다 더 엄격한 대조군·pre-trend·표본 기준을 요구하는지 검증한다. |
| 다이어그램 영향 | 법인 식별 해소 → source capability history → classification → correlation/causal gate → 분석·스프레드시트 흐름을 후속 다이어그램에 반영한다. |
| 구현 맥락 topic | source-identity-capability |

## 3. 사용자 목적 기반 기업 검색 프로필과 발견 절차 (`D-03-search-profile-and-discovery`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 사용자 목적에 맞는 기업을 재현 가능하게 찾기 위해 어떤 검색 프로필·후보 발견·적합성 설명 계약을 사용할 것인가? |
| 누가 | 취업·연구 목적을 가진 사용자와 플랫폼 검색 서비스 |
| 무엇을 | 국가·직무·산업·경력·언어·취업 자격·지역·후보 수를 명시하는 SearchProfile과 후보 발견 규칙 |
| 어디서 | CLI·FastAPI 입력, company identifier resolver, source catalog, 스프레드시트 결과 |
| 언제 | 실제 기업 검색을 시작하기 전과 검색 결과를 갱신할 때 |
| 왜 | 희망 직무·산업·경력·언어·취업 자격이 없는 상태에서 적합한 기업이나 자격증을 추정하지 않기 위해 |
| 어떻게 | 국가별 후보 배분, 현지 직무명↔직업 코드 매핑 기준, 자격요건 증거 범위를 포함한 profile을 검증하고, 허용된 원천에서 후보를 발견한 뒤 matching rule·evidence·제외 사유·confidence를 결과와 함께 보존한다. |
| 근거 | E-D03-mvp-purpose-and-limits — README.md:1-43 — 현재 프로젝트는 다국가 기업 분석 MVP이며 비밀 보호와 point-in-time 원칙은 있으나 사용자별 기업 검색 프로필은 정의하지 않는다.<br>E-D03-hardcoded-entities — src/company_intel/warehouse.py:85-114 — 현재 정규화 적재는 삼성전자, Airtable, Spotify, IBM을 하드코드한다.<br>E-D03-country-source-boundaries — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:20-60 — 미국·한국·체코 원천은 재무·공고 메타데이터·공공기관 맥락·직업 기준 후보·집계 데이터의 범위와 현재 구현 상태가 서로 다르다. |
| 관찰 사실 | 사용자는 미국·한국·체코를 대상으로 무료 원천 기반 기업·고용·자격요건 검색을 요구했지만 희망 직무·산업·경력·언어·취업 자격·도시·원격 여부·국가별 후보 수는 실행 입력으로 아직 확정되지 않았다.<br>현재 28개 Probe는 공급자 연결 검증을 위한 고정 표본이며 일반 기업 universe나 사용자별 후보 탐색기가 아니다.<br>미국 기업별 공고는 현재 Greenhouse Airtable과 Lever Spotify 보드 표본에 한정되고, 한국 공공취업정보는 기관 공고 목록이며, 체코 기업별 공고 adapter는 현재 실행 인벤토리에 없다.<br>기업 데이터가 풍부하다는 사실과 사용자의 직무·언어·취업 자격에 맞는 고용주라는 판단은 서로 다른 근거를 요구한다.<br>후보가 없거나 회사 식별이 해소되지 않으면 임의 기업을 채우지 않고 exclusion과 missing_profile을 반환해야 한다. |
| 충돌 | 사용자 목적에 맞는 기업의 의미는 직무·산업·경력·언어·취업 자격·근무지에 따라 달라지지만 현재 입력에는 그 선택 기준이 없다.<br>데이터가 풍부한 상장사와 사용자에게 실제로 적합한 고용주가 항상 같지 않다.<br>국가별 공고와 직업 분류를 crosswalk할 수 있어도 개인의 자격 동등성·취업 가능성을 자동 판정할 수 없다. |
| 미구현 | SearchProfile, 국가별 후보 배분, profile validation, CandidateMatch, ExclusionReason, matching rule version 모델이 없다.<br>공급자 검증용 고정 표본과 사용자 조건으로 회사·공고를 탐색하는 source-aware discovery service가 분리되어 있지 않다.<br>기업 universe를 source catalog·identifier resolver·capability taxonomy·country policy로 구성하는 절차가 없다.<br>익명 공고·허용되지 않은 원천·만료 공고·매칭 불확실성을 후보 결과에서 제외하거나 표시하는 규칙이 없다.<br>CLI와 API에 profile 입력·재실행 기준일·결과 provenance·국가별 부족분을 반환하는 계약이 없다. |
| 선택지 | A-implicit-keyword-ranking: 직무명이나 회사명을 느슨한 키워드로 해석해 기존 예시 및 발견된 결과를 단일 적합도 순위로 반환한다.; B-explicit-profile-and-evidence-matching: 필수 SearchProfile을 검증하고, 허용된 country/source 후보만 발견한 뒤 matching rule·근거·신뢰도·제외 사유를 보이는 설명 가능한 결과를 만든다. |
| 권장안 | B-explicit-profile-and-evidence-matching |
| 권장 근거 | 정확한 기업·자격요건 반환은 사용자의 목적과 국가별 원천 제한을 동시에 알아야 하므로, 누락된 개인 조건을 추정하는 대신 명시적 profile과 근거·제외 사유를 보존하는 방식이 필요하다. |
| 파급효과 | 데이터: 사용자 입력과 후보 원천·매칭 근거·제외 사유를 분리해 보존한다.<br>스키마/API: SearchProfile·CandidateMatch·ExclusionReason과 CLI/API 요청 계약을 추가한다.<br>사용자 경험: 사용자는 왜 후보가 선택·제외됐는지와 추가로 필요한 입력을 확인한다.<br>성능: 프로필 필터를 provider 호출 전 적용해 수집 범위를 제어한다.<br>비용: 프로필 검증과 match rule 유지보수 비용이 생긴다.<br>보안: 취업 자격·언어 등 민감 입력은 최소화하고 명시적 동의 없이 추정·공유하지 않는다.<br>마이그레이션: 하드코드 예시 기업은 fixture로 남기되 검색 서비스와 분리한다.<br>테스트: 누락 profile, 국가별 source 제한, confidence, exclusion reason을 테스트한다. |
| 기회비용 | 사용자 프로필이 없으면 실제 회사 후보와 자격증 목록은 생성하지 않고 준비 상태로 남긴다.<br>검색 결과가 비어 있어도 이를 데이터·원천 제한의 명시적 결과로 반환한다. |
| 선행 결정 | D-02-company-capability-taxonomy |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-explicit-profile-and-evidence-matching<br>규칙: 사용자가 2026-09-11 요청에서 APPROVE로 5개 권장안 B를 결속하라고 명시했다.<br>근거: 명시적 SearchProfile과 source evidence를 사용하고 고정 Probe 표본이나 미해소 기업을 자동 추천하지 않는다.<br>결정자: user<br>결정 시각: 2026-09-11T06:25:49.898Z |
| 구현 대상 | src/company_intel/models.py — SearchProfile, CountryAllocation, CandidateMatch, ExclusionReason 모델 추가<br>src/company_intel/search.py (new) — profile validation, source-aware company universe, capability filter, 설명 가능한 후보 순위<br>src/company_intel/identity.py (new) — 후보 entity와 source identifier 연결<br>src/company_intel/connectors/ — 검증용 sample probe와 허용된 company/job discovery adapter 분리<br>src/company_intel/cli.py — 검색 profile 입력·검증·실행 명령<br>src/company_intel/api.py — profile 기반 후보 조회, missing profile, provenance 응답<br>tests/test_search_profile.py (new) — 필수 프로필·국가별 부족분·익명 공고·제외 사유·결정론적 순위 검증 |
| 구현 변경 ID | D-03-company-search-contract-r3<br>D-03-company-search-engine-r3<br>D-03-query-contract-tests-r3<br>D-03-search-profile-tests-r3 |
| 검증 기준 | 국가·직무·산업·경력·언어·취업 자격·지역·원격 여부·후보 수·기준일 중 계약상 필수 항목이 빠지면 후보 생성 대신 구조화된 missing_profile을 반환하는지 검증한다.<br>고정 sample probe의 회사가 사용자 조건 없이 실제 추천 후보로 자동 승격되지 않는지 검증한다.<br>허용되지 않은 source, 만료 공고 또는 identity_unresolved 레코드가 회사 후보에 들어가지 않는지 검증한다.<br>각 후보에 matching rule version·source evidence·company_match_confidence·capability summary 또는 제외 사유가 있는지 검증한다.<br>국가별 데이터 부족으로 요청 개수를 채우지 못할 때 다른 국가나 임의 기업으로 보충하지 않고 shortage를 반환하는지 검증한다. |
| 다이어그램 영향 | SearchProfile 입력 → source-aware candidate discovery → identity resolution → capability filter → 설명 가능한 후보·제외 결과 흐름을 후속 다이어그램에 반영한다. |
| 구현 맥락 topic | search-career-evidence |

## 4. 채용 자격증·준비사항 원문 검증 계약 (`D-04-career-requirement-verification`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업별 채용공고의 자격증·학력·경력·언어·기술·준비사항을 어떤 원문·국가 기준·검증 상태로 구조화해 정확하게 반환할 것인가? |
| 누가 | 구직자, 연구자, 채용 요건 수집·검증 서비스 |
| 무엇을 | 공고별 requirement와 credential evidence를 required·preferred·unknown 및 vacancy_specific·national_baseline·crosswalk_only로 분리하는 증거 계약 |
| 어디서 | job posting adapter, qualification source adapter, warehouse, API, spreadsheet exporter |
| 언제 | 공고를 수집·갱신할 때와 스프레드시트 반환 전 |
| 왜 | 공고 우대사항을 법정 자격으로 바꾸거나 직무명만으로 자격증을 추정하지 않기 위해 |
| 어떻게 | 각 요건에 source URL·source record ID·원문 문구 또는 구조화 필드·확인일·국가·직업 코드·parse status·confidence를 저장하고, 검증 불가 항목은 unresolved로 남긴다. |
| 근거 | E-D04-job-schema-gap — sql/duckdb_schema.sql:117-135 — 현재 job_posting_snapshot에는 공고 식별자·직무·위치·날짜·description_hash가 있지만 자격증·학력·경력·언어·기술의 개별 원문과 검증 상태를 저장하는 테이블은 없다.<br>E-D04-official-requirement-sources — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:27-60 — 현재 한국 실행 원천은 ALIO Plus 공공기관 맥락과 MPM 공고 목록이며, 체코 MPSV/NSP/NSK는 구현 전 필드·약관 검증이 필요한 후보 원천이다.<br>E-D04-protection-rules — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:53-68 — 공고는 실제 채용의 증거가 아니며, 자격은 vacancy_specific·national_baseline·crosswalk_only로 분리하고 국가 간 동등성을 직업 코드만으로 확정하면 안 된다. |
| 관찰 사실 | 현재 인사혁신처 공공취업정보 목록은 idx·기관명·제목·공고 유형·등록일·마감일을 검증했지만 자격증·학력·경력·언어·기술 상세 필드를 제공한다는 증거는 아직 없다.<br>Greenhouse와 Lever는 표본 공고를 반환하지만 현재 normalizer는 제목·위치·부서·시각 중심이며 자격요건 원문을 구조화해 보존하지 않는다.<br>ALIO Plus 시설·행사·사업·기관은 공공기관 맥락 원천이며 채용 자격요건 원천으로 사용할 수 없다.<br>체코 MPSV/NSP/NSK는 조사된 후보 원천이지만 현재 28개 실행 Probe와 production adapter에 포함되지 않았으므로 구현 전 source policy와 실제 필드 검증이 필요하다.<br>미국·한국·체코 어느 국가에서도 공고 원문이나 공식 국가 기준이 없으면 직무명만으로 자격증을 추천할 수 없다. |
| 충돌 | 고용주 공고의 required·preferred 표현과 국가 법정 자격·직업 baseline은 서로 다른 증거 범위와 유효기간을 가진다.<br>목록 API의 제목·유형 필드는 상세 자격요건의 존재를 증명하지 않으며, 공고 상세 endpoint 또는 허용된 원문 없이는 requirement_unavailable이어야 한다.<br>직업 코드 crosswalk는 기술·직무 비교를 돕지만 자격증의 국가 간 동등성을 보증하지 않는다.<br>공고가 삭제·마감·수정될 수 있으므로 snapshot과 source hash 없이 한 번의 수집 결과를 지속 요건으로 취급하면 안 된다.<br>원시 공고 자동 추출·재배포가 제한된 원천은 production ingestion에 사용할 수 없다. |
| 미구현 | job_requirement, credential_evidence, requirement_verification, source excerpt 또는 structured source field 모델이 없다.<br>MPM 공고 상세, 허용된 ATS description, 체코 MPSV/NSP/NSK를 실제 필드 계약과 source policy로 검증하는 adapter가 없다.<br>공고별 required·preferred·unknown과 vacancy_specific·national_baseline·crosswalk_only·requirement_unavailable을 결정하는 parser·review 상태가 없다.<br>공고 원문·국가 자격 원천·직업 코드·확인일을 연결하는 provenance API와 export가 없다.<br>원천 부재나 상세 필드 부재를 자동 추천 대신 제한으로 반환하는 country/source policy가 없다. |
| 선택지 | A-flattened-recommendation-text: 공고 제목·설명에서 키워드를 모아 기업마다 하나의 추천 자격증·준비사항 텍스트를 만든다.; B-evidence-level-requirements: 공고별·국가 기준별 requirement와 credential evidence를 개별 행으로 저장하고 상태·원문 근거·확인일·국가·직업 코드·parse/review 상태를 보존한다. |
| 권장안 | B-evidence-level-requirements |
| 권장 근거 | 사용자가 원하는 정확한 자격증·준비사항은 요약 추천이 아니라 공고별 또는 공식 국가 기준별 근거, 상태, 확인일, 제한 사유를 추적해야 하며, 미국처럼 원천이 없는 경우에는 미확인으로 정직하게 표시해야 한다. |
| 파급효과 | 데이터: 요건·자격 근거·확인 상태·원천과 공고 snapshot을 분리해 보존한다.<br>스키마/API: requirement·credential evidence·verification API와 country policy가 추가된다.<br>사용자 경험: 사용자는 필수·우대·국가 baseline·crosswalk·미확인을 구분한 준비 목록을 받는다.<br>성능: 증분 공고와 source hash 기반으로 변경된 요건만 재검증한다.<br>비용: 구조화 parser와 review 흐름 비용이 증가하지만 부정확한 추천을 줄인다.<br>보안: 원천 출처 표기와 추출 제한을 보존하고 자격증 원본·개인정보는 수집하지 않는다.<br>마이그레이션: 기존 job snapshot과 호환되는 additive schema로 도입한다.<br>테스트: 원문 근거·상태·국가·직업 코드·확인일이 없는 결과를 실패시키는 테스트를 추가한다. |
| 기회비용 | 원천이 없거나 약관상 자동 추출할 수 없는 국가·기업에는 자격증 목록을 만들어 내지 않는다.<br>사람의 이력서·자격증 파일은 이 기능의 입력이 아니며, profile 조건과 공개 원천만 사용한다. |
| 선행 결정 | D-03-search-profile-and-discovery |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-evidence-level-requirements<br>규칙: 사용자가 2026-09-11 요청에서 APPROVE로 5개 권장안 B를 결속하라고 명시했다.<br>근거: 공고별·국가 기준별 requirement evidence를 분리하고 상세 근거가 없으면 requirement_unavailable로 남긴다.<br>결정자: user<br>결정 시각: 2026-09-11T06:25:49.898Z |
| 구현 대상 | sql/duckdb_schema.sql — job_requirement, credential_evidence, requirement_verification, source excerpt/provenance 테이블을 additive하게 추가<br>src/company_intel/models.py — RequirementStatus, EvidenceScope, VerificationStatus, RequirementAvailability 모델 추가<br>src/company_intel/career_requirements.py (new) — 공고·국가 baseline·crosswalk 정규화와 unresolved 처리<br>src/company_intel/connectors/ — MPM 상세·허용된 ATS 원문·체코 MPSV/NSP/NSK adapter를 source policy와 연결<br>src/company_intel/warehouse.py — 공고 snapshot과 requirement evidence 적재·증분 갱신<br>src/company_intel/api.py — 기업·공고별 검증된 준비사항과 제한 사유 조회<br>tests/test_career_requirements.py (new) — required/preferred·상세 필드 부재·국가 기준·원천 제한·stale 공고 검증 |
| 구현 변경 ID | D-03-company-search-engine-r3 |
| 검증 기준 | 모든 반환 requirement에 source_url, source_record_id, retrieved_at, country_code, evidence_scope, verification_status가 있는지 검증한다.<br>MPM 목록이나 ATS 메타데이터만 있고 상세 근거가 없으면 자격증을 생성하지 않고 requirement_unavailable을 반환하는지 검증한다.<br>공고 우대사항이 required 또는 법정 자격으로 승격되지 않는지 검증한다.<br>ESCO/ISCO crosswalk만 있는 항목이 credential equivalence나 vacancy_specific으로 표시되지 않는지 검증한다.<br>허가된 회사별 요건 원천이 없으면 no_primary_requirement_source 제한을 반환하는지 검증한다.<br>마감·삭제·익명 공고가 회사별 자격요건 결과에 잘못 남지 않는지 검증한다. |
| 다이어그램 영향 | 공고 또는 국가 기준 원천 → requirement extraction → verification status → 자격·준비사항 스프레드시트 행 흐름을 후속 다이어그램에 반영한다. |
| 구현 맥락 topic | search-career-evidence |

## 5. 스프레드시트 반환 계약과 운영 경계 (`D-05-spreadsheet-output-contract`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 기업·가용성·채용공고·자격요건·원천 근거·제외 사유를 어떤 스프레드시트 계약으로 반환해 사용자가 직접 검토하고 재현할 수 있게 할 것인가? |
| 누가 | 기업·직무 후보를 검토하는 사용자와 결과를 생성하는 플랫폼 |
| 무엇을 | 다중 시트 또는 정규화된 CSV bundle의 evidence-first spreadsheet export 계약 |
| 어디서 | warehouse query, reporting/export module, CLI/API download 경계 |
| 언제 | profile 기반 검색·분류·요건 검증 후 사용자에게 결과를 반환할 때 |
| 왜 | 한 줄 요약만으로는 재무 전용·공고 전용·미확인 자격증·원천 제한과 시간 기준을 검토할 수 없기 때문에 |
| 어떻게 | companies, capabilities, job_postings, requirements, sources, exclusions, run_manifest를 외래키·원천 URL·확인일·분류 사유와 함께 결정론적으로 생성한다. |
| 근거 | E-D05-current-reporting — src/company_intel/reporting.py:1-67 — 현재 reporting 모듈은 API probe 결과의 한국어 Markdown 표를 만들며 기업 후보·요건·근거 스프레드시트 export는 제공하지 않는다.<br>E-D05-time-and-provenance-rules — docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/source-verification-2026-09-11.md:53-68 — 보호 규칙은 source_name, source_record_id, source_url, retrieved_at, license_attribution_status, company_match_confidence, classification_reason을 모든 스프레드시트 행에 보존하도록 요구한다.<br>E-D05-readme-artifact-policy — README.md:1-43 — 현재 프로젝트는 비밀 마스킹, raw/normalized/log artifact, period_end·available_at·collected_at·revision_at 분리를 원칙으로 한다. |
| 관찰 사실 | 현재 플랫폼은 provider validation JSON과 한국어 Markdown 보고서를 생성하지만 사용자 SearchProfile에 따른 기업·공고·자격요건 CSV/XLSX를 생성하지 않는다.<br>기업, source capability, 채용공고, 자격요건, 원자 API 필드, 제외 사유는 다대다 관계이므로 한 기업 한 행으로 병합하면 근거와 시간 의미가 손실된다.<br>모든 사용자 결과는 source_name, source_record_id, source_url, retrieved_at, license_attribution_status, company_match_confidence, classification_reason으로 추적 가능해야 한다.<br>profile·source policy·identity·capability·requirement evidence가 부족하면 빈 추천을 성공처럼 내보내지 않고 exclusions와 run_manifest에 부족 사유를 기록해야 한다.<br>CSV bundle을 기준 계약으로 두고 XLSX는 동일 row key·header version을 렌더링해야 라이브러리 변경과 데이터 계약을 분리할 수 있다. |
| 충돌 | 한 장의 요약은 사용하기 쉽지만 같은 기업의 여러 원천·여러 공고·여러 요건·서로 다른 확인일을 정확히 표현할 수 없다.<br>XLSX는 사용성이 높지만 추가 라이브러리·스타일·수식이 필요하며 CSV만으로는 다중 시트·연결을 표현할 수 없다.<br>스프레드시트가 결과물이어도 원천 약관상 재배포가 제한된 원문 전체나 비밀·개인정보를 포함하면 안 된다. |
| 미구현 | export schema version, sheet/header 계약, CSV bundle renderer, XLSX renderer, run manifest, source attribution formatter가 없다.<br>companies·capabilities·job_postings·requirements·sources·exclusions·run_manifest 간 foreign key와 orphan 검증이 없다.<br>provider_status와 atomic_field_contract를 사용자 검증 부록으로 내보낼지 결정된 필드 계약이 없다.<br>CLI/API에서 profile 기반 결과를 안전한 경로에 생성하고 다운로드 metadata를 반환하는 경계가 없다.<br>비밀·민감 필드·평문 URL의 키·재배포 제한 원문을 export 전에 차단하는 sanitizer가 없다. |
| 선택지 | A-flat-company-summary-csv: 기업마다 한 행의 CSV를 만들고 대표 분류·대표 공고·추천 준비사항만 요약한다.; B-evidence-first-workbook-bundle: 정규화된 CSV bundle을 기준 산출물로 만들고, 같은 계약을 다중 시트 XLSX로 렌더링한다. companies, capabilities, job_postings, requirements, sources, exclusions, run_manifest를 분리한다. |
| 권장안 | B-evidence-first-workbook-bundle |
| 권장 근거 | 기업 후보와 정확한 자격요건은 여러 원천·시간·검증 상태의 관계형 결과이므로, 정규화 CSV를 안정된 기준으로 하고 다중 시트 XLSX를 제공해야 사용성과 재현성·보안·출처 검토를 함께 충족한다. |
| 파급효과 | 데이터: 회사·capability·공고·요건·원천·제외·실행 시점을 독립 시트와 foreign key로 보존한다.<br>스키마/API: versioned export contract, CSV renderer, optional XLSX renderer, download manifest를 추가한다.<br>사용자 경험: 한 파일에서 후보 요약과 세부 근거·미확인·제외 사유를 검토할 수 있다.<br>성능: 한 번의 materialized export run으로 반복 조회를 줄이고 파일 크기 한계를 명시한다.<br>비용: XLSX 지원과 QA 비용이 추가되지만 재설계·수동 검증 비용을 줄인다.<br>보안: 비밀·개인정보·약관상 재배포 금지 원문을 sanitizer로 제외하고 출처 표기를 강제한다.<br>마이그레이션: 기존 artifact JSON은 보존하고 새로운 export run을 additive하게 도입한다.<br>테스트: mandatory provenance, referential integrity, deterministic ordering, redaction, sheet contract를 검증한다. |
| 기회비용 | profile·source policy·capability 근거가 없으면 후보를 채운 spreadsheet 대신 제한·미해결 입력을 포함한 결과만 생성한다.<br>원천 약관이 허용하지 않는 전체 원문·공고 설명·개인정보는 export에서 제외한다. |
| 선행 결정 | D-04-career-requirement-verification |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-evidence-first-workbook-bundle<br>규칙: 사용자가 2026-09-11 요청에서 APPROVE로 5개 권장안 B를 결속하라고 명시했다.<br>근거: 정규화 CSV bundle을 기준 계약으로 두고 동일 관계키를 가진 XLSX와 근거·제외·run manifest를 제공한다.<br>결정자: user<br>결정 시각: 2026-09-11T06:25:49.898Z |
| 구현 대상 | src/company_intel/exporting.py (new) — versioned CSV bundle과 optional XLSX workbook renderer<br>src/company_intel/reporting.py — export run manifest, provider status, 한국어 사용자 안내 연결<br>src/company_intel/warehouse.py — export query와 foreign key·provenance materialization<br>src/company_intel/security.py — 비밀·개인정보·재배포 제한 원문 export sanitizer<br>src/company_intel/cli.py — profile 결과 export 명령과 output path 안전 검사<br>src/company_intel/api.py — export job 생성·상태·download metadata endpoint<br>pyproject.toml — 선택된 XLSX renderer 의존성 및 보안 검토<br>tests/test_exporting.py (new) — headers, ordering, links, mandatory evidence, redaction, empty/limited output 검증 |
| 구현 변경 ID | D-05-export-reporting-r3<br>D-05-export-tests-r3<br>D-05-export-verdict-tables-r3<br>D-05-run-manifest-r3<br>D-05-run-manifest-tests-r3 |
| 검증 기준 | 모든 user-facing 회사·공고·요건 행이 source 또는 exclusion record로 추적되는지 검증한다.<br>CSV bundle과 XLSX의 sheet/header·row key가 versioned contract와 일치하는지 검증한다.<br>companies·capabilities·job_postings·requirements·sources·exclusions·run_manifest의 외래키와 orphan 부재를 검증한다.<br>API key, 비밀 환경변수, 개인 구직자 데이터, 평문 URL의 키, 약관상 재배포 금지 원문이 export에 없는지 검증한다.<br>빈 후보·source 제한·identity_unresolved·requirement_unavailable이 성공한 추천처럼 보이지 않고 명시적 exclusion 또는 limitation으로 표시되는지 검증한다.<br>동일 profile·source snapshot·as_of 기준에서는 정렬·run manifest·파일 해시가 결정론적인지 검증한다. |
| 다이어그램 영향 | 분류·검색·요건 검증 결과 → export materialization → CSV bundle/XLSX → 사용자 검토·재현 흐름을 후속 다이어그램에 반영한다. |
| 구현 맥락 topic | evidence-export |

## 6. 산업·국가·규모 동료군 기업 스크리너와 변수별 순위 (`D-06-peer-screener-ranking`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 사용자가 국가·산업·규모와 분석 변수를 선택해 비교 가능한 동료군 안에서 기업을 필터링·내림차순 정렬하려면 어떤 입력·동료군·결과 계약을 채택할 것인가? |
| 누가 | 미국·한국·체코 기업을 비교하는 사용자와 분석 API |
| 무엇을 | 산업·국가·규모 동료군에 한정한 재무·수익성·성장성·인력 생산성·가치 지표 스크리너와 순위 |
| 어디서 | DuckDB 기업·재무 fact, analytics API·CLI, 증거 스프레드시트 |
| 언제 | 사용자가 비교 범위와 정렬 지표를 제출하고 적격 데이터가 있는 기업을 조회할 때 |
| 왜 | 서로 다른 산업·국가·규모의 기업을 하나의 순위에 섞어 왜곡된 결론을 내리지 않기 위해 |
| 어떻게 | country × industry × size_bucket 동료군, 변수 방향, 데이터 커버리지와 제외 사유를 응답에 보존하고 결측 기업을 점수로 보충하지 않는다. |
| 근거 | E-D06-user-screener-purpose — /home/ubuntu/.codex/attachments/2eefe592-56f6-4115-8bd5-2860319bd775/pasted-text.txt:1-4,10-24 — 사용자는 산업별 분리와 보고서 영역별 변수에 따른 기업 내림차순 정리를 요구했고, 비교는 산업·국가·시가총액 구간 안에서 해야 한다는 설계 근거가 있다.<br>E-D06-current-ranking-engine — src/company_intel/analytics.py:77-139 — rank_companies는 country·industry·size_bucket별 그룹 안에서 지표 방향·백분위·커버리지를 계산하지만, 저장된 기업 universe를 필터링해 사용자에게 제공하는 스크리너 계약은 없다. |
| 관찰 사실 | 원문은 산업별 분리와 각 변수의 내림차순 정리를 명시한다.<br>현재 순위 엔진은 동료군 경계를 지키지만 배열 입력만 받고 source capability·분류 제외·실제 데이터 부족을 표시하는 검색 계약은 없다.<br>공개 원천별로 재무·시장·고용 정보의 가용성이 다르므로 전체 지표가 없는 기업을 완전한 순위로 표시하면 안 된다. |
| 충돌 | 단일 종합 점수는 사용하기 쉽지만 변수별 비교와 결측·가중치의 의미를 가린다.<br>국가 간 산업 분류는 다대다 매핑이므로 매핑 근거 없는 동료군 병합은 허용할 수 없다. |
| 미구현 | 저장된 기업 fact에서 국가·산업·규모·변수·기준일을 받는 스크리너 API·CLI가 없다.<br>사용자 선택 변수의 방향·가중치·결측 처리·최소 동료 수를 명시하는 계약이 없다.<br>순위 행에 source coverage, capability, exclusion reason, peer size를 함께 반환하는 통합 검증이 없다. |
| 선택지 | A-global-composite-rank: 모든 국가와 산업을 하나의 고정 종합점수로 합쳐 단일 순위를 반환한다.; B-peer-scoped-evidence-screener: 명시적 국가·산업·규모·변수·기준일을 받아 동료군 안에서만 순위화하고 coverage·근거·제외 사유를 반환한다. |
| 권장안 | B-peer-scoped-evidence-screener |
| 권장 근거 | 사용자가 요구한 산업·국가별 내림차순 비교를 실제로 충족하면서 데이터 부족을 숨기지 않는 유일한 방식이다. |
| 파급효과 | 데이터: 기업 fact·산업 매핑·coverage를 동료군별로 결합한다.<br>스키마/API: 변수 선택형 screener request와 evidence rank response가 필요하다.<br>사용자 경험: 사용자는 변수별 순위·동료 수·제외 근거를 확인한다.<br>성능: 필터된 동료군만 계산한다.<br>비용: 산업 매핑 및 데이터 품질 관리가 추가된다.<br>보안: 공개 사실과 출처만 출력한다.<br>마이그레이션: 기존 analytics 함수 위에 저장소 조회를 추가한다.<br>테스트: 국가·산업·규모 경계와 결측 처리의 통합 테스트가 필요하다. |
| 기회비용 | 전역 순위를 원하면 별도 비교 불가 경고를 받아야 한다. |
| 선행 결정 | D-02-company-capability-taxonomy |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-peer-scoped-evidence-screener<br>규칙: 사용자가 2026-09-11 요청에서 D-06~D-10 권장안 B APPROVE와 로컬 구현을 명시했다.<br>근거: 산업·국가·규모 동료군 안에서 변수별 근거와 결측·제외 사유를 보존하는 스크리너를 사용한다.<br>결정자: user<br>결정 시각: 2026-09-11T09:44:52Z |
| 구현 대상 | src/company_intel/analytics.py<br>src/company_intel/warehouse.py<br>src/company_intel/api.py<br>src/company_intel/cli.py<br>tests/test_analytics.py<br>새 screener 통합 테스트 |
| 구현 변경 ID | D-06-screener-group-tests-r3<br>D-06-screener-signature-groups-r3 |
| 검증 기준 | 동일 산업·국가·규모가 아닌 행이 같은 peer_group에 섞이지 않는지 확인한다.<br>결측 지표·불충분한 동료군이 점수로 위장되지 않고 coverage 또는 exclusion으로 반환되는지 확인한다.<br>사용자가 선택한 변수 방향과 기준일이 결과 메타데이터에 보존되는지 확인한다. |
| 다이어그램 영향 | ScreenerProfile → eligibility filter → peer group → variable ranking → evidence response 흐름을 추가한다. |
| 구현 맥락 topic | company-screening |

## 7. 기업 시간축·시장·거시 비교와 point-in-time 근거 (`D-07-company-timeline-macro-comparison`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 한 기업의 재무·인력·채용공고·시장가격 변화를 국가·산업 거시 변수와 같은 시간축에서 어떤 시점 규칙으로 비교할 것인가? |
| 누가 | 특정 기업을 선택해 변화 원인을 검토하는 사용자와 분석 API |
| 무엇을 | 기업 fact·시장가격·채용 snapshot·사건·거시 series를 시점과 출처가 보이는 하나의 비교 응답으로 반환하는 기능 |
| 어디서 | DuckDB 시계열 테이블과 /company/{entity_id}/timeline API·분석 보고서 |
| 언제 | 기업·국가·기간·비교 지표를 선택해 시간대별 변화를 조회할 때 |
| 왜 | 공시일 이전의 값을 과거 분석에 섞거나 국가 집계를 개별 기업 사실로 오해하지 않기 위해 |
| 어떻게 | period_end, observation_date, available_at, revision_at, collected_at을 구분하고 기업·거시 series를 별도 축으로 반환하며 정렬 불가 사유를 표시한다. |
| 근거 | E-D07-user-time-macro-purpose — /home/ubuntu/.codex/attachments/2eefe592-56f6-4115-8bd5-2860319bd775/pasted-text.txt:1-4,51-80 — 사용자는 전체·개별 기업의 시간대별 변화와 경제·주식 변수를 비교할 방법을 요구했고, 재무·시장·거시 변수의 서로 다른 빈도를 구분해야 한다.<br>E-D07-current-timeline-gap — src/company_intel/api.py:125-142 — 현재 timeline endpoint는 financial_fact·workforce_fact·company_event만 반환하며 market_price와 macro_observation을 반환하거나 정렬 적격성을 표시하지 않는다. |
| 관찰 사실 | 원문은 선택 기업의 시간 변화와 경제·주식 변수 비교를 명시한다.<br>현재 스키마에는 financial_fact, market_price, macro_observation, company_event가 분리 저장된다.<br>현재 timeline API는 거시·시장 데이터를 연결하지 않아 기능 목적을 완전히 충족하지 않는다. |
| 충돌 | 한 배열로 병합하면 빈도·단위·수정시점 차이를 잃는다.<br>거시 집계 series는 기업 개별 성과의 사실이나 인과 증거가 아니다. |
| 미구현 | 기간·국가·시장 security·거시 series 선택을 받는 timeline 비교 요청이 없다.<br>market_price·macro_observation과 point-in-time metadata를 포함한 응답이 없다.<br>단위·기간·available_at 불일치 시 분석 불가를 반환하는 통합 테스트가 없다. |
| 선택지 | A-merged-date-chart: 서로 다른 빈도의 값을 날짜 기준으로 단순 병합해 한 시계열로 반환한다.; B-point-in-time-multiaxis-comparison: 기업·시장·거시 series를 원천·단위·관측일·available_at과 함께 분리 반환하고 검증 가능한 공통 기간만 비교 후보로 표시한다. |
| 권장안 | B-point-in-time-multiaxis-comparison |
| 권장 근거 | 시간축 비교가 원문의 핵심 결과물이므로 빠른 병합보다 관측·공개 시점과 집계 경계를 보존해야 한다. |
| 파급효과 | 데이터: 기업·시장·거시 시계열을 역할별로 결합한다.<br>스키마/API: 시계열 선택과 적격성 메타데이터를 추가한다.<br>사용자 경험: 사용자는 변화와 한계를 함께 검토한다.<br>성능: 기간과 series를 선행 필터링한다.<br>비용: 빈티지·정렬 유지 비용이 있다.<br>보안: 원천 링크와 제한만 제공한다.<br>마이그레이션: 기존 endpoint를 호환적으로 확장한다.<br>테스트: point-in-time 및 다축 응답 계약 테스트를 추가한다. |
| 기회비용 | 실시간·전수 시장가격이 없는 체코 기업은 제한 상태가 남는다. |
| 선행 결정 | D-02-company-capability-taxonomy |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-point-in-time-multiaxis-comparison<br>규칙: 사용자가 2026-09-11 요청에서 D-06~D-10 권장안 B APPROVE와 로컬 구현을 명시했다.<br>근거: 기업·시장·거시 series의 시점·단위·원천을 분리하고 공통 기간 적격성만 비교한다.<br>결정자: user<br>결정 시각: 2026-09-11T09:44:52Z |
| 구현 대상 | src/company_intel/api.py<br>src/company_intel/warehouse.py<br>src/company_intel/normalization.py<br>sql/duckdb_schema.sql<br>새 timeline 통합 테스트 |
| 구현 변경 ID | D-07-axis-series-timeline-r3<br>D-07-timeline-tests-r3 |
| 검증 기준 | 기업·시장·거시 series가 각 원천·단위·관측일·available_at을 보존하는지 확인한다.<br>기업 국가와 거시 국가, security, 기간이 맞지 않으면 비교 가능으로 표시하지 않는지 확인한다.<br>timeline response가 market·macro와 현재 제공되는 fact를 모두 역할별로 반환하는지 확인한다. |
| 다이어그램 영향 | 기업 fact·market·macro·event의 다축 point-in-time 정렬 흐름을 추가한다. |
| 구현 맥락 topic | time-value-events |

## 8. 근거·가정·신뢰도를 보이는 기업 미래가치 시나리오 (`D-08-future-value-scenarios`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 사용자가 선택한 기업의 미래가치를 단일 예측값이 아닌 어떤 재무 근거·가정·낙관/기준/침체 시나리오·데이터 신뢰도와 함께 반환할 것인가? |
| 누가 | 기업 가치와 가정 민감도를 검토하는 사용자 |
| 무엇을 | DCF·상대가치 입력과 데이터 coverage를 분리한 미래가치 범위 |
| 어디서 | analytics 엔진, API·CLI, 기업 분석 보고서 |
| 언제 | 재무·시장·거시 입력의 관측시점이 확인된 후 |
| 왜 | 점수 또는 단일 목표가를 사실·투자 권유처럼 보이지 않게 하기 위해 |
| 어떻게 | 시나리오별 가정·입력 provenance·결측·신뢰도를 명시하고 적격하지 않은 기업에는 계산 불가 사유를 반환한다. |
| 근거 | E-D08-user-future-value-purpose — /home/ubuntu/.codex/attachments/2eefe592-56f6-4115-8bd5-2860319bd775/pasted-text.txt:1-4,67-80 — 사용자는 타깃 기업의 시간대별 변화와 미래가치를 요청했고, 시장가치와 거시 변수는 분석 입력으로 열거되어 있다.<br>E-D08-current-engine-gap — src/company_intel/api.py:115-123;src/company_intel/analytics.py:257-355 — 현재 API는 사용자가 공급한 숫자로 DCF와 future-score를 계산하지만 기업의 저장된 evidence·가정·coverage와 연결하는 조회 계약은 없다. |
| 관찰 사실 | 현재 dcf_scenarios와 future_value_score 함수 및 API endpoint가 있다.<br>README는 미래가치를 침체·기준·낙관 시나리오와 데이터 신뢰도로 낸다고 명시한다.<br>현재 실제 분석 표본은 시장가치와 동료군 부족으로 완성된 미래가치가 아니라고 보고한다. |
| 충돌 | 단일 점수는 편리하지만 가정과 데이터 부족을 숨긴다.<br>무료 시장가격·공시 coverage가 국가별로 달라 전 기업에 동일 수준의 가치를 낼 수 없다. |
| 미구현 | 저장된 기업 fact와 source coverage로 valuation input을 선택·검증하는 서비스가 없다.<br>시나리오 가정·민감도·currency·as_of·결측 사유를 포함하는 기업별 결과 계약이 없다.<br>부족한 시장·재무 입력에 계산 결과 대신 limitation을 내는 end-to-end 테스트가 없다. |
| 선택지 | A-single-score: 모든 기업에 고정 가중치 미래 점수 하나만 반환한다.; B-evidence-bound-scenarios: 기업별 적격 입력과 출처를 확인한 뒤 침체·기준·낙관 DCF, 민감도, coverage·limitation을 함께 반환한다. |
| 권장안 | B-evidence-bound-scenarios |
| 권장 근거 | 사용자가 원하는 미래가치는 실제 기업 근거와 가정 차이를 함께 검토할 수 있어야 하며 단일 예언값이어서는 안 된다. |
| 파급효과 | 데이터: 가치 입력과 provenance를 기업·시점별로 보존한다.<br>스키마/API: 기업 기반 valuation response를 추가한다.<br>사용자 경험: 시나리오 범위·신뢰도·제한이 보인다.<br>성능: 적격 기업만 계산한다.<br>비용: 매핑과 민감도 관리가 필요하다.<br>보안: 투자 권유가 아닌 연구 결과로 제한한다.<br>마이그레이션: 기존 엔진을 additive하게 연결한다.<br>테스트: input eligibility와 scenario invariants를 검사한다. |
| 기회비용 | 가격 또는 현금흐름 근거가 부족한 기업에는 가치 수치를 만들지 않는다. |
| 선행 결정 | D-06-peer-screener-ranking<br>D-07-company-timeline-macro-comparison |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-evidence-bound-scenarios<br>규칙: 사용자가 2026-09-11 요청에서 D-06~D-10 권장안 B APPROVE와 로컬 구현을 명시했다.<br>근거: 기업별 적격 입력·출처·가정과 침체·기준·낙관 시나리오를 함께 반환한다.<br>결정자: user<br>결정 시각: 2026-09-11T09:44:52Z |
| 구현 대상 | src/company_intel/analytics.py<br>src/company_intel/pipeline.py<br>src/company_intel/api.py<br>src/company_intel/cli.py<br>tests/test_analytics.py<br>새 valuation 통합 테스트 |
| 구현 변경 ID | D-08-D09-analysis-prerequisite-r3<br>D-08-D09-analytics-tests-r3 |
| 검증 기준 | 모든 기업별 가치 결과에 scenario assumptions, currency, as_of, source coverage가 있는지 확인한다.<br>시장·재무 적격성이 없는 기업에 단일 가치 숫자가 반환되지 않는지 확인한다.<br>기존 DCF 수학 테스트와 기업 기반 입력 검증을 독립적으로 통과하는지 확인한다. |
| 다이어그램 영향 | evidence eligibility → valuation input mapping → scenario calculation → limitation-aware result 흐름을 추가한다. |
| 구현 맥락 topic | time-value-events |

## 9. AI 도입 사건과 채용·수익성 변화의 근거 기반 검증 (`D-09-ai-event-effect-validation`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 특정 AI 모델의 보급·기업 도입 이후 채용공고·직원 수·수익성·시장 반응 변화를 어떤 사건 근거·대조군·거시 통제로 검증하되 인과로 과장하지 않을 것인가? |
| 누가 | AI 도입 효과를 검토하는 사용자와 분석 서비스 |
| 무엇을 | 공식 사건 증거가 결속된 event study·중단 시계열·DiD 후보 분석 |
| 어디서 | company_event, 기업·시장·거시 시계열, analysis API·report |
| 언제 | 사건일·법인 식별·기간·대조군·가용시점이 확인된 후 |
| 왜 | 단순 전후 비교를 AI의 인과 효과로 잘못 표현하지 않기 위해 |
| 어떻게 | evidence URL·event type·confidence·exposure·대조군 규칙·검정 전제·correlation/causal eligibility를 결과에 보존한다. |
| 근거 | E-D09-user-ai-effect-purpose — /home/ubuntu/.codex/attachments/2eefe592-56f6-4115-8bd5-2860319bd775/pasted-text.txt:1-4,100-130 — 사용자는 특정 AI 모델 보급 뒤 채용률·수익성 변화를 대조·검증할 수 있게 해 달라고 했고, 원문은 사건 데이터베이스와 대조군·DiD를 요구한다.<br>E-D09-current-array-api-gap — src/company_intel/api.py:101-123;src/company_intel/analytics.py:198-256 — 현재 event-study와 DiD endpoint는 배열·인덱스를 직접 받아 계산하며 company_event의 URL·confidence·대조군·point-in-time 적격성을 조회하지 않는다. |
| 관찰 사실 | 현재 event_study와 difference_in_differences 수학 함수는 테스트된다.<br>현재 schema에는 company_event 테이블이 있지만 실제 AI 사건 원천을 적재·검증하는 workflow는 없다.<br>원문은 상관·인과를 구분하고 사전 추세·거시 통제를 확인해야 한다고 명시한다. |
| 충돌 | AI 발표와 실제 도입 시점은 다를 수 있다.<br>공고 수·직원 수·수익성은 서로 다른 빈도와 공개 범위를 가지며, 공고는 채용 완료가 아니다. |
| 미구현 | AI event evidence의 source URL·confidence·exposure·entity identity를 저장·검토하는 입력 경계가 없다.<br>대조군 선택·사전 추세·국가 거시 통제를 명시하는 기업 기반 analysis request가 없다.<br>근거 부족 시 causal result 대신 correlation_ineligible를 반환하는 end-to-end 테스트가 없다. |
| 선택지 | A-unqualified-before-after: 사건 날짜 전후 평균의 차이를 곧바로 AI 효과로 표시한다.; B-evidence-bound-candidate-analysis: 확인된 사건 증거와 식별·시점·대조군·거시 조건을 먼저 검사하고, 통과한 결과만 correlation candidate로 반환하며 인과 한계를 명시한다. |
| 권장안 | B-evidence-bound-candidate-analysis |
| 권장 근거 | 사용자의 목표는 단순 요약이 아니라 검증 가능한 대조이므로 사건 근거와 분석 적격성 없이는 결과를 계산하지 않아야 한다. |
| 파급효과 | 데이터: event evidence와 결과 series의 식별·시점을 보존한다.<br>스키마/API: 기업 기반 event-analysis 요청과 제한 상태가 필요하다.<br>사용자 경험: 결론보다 검증 전제와 근거가 먼저 보인다.<br>성능: 부적격 조합을 차단한다.<br>비용: 사건 확인·대조군 관리 비용이 든다.<br>보안: 인과 과장을 방지한다.<br>마이그레이션: 현재 event/DiD 함수를 재사용한다.<br>테스트: evidence gate와 통계 계산을 분리 검증한다. |
| 기회비용 | 일반 뉴스나 추정 날짜만으로는 AI 효과 분석을 시작할 수 없다. |
| 선행 결정 | D-07-company-timeline-macro-comparison |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-evidence-bound-candidate-analysis<br>규칙: 사용자가 2026-09-11 요청에서 D-06~D-10 권장안 B APPROVE와 로컬 구현을 명시했다.<br>근거: 확인된 사건·식별·시점·대조군·거시 조건이 있는 분석만 후보 결과로 반환한다.<br>결정자: user<br>결정 시각: 2026-09-11T09:44:52Z |
| 구현 대상 | sql/duckdb_schema.sql<br>src/company_intel/warehouse.py<br>src/company_intel/analytics.py<br>src/company_intel/api.py<br>src/company_intel/pipeline.py<br>tests/test_analytics.py<br>새 event evidence 통합 테스트 |
| 구현 변경 ID | D-08-D09-analysis-prerequisite-r3<br>D-08-D09-analytics-tests-r3 |
| 검증 기준 | 사건 분석이 source URL·event_date·entity identity·available_at·대조군 근거 없이 실행되지 않는지 확인한다.<br>공고 수를 실제 고용 완료 수로 표기하지 않는지 확인한다.<br>통과 결과가 인과 확정이 아닌 correlation candidate와 전제·경고를 함께 반환하는지 확인한다. |
| 다이어그램 영향 | event evidence → eligibility gate → aligned outcomes/control → event study/DiD → qualified result 흐름을 추가한다. |
| 구현 맥락 topic | time-value-events |

## 10. 현재 채용공고 확인과 국가·직무·요건 기반 필터 검색 (`D-10-job-availability-filtered-discovery`)

| 구분 | 내용 |
|---|---|
| 상태 | accepted |
| 결정 질문 | 사용자가 실제 공개 채용공고를 국가·산업·직무·근무형태·언어·검증된 required/preferred 요건으로 필터링해 기업과 공고를 함께 확인하려면 어떤 검색 계약을 완성할 것인가? |
| 누가 | 채용공고와 준비사항을 확인하는 사용자 |
| 무엇을 | 공고 snapshot을 채용 수요로 명시하고 기업·공고·요건을 국가와 명시 필터로 결합한 검색 |
| 어디서 | SearchProfile, job_posting_snapshot, job_requirement, CLI·FastAPI·spreadsheet |
| 언제 | 프로필을 제출하고 현재·마감·상세근거 상태를 확인할 때 |
| 왜 | 기업명 키워드만 맞는 결과나 근거 없는 자격증을 실제 채용·필수 요건으로 오해하지 않기 위해 |
| 어떻게 | 활성 공고·국가·직무·산업·고용형태·언어·요건 텍스트와 evidence status를 명시적으로 필터링하고 미확인 요건은 매칭에 사용하지 않는다. |
| 근거 | E-D10-public-job-demand-purpose — /home/ubuntu/.codex/attachments/2eefe592-56f6-4115-8bd5-2860319bd775/pasted-text.txt:513-529 — 원문은 회사별 공개 채용공고·직무·위치·설명에서 채용 수요를 확인하되, 공고는 실제 채용 완료가 아니라는 한계를 지켜야 한다고 정리한다.<br>E-D10-current-filter-gap — src/company_intel/search.py:27-50;src/company_intel/api.py:157-176 — SearchProfile에는 industries·languages·employment_types가 있으나 rank_candidates는 country·capability·이름/산업/제목 키워드만 사용하고, API는 공고 목록이나 요건 조건 검색을 제공하지 않는다. |
| 관찰 사실 | 현재 SearchProfile은 countries, job_keywords, industries, required_capabilities, languages, employment_types를 선언한다.<br>현재 rank_candidates는 industries·languages·employment_types를 적용하지 않고, Warehouse.search_candidates는 entity만 조회해 공고·요건으로 필터링하지 않는다.<br>현재 requirements endpoint는 하나의 provider/job_id를 조회할 뿐 검색 결과에 공고와 요건을 함께 반환하지 않는다.<br>공개 공고는 채용 수요이지 실제 입사·채용 완료 인원이 아니다. |
| 충돌 | 넓은 키워드 검색은 후보 수를 늘리지만 고용형태·언어·요건 조건을 무시한다.<br>공고 상세 근거가 없는 요건은 맞춤 자격증 필터의 true 조건으로 사용할 수 없다. |
| 미구현 | industries·languages·employment_types 및 requirement 상태를 실제 SQL·ranking filter로 적용하지 않는다.<br>활성·마감·삭제 상태, 국가별 shortage, 직무별 공고와 기업 결과를 함께 반환하는 contract가 없다.<br>required와 preferred를 구분하고 requirement_unavailable을 false match가 아닌 제한 상태로 처리하는 end-to-end test가 없다. |
| 선택지 | A-company-keyword-only: 회사명·직무 키워드만으로 기업 후보를 반환하고 공고·요건은 별도 수동 조회에 맡긴다.; B-evidence-filtered-job-discovery: 명시된 필터를 실제 기업·활성 공고·검증된 요건 조인에 적용하고, 공고·근거·제외·shortage를 한 응답과 export에 함께 반환한다. |
| 권장안 | B-evidence-filtered-job-discovery |
| 권장 근거 | 사용자가 명시한 채용확인·필터링·국가 분리·필요 요건 필터를 모두 실제 데이터 행동으로 만들고, 미확인을 추천으로 바꾸지 않는 방식이다. |
| 파급효과 | 데이터: 기업·공고·요건을 evidence-first 관계로 조회한다.<br>스키마/API: 실제 filter semantics와 job match 응답이 추가된다.<br>사용자 경험: 한 검색에서 채용 수요·요건·제외를 검토한다.<br>성능: 필터와 활성 공고 조건을 저장소에서 적용한다.<br>비용: 국가별 source coverage와 테스트 유지 비용이 생긴다.<br>보안: 개인 민감 정보를 저장하지 않는다.<br>마이그레이션: 기존 검색·요건 endpoint를 additive하게 확장한다.<br>테스트: 모든 선언 필터와 공고/요건 경계를 end-to-end로 검증한다. |
| 기회비용 | 공개 ATS·공공 공고가 없는 국가·기업에는 채용 확인 불가가 정답으로 남는다. |
| 선행 결정 | D-03-search-profile-and-discovery<br>D-04-career-requirement-verification |
| 의존 예외 | — |
| 사용자 결정 | 처분: ACCEPT<br>선택지 ID: B-evidence-filtered-job-discovery<br>규칙: 사용자가 2026-09-11 요청에서 D-06~D-10 권장안 B APPROVE와 로컬 구현을 명시했다.<br>근거: 국가·직종·연봉·위치·근무형태·언어·산업·요건을 실제 공고와 근거 행에 적용한다.<br>결정자: user<br>결정 시각: 2026-09-11T09:44:52Z |
| 구현 대상 | src/company_intel/models.py<br>src/company_intel/search.py<br>src/company_intel/warehouse.py<br>src/company_intel/api.py<br>src/company_intel/cli.py<br>src/company_intel/exporting.py<br>tests/test_search_profile.py<br>tests/test_career_requirements.py<br>새 job discovery 통합 테스트 |
| 구현 변경 ID | D-10-api-compatibility-report-r3<br>D-10-api-profile-parity-r3<br>D-10-cli-docs-r3<br>D-10-cli-interactive-routing-r3<br>D-10-cli-workflow-tests-r3<br>D-10-interactive-module-r3<br>D-10-interactive-tests-r3<br>D-10-job-search-tests-r3<br>D-10-job-search-verdicts-r3<br>D-10-korean-status-docs-r3 |
| 검증 기준 | industries·languages·employment_types와 국가 필터 각각이 실제 결과 집합을 줄이는지 확인한다.<br>검증된 required 요건만 필수 매칭에 쓰고 preferred와 requirement_unavailable을 구분하는지 확인한다.<br>응답이 기업만이 아니라 활성 공고·source URL·snapshot date·제외·shortage를 반환하는지 확인한다.<br>공고 수요를 실제 채용 완료 인원으로 표기하지 않는지 확인한다. |
| 다이어그램 영향 | JobSearchProfile → active job filter → requirement evidence filter → company/job match·shortage·export 흐름을 추가한다. |
| 구현 맥락 topic | search-career-evidence |
