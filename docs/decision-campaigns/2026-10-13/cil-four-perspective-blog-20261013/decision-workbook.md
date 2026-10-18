# cil-four-perspective-blog-20261013 — 의사결정 워크북

> 이 파일은 같은 `campaign.json`·결정 JSON에서 만든 읽기용 화면입니다.
> 현재 상태는 plan·result·검증 attempt와 파일 해시가 맞을 때만 통과로 표시합니다.
> 의도·설계 이유와 최종 해결 여부는 사람이 정본과 근거를 확인해 판단합니다.

## 이번 목적과 사용자 판단

### 산업별 목차와 단일 보고서의 네 독자 관점

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. |
| 현재 입력 문제 | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/taxonomy.py — 적용 경계: apps/company-report-blog/src/report_blog/taxonomy.py; 명시 sector parent/order와 네 audience를 유지하고 slug collision/분류 미등록을 검사; 목차는 report_id로 연결<br>apps/company-report-blog/schemas/taxonomy.schema.json — 적용 경계: apps/company-report-blog/schemas/taxonomy.schema.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다.<br>apps/company-report-blog/config/taxonomy.json — 적용 경계: apps/company-report-blog/config/taxonomy.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다.<br>apps/company-report-blog/tests/test_taxonomy.py — 적용 경계: apps/company-report-blog/tests/test_taxonomy.py; 새 테스트 파일: 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report_id의 중복 방지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. |
| 수용·거부 조건 | B-D01-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C01-taxonomy-K01: 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report_id의 중복 방지 → 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report_id의 중복 방지 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 산업별 목차와 단일 보고서의 네 독자 관점를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D01 정본과 상세 근거](decisions/01-b-d01.json)

### 원천·계산·AI 해석·작성자 평가의 별도 revision

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. |
| 현재 입력 문제 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/models.py — 적용 경계: apps/company-report-blog/src/report_blog/models.py; 원천/계산/AI/사용자 schema를 독립 타입으로 검사하고 네 perspective 및 claim별 evidence 요구<br>apps/company-report-blog/src/report_blog/opinions.py — 적용 경계: apps/company-report-blog/src/report_blog/opinions.py; 사용자만 opinion을 쓰며 visibility와 based_on revision을 저장; AI 재생성 시 원문을 그대로 보존<br>apps/company-report-blog/src/report_blog/compose.py — 적용 경계: apps/company-report-blog/src/report_blog/compose.py; CIL structured 결과와 AI claim을 결합하되 근거 없는 숫자/빈 시계열은 검증 실패 또는 명시 한계<br>apps/company-report-blog/src/report_blog/render.py — 적용 경계: apps/company-report-blog/src/report_blog/render.py; Jinja escape/StrictUndefined와 URL scheme allowlist; 네 섹션과 사실/AI/사람 앵커를 한 HTML에 출력<br>apps/company-report-blog/templates/report.html — 적용 경계: apps/company-report-blog/templates/report.html; 원천/계산 근거, 네 AI 관점, 사용자 의견, 관련 분석 목차를 한 페이지에 분리; private 평가 제외<br>apps/company-report-blog/schemas/report.schema.json — 적용 경계: apps/company-report-blog/schemas/report.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다.<br>apps/company-report-blog/schemas/human-evaluation.schema.json — 적용 경계: apps/company-report-blog/schemas/human-evaluation.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다.<br>apps/company-report-blog/tests/test_report_contracts.py — 적용 경계: apps/company-report-blog/tests/test_report_contracts.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>apps/company-report-blog/tests/test_human_preservation.py — 적용 경계: apps/company-report-blog/tests/test_human_preservation.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>apps/company-report-blog/tests/test_render.py — 적용 경계: apps/company-report-blog/tests/test_render.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. |
| 수용·거부 조건 | B-D02-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C02-report-opinions-K01: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단 → 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 원천·계산·AI 해석·작성자 평가의 별도 revision를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D02 정본과 상세 근거](decisions/02-b-d02.json)

### 기존 CIL parameterized 수집·재무·채용·인력·거시 경로 보강

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. |
| 현재 입력 문제 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다.<br>수집은 새 report-blog CLI와 collectors module이 소유한다. 기존 23개 CIL CLI와 Korean guide는 수정하지 않는다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | src/company_intel/connectors/collectors.py — 적용 경계: src/company_intel/connectors/collectors.py; allowlist URL·entity/date/page·read-only collector와 원문 provenance; arbitrary URL/SSRF·키 노출·무한 pagination 금지<br>src/company_intel/connectors/keyed.py — 적용 경계: src/company_intel/connectors/keyed.py; 기존 probe 기본 의미 유지; 동적 FRED series id와 BEA 관측/catalog 분리; DART 직원 공시 typed 정규화<br>src/company_intel/connectors/keyless.py — 적용 경계: src/company_intel/connectors/keyless.py; SEC concept/기간/단위별 전체 필요한 행 및 filing history; Eurostat dimension/category mapping; 기존 표본 probe 유지<br>src/company_intel/normalization.py — 적용 경계: src/company_intel/normalization.py; financial concept/account/statement/currency와 직원 공시/공고/거시 observation class 분리; 같은 comparable signature에서만 계산<br>config/providers.json — 적용 경계: config/providers.json; 신규 수집 4 operation과 기존8증강의 source mapping·권리·키 전제를 별도 등록; IMF 재승격 금지<br>tests/test_parameterized_collection.py — 적용 경계: tests/test_parameterized_collection.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>tests/test_blog_source_mapping.py — 적용 경계: tests/test_blog_source_mapping.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. |
| 수용·거부 조건 | B-D03-O01: 수용 설명 미등록 / 거부 설명 미등록<br>B-D03-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C03-cil-coverage-K01: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지 → 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 기존 CIL parameterized 수집·재무·채용·인력·거시 경로 보강를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D03 정본과 상세 근거](decisions/03-b-d03.json)

### 공식 SDK 기반 작은 Blogger 게시 adapter

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. |
| 현재 입력 문제 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/blogger.py — 적용 경계: apps/company-report-blog/src/report_blog/blogger.py; 소유 계정 blog 해소·list/get/draft insert/patch/publish; dry-run/명시 mode, 불확실 응답 대조 및 외부 편집 충돌 차단<br>apps/company-report-blog/src/report_blog/google_auth.py — 적용 경계: apps/company-report-blog/src/report_blog/google_auth.py; 사용자 OAuth 파일 외부 secret reference; scope별 서비스·refresh·30s transport; key나 token 출력 금지<br>apps/company-report-blog/config/provider-contracts.json — 적용 경계: apps/company-report-blog/config/provider-contracts.json; Google7+성과4의 호출형식·secret ref·scope·read/write·retry/쿼터/권리/exit 경계를 분리<br>apps/company-report-blog/tests/test_blogger_adapter.py — 적용 경계: apps/company-report-blog/tests/test_blogger_adapter.py; 새 테스트 파일: isDraft=True 명시, 같은 content_key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. |
| 수용·거부 조건 | B-D04-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C04-blogger-K01: isDraft=True 명시, 같은 content_key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회 → isDraft=True 명시, 같은 content_key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 공식 SDK 기반 작은 Blogger 게시 adapter를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D04 정본과 상세 근거](decisions/04-b-d04.json)

### 게시 장부·분석 교차링크·실행 실패 복구

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. |
| 현재 입력 문제 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/ledger.py — 적용 경계: apps/company-report-blog/src/report_blog/ledger.py; SQLite transactional outbox·single writer·stable content_key·append revision; network와 DB의 비원자성 복구<br>apps/company-report-blog/src/report_blog/links.py — 적용 경계: apps/company-report-blog/src/report_blog/links.py; 명시 이유/관계의 typed 연결; 산업/직종/기업/시점/반박 글의 안정 ID 및 missing URL 상태; 자동 인과 추정 금지<br>apps/company-report-blog/migrations/001.sql — 적용 경계: apps/company-report-blog/migrations/001.sql; report/revision/evaluation/relation/publication_attempt 테이블과 고유 content_key 제약; 고객/키 데이터 저장 금지<br>apps/company-report-blog/tests/test_ledger.py — 적용 경계: apps/company-report-blog/tests/test_ledger.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>apps/company-report-blog/tests/test_relations.py — 적용 경계: apps/company-report-blog/tests/test_relations.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. |
| 수용·거부 조건 | B-D05-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C05-ledger-links-K01: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리 → 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 게시 장부·분석 교차링크·실행 실패 복구를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D05 정본과 상세 근거](decisions/05-b-d05.json)

### 소유 블로그의 유입·관측 수익과 사용자 판단 분리

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. |
| 현재 입력 문제 | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/metrics.py — 적용 경계: apps/company-report-blog/src/report_blog/metrics.py; 계정·권한·시점·통화 및 실제 dimension coverage를 유지한 readonly 조회; unavailable/unknown와0을 구분<br>apps/company-report-blog/tests/test_metrics.py — 적용 경계: apps/company-report-blog/tests/test_metrics.py; 새 테스트 파일: 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. |
| 수용·거부 조건 | B-D06-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C06-metrics-K01: 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope → 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 소유 블로그의 유입·관측 수익과 사용자 판단 분리를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D06 정본과 상세 근거](decisions/06-b-d06.json)

### 수동 실행 CLI와 thin skill의 책임·재사용 경계

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. |
| 현재 입력 문제 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. |
| 수정 후 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/pyproject.toml — 적용 경계: apps/company-report-blog/pyproject.toml; 별도 앱 console entrypoint 및 SDK2.201.0/google-auth2.62.0/oauthlib1.5.0/Jinja3.1.6; CIL 루트 패키지는 변경하지 않음<br>apps/company-report-blog/uv.lock — 적용 경계: apps/company-report-blog/uv.lock; 위 직접 버전과 전이 의존성 hash를 lock하고 Python3.13 resolver/local test; 설치 성공을 live 연동으로 판단하지 않음<br>apps/company-report-blog/src/report_blog/__init__.py — 적용 경계: apps/company-report-blog/src/report_blog/__init__.py; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.<br>apps/company-report-blog/src/report_blog/cli.py — 새 앱 CLI가 typed CollectionSpec으로 collectors를 호출하고 기존 CIL CLI의 ingest/분석을 연결한다. 기존 CIL 23개 명령·Korean help/guide 파일은 수정하지 않는다. 일반 실행은 preview/초안만 생성한다. publish 및 이미 공개된 글의 content/labels 변경은 대상 report revision과 post ID에 대한 명시 mode/실행 허용이 없으면 거부한다. OAuth blogger scope와 정책 승인을 개별 게시 허가로 대체하지 않는다.<br>apps/company-report-blog/README.md — 적용 경계: apps/company-report-blog/README.md; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.<br>apps/company-report-blog/skills/company-report-blog/SKILL.md — 적용 경계: apps/company-report-blog/skills/company-report-blog/SKILL.md; 네 관점 작성과 CIL 호출·의견 소유권·preview/draft/게시·metrics를 연결하는 thin skill; 기존 분석 스킬과 캠페인 권위 보존<br>apps/company-report-blog/skills/company-report-blog/agents/openai.yaml — 적용 경계: apps/company-report-blog/skills/company-report-blog/agents/openai.yaml; 스킬 trigger/예시를 보고서 실행으로 한정하고 암묵 발동이 원격 쓰기 승인을 만들지 않도록 지침<br>apps/company-report-blog/tests/test_cli.py — 적용 경계: apps/company-report-blog/tests/test_cli.py; 새 테스트 파일: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다. |
| 대안의 차이 | A: 기존 기능만 유지하고 이 책임을 프로그램화하지 않는다.<br>B: 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. |
| 수용·거부 조건 | B-D07-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C07-cli-skill-K01: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과 → 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 사용자 수동 실행; 이번은 PREPARE까지 |
| 이번 판단 | 수동 실행 CLI와 thin skill의 책임·재사용 경계를 어떤 책임 경계로 구성할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D07 정본과 상세 근거](decisions/07-b-d07.json)

### 작성자 평가 입력 위치

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 작성자 평가 입력 위치 |
| 현재 입력 문제 | 저장/권한 경계는 준비했으나 입력값 또는 공개 정책은 미결이다. |
| 수정 후 동작 | 로컬 의견 정본 + CLI evaluate (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: 로컬 의견 정본 + CLI evaluate (권장)<br>B: Blogger 편집기 + 명시적 fetch/import; 외부 편집 충돌 해결 필요 |
| 수용·거부 조건 | 설명 미등록 |
| 확인 방법 | 선택값의 실제 권한/소유 범위를 확인 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 구현 exact 승인 또는 외부 연결 전 |
| 이번 판단 | 작성자 의견은 로컬 Markdown/JSON을 편집해 CLI로 반영할 것인가, Blogger 편집기에서 수정한 내용을 명시 import할 것인가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[B-D08 정본과 상세 근거](decisions/08-b-d08.json)

### 실행 시 공개·갱신 정책

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 실행 시 공개·갱신 정책 |
| 현재 입력 문제 | 2026-10-14 사용자가 초안 기본·명시 공개/갱신 정책을 승인했다. |
| 수정 후 동작 | 초안 기본, 공개와 공개 글 갱신은 명시 실행 |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | apps/company-report-blog/src/report_blog/cli.py — 새 앱 CLI가 typed CollectionSpec으로 collectors를 호출하고 기존 CIL CLI의 ingest/분석을 연결한다. 기존 CIL 23개 명령·Korean help/guide 파일은 수정하지 않는다. 일반 실행은 preview/초안만 생성한다. publish 및 이미 공개된 글의 content/labels 변경은 대상 report revision과 post ID에 대한 명시 mode/실행 허용이 없으면 거부한다. OAuth blogger scope와 정책 승인을 개별 게시 허가로 대체하지 않는다. |
| 대안의 차이 | A: 초안/preview; publish는 별도 명시 승인 (권장)<br>B: 검토된 revision 승인 후 기존 공개 글도 갱신 |
| 수용·거부 조건 | B-D09-O01: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | B-C07-cli-skill-K01: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과 → 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과 |
| 확인 한계 | 준비 완료 · 승인 미확인 · 미실행 · 미실행·미확인 · 운영: 미관측 · 사람 판단: 미관측 |
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 실행 범위 | 구현 exact 승인 또는 외부 연결 전 |
| 이번 판단 | 실행은 항상 초안/preview까지만 할 것인가, 검토된 새 revision에 한해 기존 공개 글도 갱신할 것인가? |
| 조건별 다음 행동 | CHECK_BINDINGS — 현재 구현·검사 증거를 다시 결속합니다. |

[B-D09 정본과 상세 근거](decisions/09-b-d09.json)

### 첫 coverage 및 소유 블로그 연결

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | 첫 coverage 및 소유 블로그 연결 |
| 현재 입력 문제 | 저장/권한 경계는 준비했으나 입력값 또는 공개 정책은 미결이다. |
| 수정 후 동작 | 한국부터 산업을 선택하고 블로그 URL/권한은 안전한 OAuth로 별도 연결 (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: 한국부터 산업을 선택하고 블로그 URL/권한은 안전한 OAuth로 별도 연결 (권장)<br>B: 한국·미국·체코 복수 coverage; SEC 연락처/BEA 활성화 포함 외부 전제 확인 |
| 수용·거부 조건 | 설명 미등록 |
| 확인 방법 | 선택값의 실제 권한/소유 범위를 확인 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 구현 exact 승인 또는 외부 연결 전 |
| 이번 판단 | 첫 조사 국가·산업·보고기간과 소유 Blogger URL은 무엇이며 Search Console/AdSense를 연결할 계정이 준비되어 있는가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[B-D10 정본과 상세 근거](decisions/10-b-d10.json)

## 캠페인 요약

| 항목 | 값 |
|---|---|
| 현재 실행 범위 | 현재 구현·검사 증거 재결속 필요; 과거 통과를 현재 완료로 사용하지 않습니다. |
| 작성 당시 목적·범위 | 산업별 네 독자 관점 Blogger 보고서·작성자 평가 분리 및 CIL API coverage 보강을 PREPARE하고 미결 질문만 인계 |
| 캠페인 단계 | decision-required |
| 현재 검증 | 미완료·상세 상태 확인 |

## 의사결정 요약

| No | 작업 단위 | 상태 | 결정 이름 | 권장안 | 선행 결정 | 사용자 결정 |
|---:|---|---|---|---|---|---|
| 1 | B-C01-taxonomy | accepted | 산업별 목차와 단일 보고서의 네 독자 관점 | B | — | ACCEPT |
| 2 | B-C02-report-opinions | accepted | 원천·계산·AI 해석·작성자 평가의 별도 revision | B | B-D01 | ACCEPT |
| 3 | B-C03-cil-coverage | accepted | 기존 CIL parameterized 수집·재무·채용·인력·거시 경로 보강 | B | — | ACCEPT |
| 4 | B-C04-blogger | accepted | 공식 SDK 기반 작은 Blogger 게시 adapter | B | B-D01<br>B-D02<br>B-D05 | ACCEPT |
| 5 | B-C05-ledger-links | accepted | 게시 장부·분석 교차링크·실행 실패 복구 | B | B-D02 | ACCEPT |
| 6 | B-C06-metrics | accepted | 소유 블로그의 유입·관측 수익과 사용자 판단 분리 | B | B-D05 | ACCEPT |
| 7 | B-C07-cli-skill | accepted | 수동 실행 CLI와 thin skill의 책임·재사용 경계 | B | B-D01<br>B-D02<br>B-D03<br>B-D04<br>B-D05<br>B-D06 | ACCEPT |
| 8 | discussion-B-D08 | decision-required | 작성자 평가 입력 위치 | A | — | — |
| 9 | discussion-B-D09 | accepted | 실행 시 공개·갱신 정책 | A | — | ACCEPT |
| 10 | discussion-B-D10 | decision-required | 첫 coverage 및 소유 블로그 연결 | A | — | — |

## 작업 단위별 검증 상태

| 작업 단위 | 현재 상태 | 이유 |
|---|---|---|
| B-C01-taxonomy | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C02-report-opinions | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C03-cil-coverage | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C04-blogger | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C05-ledger-links | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C06-metrics | 계획됨 · 구현 미실행 | result-reference-incomplete |
| B-C07-cli-skill | 계획됨 · 구현 미실행 | result-reference-incomplete |

## 검증 실패 조건과 실제 해석

| 실패 코드 | 실패 배치 / 표시된 TU | 검증기가 거부하는 정확한 조건 | 실제 확인과 해석 |
|---|---|---|---|
| — | 관측 자료 없음 | 조건 설명 미등록 | 실패가 없다는 뜻이 아님 |

> 배치 실패로 표시된 TU 수는 각 TU의 독립 오류 수가 아닐 수 있습니다.
> 관측 범위·근거의 신선도를 확인하며, 자료 미등록은 실패 0건을 뜻하지 않습니다.

## Plan·결정별 변경 책임과 완료 경계

| Plan / 결정 | 해결하려는 문제·목표 | 연결된 컴포넌트와 책임 | 현재 프로젝트 동작 변화 | 파일 수 | 의미적 완료 여부 |
|---|---|---|---|---:|---|
| B-C01-taxonomy-plan-r1 / B-D01 | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/src/report_blog/taxonomy.py; 명시 sector parent/order와 네 audience를 유지하고 slug collision/분류 미등록을 검사; 목차는 report_id로 연결<br>적용 경계: apps/company-report-blog/schemas/taxonomy.schema.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다.<br>적용 경계: apps/company-report-blog/config/taxonomy.json; 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다.<br>적용 경계: apps/company-report-blog/tests/test_taxonomy.py; 새 테스트 파일: 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report_id의 중복 방지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C01-taxonomy-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 4 | 오래됨 — 의미적 완료 미확인 |
| B-C02-report-opinions-plan-r1 / B-D02 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/src/report_blog/models.py; 원천/계산/AI/사용자 schema를 독립 타입으로 검사하고 네 perspective 및 claim별 evidence 요구<br>적용 경계: apps/company-report-blog/src/report_blog/opinions.py; 사용자만 opinion을 쓰며 visibility와 based_on revision을 저장; AI 재생성 시 원문을 그대로 보존<br>적용 경계: apps/company-report-blog/src/report_blog/compose.py; CIL structured 결과와 AI claim을 결합하되 근거 없는 숫자/빈 시계열은 검증 실패 또는 명시 한계<br>적용 경계: apps/company-report-blog/src/report_blog/render.py; Jinja escape/StrictUndefined와 URL scheme allowlist; 네 섹션과 사실/AI/사람 앵커를 한 HTML에 출력<br>적용 경계: apps/company-report-blog/templates/report.html; 원천/계산 근거, 네 AI 관점, 사용자 의견, 관련 분석 목차를 한 페이지에 분리; private 평가 제외<br>적용 경계: apps/company-report-blog/schemas/report.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다.<br>적용 경계: apps/company-report-blog/schemas/human-evaluation.schema.json; AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다.<br>적용 경계: apps/company-report-blog/tests/test_report_contracts.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>적용 경계: apps/company-report-blog/tests/test_human_preservation.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>적용 경계: apps/company-report-blog/tests/test_render.py; 새 테스트 파일: 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C02-report-opinions-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 10 | 오래됨 — 의미적 완료 미확인 |
| B-C03-cil-coverage-plan-r3 / B-D03 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: src/company_intel/connectors/collectors.py; allowlist URL·entity/date/page·read-only collector와 원문 provenance; arbitrary URL/SSRF·키 노출·무한 pagination 금지<br>적용 경계: src/company_intel/connectors/keyed.py; 기존 probe 기본 의미 유지; 동적 FRED series id와 BEA 관측/catalog 분리; DART 직원 공시 typed 정규화<br>적용 경계: src/company_intel/connectors/keyless.py; SEC concept/기간/단위별 전체 필요한 행 및 filing history; Eurostat dimension/category mapping; 기존 표본 probe 유지<br>적용 경계: src/company_intel/normalization.py; financial concept/account/statement/currency와 직원 공시/공고/거시 observation class 분리; 같은 comparable signature에서만 계산<br>적용 경계: config/providers.json; 신규 수집 4 operation과 기존8증강의 source mapping·권리·키 전제를 별도 등록; IMF 재승격 금지<br>적용 경계: tests/test_parameterized_collection.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>적용 경계: tests/test_blog_source_mapping.py; 새 테스트 파일: 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C03-cil-coverage-r3.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 7 | 오래됨 — 의미적 완료 미확인 |
| B-C04-blogger-plan-r1 / B-D04 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/src/report_blog/blogger.py; 소유 계정 blog 해소·list/get/draft insert/patch/publish; dry-run/명시 mode, 불확실 응답 대조 및 외부 편집 충돌 차단<br>적용 경계: apps/company-report-blog/src/report_blog/google_auth.py; 사용자 OAuth 파일 외부 secret reference; scope별 서비스·refresh·30s transport; key나 token 출력 금지<br>적용 경계: apps/company-report-blog/config/provider-contracts.json; Google7+성과4의 호출형식·secret ref·scope·read/write·retry/쿼터/권리/exit 경계를 분리<br>적용 경계: apps/company-report-blog/tests/test_blogger_adapter.py; 새 테스트 파일: isDraft=True 명시, 같은 content_key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C04-blogger-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 4 | 오래됨 — 의미적 완료 미확인 |
| B-C05-ledger-links-plan-r1 / B-D05 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/src/report_blog/ledger.py; SQLite transactional outbox·single writer·stable content_key·append revision; network와 DB의 비원자성 복구<br>적용 경계: apps/company-report-blog/src/report_blog/links.py; 명시 이유/관계의 typed 연결; 산업/직종/기업/시점/반박 글의 안정 ID 및 missing URL 상태; 자동 인과 추정 금지<br>적용 경계: apps/company-report-blog/migrations/001.sql; report/revision/evaluation/relation/publication_attempt 테이블과 고유 content_key 제약; 고객/키 데이터 저장 금지<br>적용 경계: apps/company-report-blog/tests/test_ledger.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>적용 경계: apps/company-report-blog/tests/test_relations.py; 새 테스트 파일: 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C05-ledger-links-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 5 | 오래됨 — 의미적 완료 미확인 |
| B-C06-metrics-plan-r1 / B-D06 | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/src/report_blog/metrics.py; 계정·권한·시점·통화 및 실제 dimension coverage를 유지한 readonly 조회; unavailable/unknown와0을 구분<br>적용 경계: apps/company-report-blog/tests/test_metrics.py; 새 테스트 파일: 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C06-metrics-r1.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 2 | 오래됨 — 의미적 완료 미확인 |
| B-C07-cli-skill-plan-r3 / B-D07 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. → 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 | 적용 경계: apps/company-report-blog/pyproject.toml; 별도 앱 console entrypoint 및 SDK2.201.0/google-auth2.62.0/oauthlib1.5.0/Jinja3.1.6; CIL 루트 패키지는 변경하지 않음<br>적용 경계: apps/company-report-blog/uv.lock; 위 직접 버전과 전이 의존성 hash를 lock하고 Python3.13 resolver/local test; 설치 성공을 live 연동으로 판단하지 않음<br>적용 경계: apps/company-report-blog/src/report_blog/__init__.py; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.<br>새 앱 CLI가 typed CollectionSpec으로 collectors를 호출하고 기존 CIL CLI의 ingest/분석을 연결한다. 기존 CIL 23개 명령·Korean help/guide 파일은 수정하지 않는다. 일반 실행은 preview/초안만 생성한다. publish 및 이미 공개된 글의 content/labels 변경은 대상 report revision과 post ID에 대한 명시 mode/실행 허용이 없으면 거부한다. OAuth blogger scope와 정책 승인을 개별 게시 허가로 대체하지 않는다.<br>적용 경계: apps/company-report-blog/README.md; 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다.<br>적용 경계: apps/company-report-blog/skills/company-report-blog/SKILL.md; 네 관점 작성과 CIL 호출·의견 소유권·preview/draft/게시·metrics를 연결하는 thin skill; 기존 분석 스킬과 캠페인 권위 보존<br>적용 경계: apps/company-report-blog/skills/company-report-blog/agents/openai.yaml; 스킬 trigger/예시를 보고서 실행으로 한정하고 암묵 발동이 원격 쓰기 승인을 만들지 않도록 지침<br>적용 경계: apps/company-report-blog/tests/test_cli.py; 새 테스트 파일: 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지; 해당 그룹 변경점과 fixtures/반례를 모두 실행한다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C07-cli-skill-r3.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 8 | 오래됨 — 의미적 완료 미확인 |
| B-C07-cli-skill-plan-r3 / B-D09 | 2026-10-14 사용자가 초안 기본·명시 공개/갱신 정책을 승인했다. → 초안 기본, 공개와 공개 글 갱신은 명시 실행 | 새 앱 CLI가 typed CollectionSpec으로 collectors를 호출하고 기존 CIL CLI의 ingest/분석을 연결한다. 기존 CIL 23개 명령·Korean help/guide 파일은 수정하지 않는다. 일반 실행은 preview/초안만 생성한다. publish 및 이미 공개된 글의 content/labels 변경은 대상 report revision과 post ID에 대한 명시 mode/실행 허용이 없으면 거부한다. OAuth blogger scope와 정책 승인을 개별 게시 허가로 대체하지 않는다.<br>[모든 변경점·책임](#변경점-상세) · [정확한 경로·operation·명령](implementation-plans/B-C07-cli-skill-r3.json) | 예정·미확인: 제품 효과 미등록; UX 설명은 결정 정본에서 별도 확인 | 1 | 오래됨 — 의미적 완료 미확인 |

> 파일 수는 해당 plan·결정에 연결된 고유 변경 경로 수(테스트 포함)입니다.
> 공유 경로 때문에 행별 수를 합산하지 않습니다. 계획상 변화나 차단 기준 통과만으로 의미적 완료를 확정하지 않습니다.

## 의사결정 상세

<details>
<summary>의도·설계 근거가 필요할 때 펼치기</summary>

## 1. 산업별 목차와 단일 보고서의 네 독자 관점 (`B-D01`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 한 블로그의 산업 부모/자식 구조와 네 관점 라벨; 보고서는 하나이며 관련 분석을 stable ID로 연결한다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 4개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 고정된 네 관점, 순서/부모 보존, native 폴더 오인 방지, 미분류 유지와 같은 report_id의 중복 방지 |

## 2. 원천·계산·AI 해석·작성자 평가의 별도 revision (`B-D02`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | AI 해석과 사용자 판단을 같은 페이지에 분리하며 원천과 계산값에 출처를 결속한다. 기존 의견은 새 AI revision으로 덮어쓰지 않는다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 10개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 원천/계산/AI/사람 구별, 허위 수치 차단, 작성자 평가 bytes/revision 보존, stale 평가 표시와 XSS/URL scheme 차단 |

## 3. 기존 CIL parameterized 수집·재무·채용·인력·거시 경로 보강 (`B-D03`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 등록 28개 검증 상태와 새 수집 operation 4개, 기존 operation 증강 8개, 미확인 계약 2개를 별도 집계하고 적격 조건을 만족하는 시계열만 연결한다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 7개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 임의 회사/기간/페이지 allowlist 수집; SEC concept/기간/단위 및 DART 기존 모든 행 보존; BEA catalog와 관측 구분; 직원 공시/공고 수 구분; 1 snapshot 추이 금지 |

## 4. 공식 SDK 기반 작은 Blogger 게시 adapter (`B-D04`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | CIL 계산과 보고서 의미를 게시 SDK에서 복제하지 않고 명시적 dry-run/draft/update/publish를 분리한다. Blogger 7 operation과 OAuth 경계를 구현한다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 4개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | isDraft=True 명시, 같은 content_key의 insert 재시도 금지, 외부 편집 충돌 stop, 토큰 redaction, get/list pagination 및 테스트에서 원격 쓰기 0회 |

## 5. 게시 장부·분석 교차링크·실행 실패 복구 (`B-D05`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | SQLite 트랜잭션과 단일 writer를 사용해 보고서·AI revision·사용자 revision·원격 ID·outbox 상태를 연결하며 불확실한 게시 결과를 원격과 대조한다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 5개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 동일 입력 재실행 no-op, pending/uncertain 복구, 네 독자 목차가 동일 URL 사용, broken link 검출, 의견 revision append 및 public/private 분리 |

## 6. 소유 블로그의 유입·관측 수익과 사용자 판단 분리 (`B-D06`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | Search Console/AdSense 4 operation의 읽기 전용 접근으로 확인 가능한 성과만 집계하며 콘텐츠 품질·사용자 평가를 수익으로 대체하지 않는다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 미연동은 unknown, site/account/기간/통화별 집계, URL 매핑/부분 coverage 표시, 임의 페이지 매출 배분 금지와 readonly scope |

## 7. 수동 실행 CLI와 thin skill의 책임·재사용 경계 (`B-D07`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 사용자가 실행할 때 기존 CIL→보고서 구성기→게시 adapter→장부→성과 조회를 연결한다. AI 의미 작성은 현재 대화 모델이 맡고 도구는 검사/집계/갱신을 맡는다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 사용자 명시 목적에 맞춘 PREPARE 설계 선택; 실행 승인으로 사용 금지 |
| 수정할 코드 경계 | 목표 경로 8개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — typed evidence/revision/CLI와 최소 adapter를 연결 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 기존 23개 CIL CLI 유지, 새 CLI 안정 JSON/preview, 네 관점 typed 입력, 명시 실행만 원격 쓰기, 예약/유료 AI/캠페인 권한 자동 확대 금지 |

## 8. 작성자 평가 입력 위치 (`B-D08`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 저장/권한 경계는 준비했으나 입력값 또는 공개 정책은 미결이다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 로컬 의견 정본 + CLI evaluate (권장) |
| 수정할 코드 경계 | 요약 검토 필요 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 선택값의 실제 권한/소유 범위를 확인 |
| 미결 선택 | A: 로컬 의견 정본 + CLI evaluate (권장); B: Blogger 편집기 + 명시적 fetch/import; 외부 편집 충돌 해결 필요 |

## 9. 실행 시 공개·갱신 정책 (`B-D09`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 2026-10-14 사용자가 초안 기본·명시 공개/갱신 정책을 승인했다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 초안 기본, 공개와 공개 글 갱신은 명시 실행 |
| 수정할 코드 경계 | 목표 경로 1개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — A/B 또는 정확한 값으로 답변 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 기본 실행·명시 승인 없음·공개 글 대상 PATCH의 반례에서 원격 공개 변경0회; 초안 isDraft=True 및 승인 revision만 통과 |

## 10. 첫 coverage 및 소유 블로그 연결 (`B-D10`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 저장/권한 경계는 준비했으나 입력값 또는 공개 정책은 미결이다. (근거: docs/decision-campaigns/2026-10-13/cil-four-perspective-blog-20261013/evidence/product-contract-ko.md) |
| 바꿀 동작 | 한국부터 산업을 선택하고 블로그 URL/권한은 안전한 OAuth로 별도 연결 (권장) |
| 수정할 코드 경계 | 요약 검토 필요 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 한 페이지에 네 시선과 AI/작성자 구역을 분리하며 목차로 탐색한다. |
| 통과를 확인할 증거 | 선택값의 실제 권한/소유 범위를 확인 |
| 미결 선택 | A: 한국부터 산업을 선택하고 블로그 URL/권한은 안전한 OAuth로 별도 연결 (권장); B: 한국·미국·체코 복수 coverage; SEC 연락처/BEA 활성화 포함 외부 전제 확인 |

</details>

## 정본과 상세 근거

- [B-D01 정본 JSON](decisions/01-b-d01.json)
- [B-D02 정본 JSON](decisions/02-b-d02.json)
- [B-D03 정본 JSON](decisions/03-b-d03.json)
- [B-D04 정본 JSON](decisions/04-b-d04.json)
- [B-D05 정본 JSON](decisions/05-b-d05.json)
- [B-D06 정본 JSON](decisions/06-b-d06.json)
- [B-D07 정본 JSON](decisions/07-b-d07.json)
- [B-D08 정본 JSON](decisions/08-b-d08.json)
- [B-D09 정본 JSON](decisions/09-b-d09.json)
- [B-D10 정본 JSON](decisions/10-b-d10.json)
- [캠페인 정본](campaign.json)


## 변경점 상세

고유 파일 40개 · operation 40개. [선언 inventory](component-inventory.json)의 모듈 컴포넌트 3개 · 미등록 경로 37개. 실제 기능 수로 추정하지 않습니다. 파일 수와 기능 수는 다릅니다.

<details>
<summary>모든 소유 변경점과 개별 책임</summary>

### B-C01-taxonomy

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C01-taxonomy-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [taxonomy.py](../../../../apps/company-report-blog/src/report_blog/taxonomy.py) | file-change-760b6123d467 | B-D01 |
| [taxonomy.schema.json](../../../../apps/company-report-blog/schemas/taxonomy.schema.json) | file-change-8a2889c1dc62 | B-D01 |
| [taxonomy.json](../../../../apps/company-report-blog/config/taxonomy.json) | file-change-0a8210721a0f | B-D01 |
| [test_taxonomy.py](../../../../apps/company-report-blog/tests/test_taxonomy.py) | file-change-aeda4c03fbdf | B-D01 |

### B-C02-report-opinions

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C02-report-opinions-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [models.py](../../../../apps/company-report-blog/src/report_blog/models.py) | file-change-c03ccdb32605 | B-D02 |
| [opinions.py](../../../../apps/company-report-blog/src/report_blog/opinions.py) | file-change-3524bc461a72 | B-D02 |
| [compose.py](../../../../apps/company-report-blog/src/report_blog/compose.py) | file-change-a633d3050cf5 | B-D02 |
| [render.py](../../../../apps/company-report-blog/src/report_blog/render.py) | file-change-f176652da040 | B-D02 |
| [report.html](../../../../apps/company-report-blog/templates/report.html) | file-change-b1b432dea9a9 | B-D02 |
| [report.schema.json](../../../../apps/company-report-blog/schemas/report.schema.json) | file-change-e6a672c902bc | B-D02 |
| [human-evaluation.schema.json](../../../../apps/company-report-blog/schemas/human-evaluation.schema.json) | file-change-4f661150db5f | B-D02 |
| [test_report_contracts.py](../../../../apps/company-report-blog/tests/test_report_contracts.py) | file-change-3d0882685c44 | B-D02 |
| [test_human_preservation.py](../../../../apps/company-report-blog/tests/test_human_preservation.py) | file-change-3f276d628902 | B-D02 |
| [test_render.py](../../../../apps/company-report-blog/tests/test_render.py) | file-change-3290aadb47d1 | B-D02 |

### B-C03-cil-coverage

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C03-cil-coverage-r3.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [collectors.py](../../../../src/company_intel/connectors/collectors.py) | file-change-2199b175807c | B-D03 |
| [keyed.py](../../../../src/company_intel/connectors/keyed.py) | file-change-927a21cab8b8 | B-D03 |
| [keyless.py](../../../../src/company_intel/connectors/keyless.py) | file-change-8925cfef251f | B-D03 |
| [normalization.py](../../../../src/company_intel/normalization.py) | file-change-58fda9542e8a | B-D03 |
| [providers.json](../../../../config/providers.json) | file-change-e1e3c60c9a87 | B-D03 |
| [test_parameterized_collection.py](../../../../tests/test_parameterized_collection.py) | file-change-18064dda30b3 | B-D03 |
| [test_blog_source_mapping.py](../../../../tests/test_blog_source_mapping.py) | file-change-705f2199a5ae | B-D03 |

### B-C04-blogger

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C04-blogger-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [blogger.py](../../../../apps/company-report-blog/src/report_blog/blogger.py) | file-change-9bd037dc0311 | B-D04 |
| [google_auth.py](../../../../apps/company-report-blog/src/report_blog/google_auth.py) | file-change-7d2de96119d5 | B-D04 |
| [provider-contracts.json](../../../../apps/company-report-blog/config/provider-contracts.json) | file-change-871e48ad3a4d | B-D04 |
| [test_blogger_adapter.py](../../../../apps/company-report-blog/tests/test_blogger_adapter.py) | file-change-76f93b28cdc1 | B-D04 |

### B-C05-ledger-links

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C05-ledger-links-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [ledger.py](../../../../apps/company-report-blog/src/report_blog/ledger.py) | file-change-9efdb1632b49 | B-D05 |
| [links.py](../../../../apps/company-report-blog/src/report_blog/links.py) | file-change-a47c5eb0c4ed | B-D05 |
| [001.sql](../../../../apps/company-report-blog/migrations/001.sql) | file-change-618b7cf82e49 | B-D05 |
| [test_ledger.py](../../../../apps/company-report-blog/tests/test_ledger.py) | file-change-7e7c210fc33d | B-D05 |
| [test_relations.py](../../../../apps/company-report-blog/tests/test_relations.py) | file-change-b630dece86b2 | B-D05 |

### B-C06-metrics

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C06-metrics-r1.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [metrics.py](../../../../apps/company-report-blog/src/report_blog/metrics.py) | file-change-475e37c19be1 | B-D06 |
| [test_metrics.py](../../../../apps/company-report-blog/tests/test_metrics.py) | file-change-d88831450f77 | B-D06 |

### B-C07-cli-skill

[개별 책임·바꿀 동작·의무의 정본](implementation-plans/B-C07-cli-skill-r3.json) — 아래 operation ID로 조회합니다. 긴 설명을 여기 다시 복사하지 않습니다.

| 변경 파일 | operation | 기여 결정 |
|---|---|---|
| [pyproject.toml](../../../../apps/company-report-blog/pyproject.toml) | file-change-6da0dec88ca8 | B-D07 |
| [uv.lock](../../../../apps/company-report-blog/uv.lock) | file-change-269781ae6688 | B-D07 |
| [__init__.py](../../../../apps/company-report-blog/src/report_blog/__init__.py) | file-change-57c5036c11db | B-D07 |
| [cli.py](../../../../apps/company-report-blog/src/report_blog/cli.py) | file-change-0fa8857c54f3 | B-D07<br>B-D09 |
| [README.md](../../../../apps/company-report-blog/README.md) | file-change-3d21764f4086 | B-D07 |
| [SKILL.md](../../../../apps/company-report-blog/skills/company-report-blog/SKILL.md) | file-change-335b547b9414 | B-D07 |
| [openai.yaml](../../../../apps/company-report-blog/skills/company-report-blog/agents/openai.yaml) | file-change-c8824f26de4b | B-D07 |
| [test_cli.py](../../../../apps/company-report-blog/tests/test_cli.py) | file-change-f292f33ffbc7 | B-D07 |

</details>
