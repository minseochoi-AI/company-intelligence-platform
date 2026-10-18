# cil-notion-approval-country-expansion-20261015 — 의사결정 워크북

> 이 파일은 같은 `campaign.json`·결정 JSON에서 만든 읽기용 화면입니다.
> 현재 상태는 plan·result·검증 attempt와 파일 해시가 맞을 때만 통과로 표시합니다.
> 의도·설계 이유와 최종 해결 여부는 사람이 정본과 근거를 확인해 판단합니다.

## 이번 목적과 사용자 판단

### 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/connectors/opendart_master.py, tests/test_opendart_master.py<br>주요 기호: OpenDartMasterIndex, resolve_corp_code, test_opendart_master_index |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/connectors/opendart_master.py — 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터<br>tests/test_opendart_master.py — 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D01-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D01-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C01-opendart-master-K01: 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 대한민국 119,634개 상장/외감 법인 전수를 로컬 DuckDB에 색인하여 임의 기업명에서 corp_code를 0.001초 내 동적 해소하는 어댑터를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D01 정본과 상세 근거](decisions/01-cil-d01.json)

### 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/connectors/mpsv_stream.py, tests/test_mpsv_stream.py<br>주요 기호: stream_mpsv_vacancies, aggregate_by_cz_isco, test_mpsv_stream_parsing |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/connectors/mpsv_stream.py — 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑<br>tests/test_mpsv_stream.py — 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D02-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D02-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C02-czech-mpsv-K01: 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 체코 노동사회부(MPSV)의 178.8MB 전수 구인공고 JSON 덤프를 메모리 폭증 없이 청크 단위로 스트리밍 파싱하여 CZ-ISCO 직무 코드로 집계하는 수집기를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D02 정본과 상세 근거](decisions/02-cil-d02.json)

### 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/connectors/ares_dynamic.py, tests/test_ares_dynamic.py<br>주요 기호: AresDynamicClient, get_economic_subject, test_ares_dynamic_lookup |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/connectors/ares_dynamic.py — 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기<br>tests/test_ares_dynamic.py — 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D03-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D03-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C03-czech-ares-K01: 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 체코 경제주체 레지스트리(ARES) REST API를 통해 기업 상호명 및 IČO로 18개 이상 CZ-NACE 산업분류와 본사 주소를 실시간 동적 조회하는 어댑터를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D03 정본과 상세 근거](decisions/03-cil-d03.json)

### 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/connectors/worknet.py, tests/test_worknet.py<br>주요 기호: WorknetJobConnector, search_worknet_jobs, test_worknet_jobs_parsing |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/connectors/worknet.py — 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터<br>tests/test_worknet.py — 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D04-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D04-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C04-worknet-public-K01: 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | .env에 등록된 공공데이터포털(nomal) 및 고용노동부 워크넷 OpenAPI를 활용하여 실시간 전국 공공/민간 채용공고와 NCS 직무 단위를 동적 조회하는 커넥터를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D04 정본과 상세 근거](decisions/04-cil-d04.json)

### 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/notion_queue.py, tests/test_notion_queue.py<br>주요 기호: NotionApprovalQueue, create_draft_page, poll_approved_pages, test_notion_approval_flow |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/notion_queue.py — 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진<br>tests/test_notion_queue.py — 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D05-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D05-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C05-notion-approval-K01: 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 에이전트가 생성한 기업/직무 분석 보고서를 노션 데이터베이스('에이전트 개발 로그')에 초안으로 등록하고, 스마트폰 노션 앱에서의 '승인' 토글을 감지하는 모바일 승인 큐를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D05 정본과 상세 근거](decisions/05-cil-d05.json)

### Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/publisher/blogger_publisher.py, tests/test_blogger_publisher.py<br>주요 기호: BloggerPublisher, publish_post_from_notion, test_blogger_headless_publishing |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/publisher/blogger_publisher.py — Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔<br>tests/test_blogger_publisher.py — Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D06-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D06-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C06-blogger-headless-K01: Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 노션 모바일 승인 큐에서 승인된 보고서 초안을 감지하여 Google Blogger API v3로 즉시 원클릭 배포하고 배포 URL을 노션에 역기입하는 헤드리스 퍼블리셔를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D06 정본과 상세 근거](decisions/06-cil-d06.json)

### 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 |
| 현재 입력 문제 | 대상 모듈: src/company_intel/dynamic_screening.py, tests/test_dynamic_screening.py<br>주요 기호: DynamicScreeningEngine, run_screening_pipeline, test_dynamic_screening_pipeline |
| 수정 후 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 생산자·소비자 책임 | src/company_intel/dynamic_screening.py — 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통<br>tests/test_dynamic_screening.py — 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 검증 단위 테스트 |
| 대안의 차이 | A: 기존 단일 고정 픽스처(Fixture) 상태 유지<br>B: 동적 마스터 색인 및 스트리밍 어댑터 구축 (권장) |
| 수용·거부 조건 | CIL-D07-O01: 수용 설명 미등록 / 거부 설명 미등록<br>CIL-D07-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | CIL-C07-platform-integration-K01: 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 → 테스트 성공 |
| 확인 한계 | 준비 확인 필요 · 승인 미확인 · 증거 오래됨 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 2026-10-15 실시간 확장 단계 |
| 이번 판단 | 구축된 OpenDART 마스터, 체코 MPSV/ARES, 워크넷, 노션-Blogger 배포 파이프라인을 통합하여 #1 채용 및 #2 기업 스크리닝 엔드포인트를 실시간 동적 검색 체계로 완성할 방안은 무엇인가? |
| 조건별 다음 행동 | PREPARE — 현재 Plan·문맥·범위 결속을 확인합니다. |

[CIL-D07 정본과 상세 근거](decisions/07-cil-d07.json)

## 캠페인 요약

| 항목 | 값 |
|---|---|
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 목적·범위 | 노션 모바일 승인 기반 Blogger 자동 배포 및 한국·체코 전수 기업 채용·재무 API 확장을 통한 1·2단계 플랫폼 완성 |
| 캠페인 단계 | decision-approved |
| 현재 검증 | 미완료·상세 상태 확인 |

## 의사결정 요약

| No | 작업 단위 | 상태 | 결정 이름 | 권장안 | 선행 결정 | 사용자 결정 |
|---:|---|---|---|---|---|---|
| 1 | CIL-C01-opendart-master | accepted | 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 | B | — | ACCEPT |
| 2 | CIL-C02-czech-mpsv | accepted | 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 | B | — | ACCEPT |
| 3 | CIL-C03-czech-ares | accepted | 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 | B | — | ACCEPT |
| 4 | CIL-C04-worknet-public | accepted | 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 | B | — | ACCEPT |
| 5 | CIL-C05-notion-approval | accepted | 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 | B | — | ACCEPT |
| 6 | CIL-C06-blogger-headless | accepted | Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 | B | CIL-D05 | ACCEPT |
| 7 | CIL-C07-platform-integration | accepted | 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 | B | CIL-D01<br>CIL-D02<br>CIL-D03<br>CIL-D04<br>CIL-D06 | ACCEPT |

## 작업 단위별 검증 상태

| 작업 단위 | 현재 상태 | 이유 |
|---|---|---|
| CIL-C01-opendart-master | 오래됨 | scope-lock-missing |
| CIL-C02-czech-mpsv | 오래됨 | scope-lock-missing |
| CIL-C03-czech-ares | 오래됨 | scope-lock-missing |
| CIL-C04-worknet-public | 오래됨 | scope-lock-missing |
| CIL-C05-notion-approval | 오래됨 | scope-lock-missing |
| CIL-C06-blogger-headless | 오래됨 | scope-lock-missing |
| CIL-C07-platform-integration | 오래됨 | scope-lock-missing |

## 검증 실패 조건과 실제 해석

| 실패 코드 | 실패 배치 / 표시된 TU | 검증기가 거부하는 정확한 조건 | 실제 확인과 해석 |
|---|---|---|---|
| — | 관측 자료 없음 | 조건 설명 미등록 | 실패가 없다는 뜻이 아님 |

> 배치 실패로 표시된 TU 수는 각 TU의 독립 오류 수가 아닐 수 있습니다.
> 관측 범위·근거의 신선도를 확인하며, 자료 미등록은 실패 0건을 뜻하지 않습니다.

## Plan·결정별 변경 책임과 완료 경계

| Plan / 결정 | 해결하려는 문제·목표 | 연결된 컴포넌트와 책임 | 현재 프로젝트 동작 변화 | 파일 수 | 의미적 완료 여부 |
|---|---|---|---|---:|---|
| CIL-C01-opendart-master-plan-r1 / CIL-D01 | 대상 모듈: src/company_intel/connectors/opendart_master.py, tests/test_opendart_master.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터<br>대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C01-opendart-master-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C02-czech-mpsv-plan-r1 / CIL-D02 | 대상 모듈: src/company_intel/connectors/mpsv_stream.py, tests/test_mpsv_stream.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑<br>체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C02-czech-mpsv-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C03-czech-ares-plan-r1 / CIL-D03 | 대상 모듈: src/company_intel/connectors/ares_dynamic.py, tests/test_ares_dynamic.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기<br>체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C03-czech-ares-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C04-worknet-public-plan-r1 / CIL-D04 | 대상 모듈: src/company_intel/connectors/worknet.py, tests/test_worknet.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터<br>공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C04-worknet-public-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C05-notion-approval-plan-r1 / CIL-D05 | 대상 모듈: src/company_intel/notion_queue.py, tests/test_notion_queue.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진<br>노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C05-notion-approval-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C06-blogger-headless-plan-r1 / CIL-D06 | 대상 모듈: src/company_intel/publisher/blogger_publisher.py, tests/test_blogger_publisher.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔<br>Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C06-blogger-headless-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| CIL-C07-platform-integration-plan-r1 / CIL-D07 | 대상 모듈: src/company_intel/dynamic_screening.py, tests/test_dynamic_screening.py → 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 | 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통<br>1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 검증 단위 테스트<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/CIL-C07-platform-integration-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |

> 파일 수는 해당 plan·결정에 연결된 고유 변경 경로 수(테스트 포함)입니다.
> 공유 경로 때문에 행별 수를 합산하지 않습니다. 계획상 변화나 차단 기준 통과만으로 의미적 완료를 확정하지 않습니다.

## 의사결정 상세

<details>
<summary>의도·설계 근거가 필요할 때 펼치기</summary>

## 1. 대한민국 11.9만 전체 법인 고유번호 마스터 DuckDB 색인 및 동적 기업 식별 어댑터 (`CIL-D01`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/connectors/opendart_master.py, tests/test_opendart_master.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | 119,634개 법인 마스터 테이블 생성 확인, 삼성전자/카카오 등 임의 기업명 동적 해소 0.005초 이하 검증 |

## 2. 체코 노동사회부(MPSV) 178MB 실시간 전수 구인공고 스트리밍 수집기 및 CZ-ISCO 매핑 (`CIL-D02`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/connectors/mpsv_stream.py, tests/test_mpsv_stream.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | 스트리밍 청크 읽기 테스트, CZ-ISCO 4자리 직무별 공고 수 및 급여 집계 무결성 검증 |

## 3. 체코 ARES 경제주체 레지스트리 기반 상호·주소·CZ-NACE 다중 산업분류 동적 조회기 (`CIL-D03`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/connectors/ares_dynamic.py, tests/test_ares_dynamic.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | Škoda Auto(00177041) 및 임의 체코 법인 조회 시 NACE 코드 목록 추출 검증 |

## 4. 공공데이터포털(nomal) 및 고용노동부 워크넷 실시간 채용·직무 연계 어댑터 (`CIL-D04`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/connectors/worknet.py, tests/test_worknet.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | 공공취업정보 getList 실시간 호출 결과 정규화 및 키 부재 시 안전한 폴백 검증 |

## 5. 노션 Cloud API 기반 모바일 승인 큐(Human-in-the-Loop) 및 상태 감시 엔진 (`CIL-D05`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/notion_queue.py, tests/test_notion_queue.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | 노션 페이지 블록 생성 및 상태 필터 쿼리 Mock/Live 무결성 테스트 |

## 6. Google Blogger API v3 기반 모바일 승인 연동 헤드리스 자동 퍼블리셔 (`CIL-D06`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/publisher/blogger_publisher.py, tests/test_blogger_publisher.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | HTML 렌더링 무결성, dry-run 배포 응답 파싱, 토큰 마스킹 검증 |

## 7. 1단계(채용·직무 탐색) 및 2단계(기업 식별·스크리닝) 통합 CLI 및 API 엔드포인트 개통 (`CIL-D07`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 대상 모듈: src/company_intel/dynamic_screening.py, tests/test_dynamic_screening.py (근거: docs/decision-campaigns/2026-10-15/cil-notion-approval-country-expansion-20261015/evidence/notion-mobile-approval-plan.md) |
| 바꿀 동작 | 실재성 검증 완료 원천에 한하여 점진적이고 수술적으로 통합 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 동적 마스터 테이블 색인, 스트리밍 파서, Cloud API 연동 및 단위 테스트 격리 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 스마트폰 노션 앱 원터치 승인 후 자동 블로그 포스팅 |
| 통과를 확인할 증거 | 동적 기업 스크리닝 결과에 당좌비율/현금비율/고용탄력성 지표 산출 확인 및 전체 pytest 100% 통과 |

</details>

## 정본과 상세 근거

- [CIL-D01 정본 JSON](decisions/01-cil-d01.json)
- [CIL-D02 정본 JSON](decisions/02-cil-d02.json)
- [CIL-D03 정본 JSON](decisions/03-cil-d03.json)
- [CIL-D04 정본 JSON](decisions/04-cil-d04.json)
- [CIL-D05 정본 JSON](decisions/05-cil-d05.json)
- [CIL-D06 정본 JSON](decisions/06-cil-d06.json)
- [CIL-D07 정본 JSON](decisions/07-cil-d07.json)
- [캠페인 정본](campaign.json)


## 변경점 상세

고유 파일 14개 · operation 14개. [선언 inventory](component-inventory.json)의 모듈 컴포넌트 0개 · 미등록 경로 14개. 실제 기능 수로 추정하지 않습니다. 파일 수와 기능 수는 다릅니다.

<details>
<summary>모든 소유 변경점과 개별 책임</summary>

### CIL-C01-opendart-master

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C01-opendart-master-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [opendart_master.py](../../../../src/company_intel/connectors/opendart_master.py) | file-change-cil-d01-01 | CIL-D01 |
| [test_opendart_master.py](../../../../tests/test_opendart_master.py) | file-change-cil-d01-02 | CIL-D01 |

### CIL-C02-czech-mpsv

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C02-czech-mpsv-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [mpsv_stream.py](../../../../src/company_intel/connectors/mpsv_stream.py) | file-change-cil-d02-01 | CIL-D02 |
| [test_mpsv_stream.py](../../../../tests/test_mpsv_stream.py) | file-change-cil-d02-02 | CIL-D02 |

### CIL-C03-czech-ares

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C03-czech-ares-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [ares_dynamic.py](../../../../src/company_intel/connectors/ares_dynamic.py) | file-change-cil-d03-01 | CIL-D03 |
| [test_ares_dynamic.py](../../../../tests/test_ares_dynamic.py) | file-change-cil-d03-02 | CIL-D03 |

### CIL-C04-worknet-public

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C04-worknet-public-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [worknet.py](../../../../src/company_intel/connectors/worknet.py) | file-change-cil-d04-01 | CIL-D04 |
| [test_worknet.py](../../../../tests/test_worknet.py) | file-change-cil-d04-02 | CIL-D04 |

### CIL-C05-notion-approval

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C05-notion-approval-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [notion_queue.py](../../../../src/company_intel/notion_queue.py) | file-change-cil-d05-01 | CIL-D05 |
| [test_notion_queue.py](../../../../tests/test_notion_queue.py) | file-change-cil-d05-02 | CIL-D05 |

### CIL-C06-blogger-headless

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C06-blogger-headless-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [blogger_publisher.py](../../../../src/company_intel/publisher/blogger_publisher.py) | file-change-cil-d06-01 | CIL-D06 |
| [test_blogger_publisher.py](../../../../tests/test_blogger_publisher.py) | file-change-cil-d06-02 | CIL-D06 |

### CIL-C07-platform-integration

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/CIL-C07-platform-integration-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [dynamic_screening.py](../../../../src/company_intel/dynamic_screening.py) | file-change-cil-d07-01 | CIL-D07 |
| [test_dynamic_screening.py](../../../../tests/test_dynamic_screening.py) | file-change-cil-d07-02 | CIL-D07 |

</details>
