# CIL → 네 관점 Blogger 분석지: PREPARE 정본

확인일: 2026-10-13. 소유 저장소: `/home/ubuntu/root/company-intelligence-platform`.
이번 승인된 작업은 조사·계획·PREPARE까지다. 구현, OAuth 등록, 글 공개, Git 실행은 하지 않는다.

## 고정 목적과 이번 요청의 증강

한 블로그에서 **산업 → 기업·직종·시장 질문 → 시점별 보고서**를 탐색한다. 같은 근거를 취준생·기업 분석 컨설턴트·주식시장 분석가·창업 니즈 발굴자라는 네 시선으로 설명한다. 글을 네 번 복제하지 않고 보고서 하나 안에 네 영역을 두며 독자·산업별 목차에서 같은 report_id로 연결한다.

| 독자 | 독자의 구체적인 질문 | CIL 연결 | 보고서가 제공할 결과 | 금지하는 대체 주장 |
|---|---|---|---|---|
| 취준생 | 이 산업·직종의 실제 공고는 무엇을 필수/우대로 요구하며 같은 조건의 수요가 어떻게 변하는가 | company-search, current-jobs, job-search, job-trends | 현재 확인 공고·요건 인용·직종 매핑·시점별 공고 증감·지원 조건의 미확인점 | 공고 수를 실제 채용 인원·미래 취업 보장으로 표현 |
| 분석 컨설턴트 | 어떤 기업의 사업·재무·인력 구조가 비교군과 달라졌고 근거는 무엇인가 | analyze-actual, timeline, explain, export | 사업/법인 식별·동일 회계 concept/기간/통화 재무 비교·공시 직원수·근거표 | 산업 고용 통계를 특정 기업의 직원수로 대체 |
| 주식시장 분석가 | 재무 변화와 금리·환율·경기 변화의 관계 및 시나리오 가정은 무엇인가 | analyze-actual, valuation, ai-event, timeline | 과거 가용 시점에 맞춘 계산·상관 후보·가정별 시나리오·반대 근거 | 상관을 인과로 확정, 현재 자산만으로 현금흐름/투자가치 확정 |
| 창업 니즈 발굴자 | 어느 업무에 실제 구매사건이 있으며 내가 공급자가 될 조건은 무엇인가 | CIL 기업/계약/공시 evidence + 기존 창업 스킬 | 사용자/구매자/지불자·경쟁/대체재·구매 근거·공급 자격·데이터 권리·반증 조건 | 정부지원금/정책 전망을 매출·수주 가능성으로 대체 |

기존 career 스킬은 투자 조언을 제공하지 않는다. 주식시장 섹션은 별도 보고서 정책이 소유하고 기존 스킬의 안전·요건 검증 경계를 바꾸지 않는다. 기존 창업 스킬은 기회 판단을, CIL은 계산/수집을, DCW는 구현 승인을 계속 소유한다.

## 폴더와 연결 구조

Blogger v3의 Posts에는 `labels[]`와 `content`가 있고 native nested-folder 리소스는 없다. 로컬 taxonomy 정본은 부모·자식 구조를 가지며 원격은 라벨과 산업별 목차 글로 투영한다. 블로그 테마 변경은 이번 범위 밖이다. 자동 생성은 실제 게시 실행을 승인한 다음 수행된다.

```text
분석 블로그
├── 산업별 목차
│   └── sector_id/산업명
│       ├── 취업·요구 역량·공고 추이 → canonical report URL#career
│       ├── 기업·재무·공시 인력 → URL#company
│       ├── 거시변수·시장 시나리오 → URL#market
│       └── 구매 니즈·공급 진입조건 → URL#venture
└── 같은 보고서 본문
    ├── 원천 사실·계산값·범위·확인일
    ├── AI 해석: 네 관점, 주장별 근거, 한계
    ├── 작성자 평가: 동의/반대/추가 가설/판단 유보
    └── 연결 분석: 같은 기업·직종·산업·이전 시점·반박 보고서
```

폴더 생성·행 수·목차·교차링크·현재 상태는 도구가 처리한다. 산업/직종 의미 매핑, 새로운 주제 선택, 인과 해석, 사용자 의견은 모델 또는 사람이 명시적으로 등록한다. 미분류는 미분류로 남긴다. 산업 표준 코드와 임의 사업 테마는 별도 ID이며 crosswalk에는 근거·버전·신뢰도·미확인 상태가 필요하다.

## 공개 페이지와 비공개 정본

| 객체 | 핵심 필드 | 쓰기 소유자 | 공개 경계 |
|---|---|---|---|
| ArticleSpec | report_id, question, sector_ids, company_ids, occupation_ids, jurisdictions, period, perspectives[4] | 작성자/현재 대화 모델 | 질문·범위 공개 |
| EvidenceRef / ComputedFact | source_record_id, source_url, as_of, collected_at, available_at, revision_at, concept, unit, currency, formula, input_refs, rights_status | 원천/결정론적 계산 | 검토된 값·출처만 공개; raw/키/개인자료 제외 |
| AIReportRevision | revision_id, evidence_bundle_sha256, claims[], perspective_id, evidence_refs, interpretation, uncertainty, generated_at, model_label | 모델 | 검토한 해석만 공개; 모델 버전 모르면 unknown |
| HumanEvaluationRevision | evaluation_id, author, text, verdict, targets[], based_on_ai_revision, based_on_evidence_sha256, visibility, supersedes, created_at | 사용자만 | public만 공개; AI는 수정·작성자 사칭 금지 |
| ReportRelation | from_report_id, to_report_id, relation_type, reason, evidence_ref, registered_by | 명시 등록 | source/previous_revision/disagrees_with/related_analysis 등; 자동 인과 추정 금지 |
| PublicationLedger | report_id, content_key, blog_id, post_id, url, ai_revision, human_revision, content_hash, remote_hash, request_id, state | 게시 adapter | 내부 식별/인증 자료 비공개 |
| AudienceObservation | property/account, period, timezone, dimensions, clicks, impressions, revenue, currency, mapping_status, completeness | 읽기 전용 metrics | 수익 공개 여부는 사용자가 선택; 미연동=unknown |

사용자 의견은 생성 입력과 별도 파일/테이블에 저장한다. AI revision이 바뀌어도 사용자가 검토했던 이전 revision과 의견을 보존하며 `review_outdated=true`로 표시한다. 인용된 의견은 사실 근거를 대신하지 않는다. AI 내용과 의견이 충돌하면 함께 표시하고 임의 합의로 바꾸지 않는다.

## 작업 단계와 CLI 삽입점

1. ArticleSpec의 질문·산업·기업·직종·기간·네 관점을 등록한다.
2. coverage에서 원천 미제공/미수집/미정규화/미적재/미노출/권리 미확인/오류를 구분한다.
3. 기존 CIL 명령과 새 parameterized collector로 필요한 근거를 수집·snapshot 적재한다. 실시간 원천 호출은 실행 시별 허용·쿼터·키 gate를 적용한다.
4. 같은 coverage/taxonomy/기간/단위/통화 조건에서 재무·공고·공시 인력·거시 관계를 계산한다. 비교 불가와 부족한 과거치는 숨기지 않는다.
5. 현재 대화 모델이 네 관점의 AI 해석을 evidence-bound JSON으로 작성한다. 별도 유료 모델이나 예약 실행은 기본 의존성으로 추가하지 않는다.
6. 사용자가 의견을 별도 revision으로 등록한다. 의견 입력 UI는 B-D08 논의 대상이나 저장/소유권은 고정이다.
7. render/validate가 출처, 계산, 네 섹션, 작성자 의견, 광고형 공개권, 링크, HTML 안전성을 검사한다.
8. publish preview → 승인된 mode로 draft/create/update → pending/success/uncertain 장부 → 원격 재조회로 대조한다.
9. 산업별 목차와 네 독자 관점 라벨을 같은 글에 연결한다. 같은 입력/같은 report_id면 새 글을 만들지 않는다.
10. 성과 조회는 별도 OAuth scope/계정으로 실행한다. 트래픽·수익은 기술 구현 성공 및 사용자 동의 평가와 분리한다.

예정 CLI는 `report-blog inspect/collect/compose/render/evaluate/link/preview/sync/reconcile/metrics`다. CIL의 기존 명령은 유지한다. `compose`는 외부 AI 자동 호출이 아니라 현재 모델이 만든 typed 파일을 검사/적재하며 수치 계산은 CIL이 소유한다. `sync` 기본은 dry-run이고 원격 쓰기는 명시 mode와 실행 허용이 필요하다. 인증키는 CLI 출력·캠페인·게시물에 넣지 않는다.

## 누락 개수의 분모

직전 실행 정본: 기존 등록 remote operation **28**, 최소 필드 통과 **24**, 실패 **1(BEA)**, 미실행 **3(SEC 2, 제외된 IMF 1)**. 이는 모든 원격 기능 개수도, 새로 수리할 endpoint 4개도 아니다.

이번 Blogger 연결의 유한 구현 목표: 새 operation **15개** = 수집 4개(BEA GetData, DART 직원 현황, Greenhouse 상세, Lever 상세) + Blogger 7개(blogs.listByUser/getByUrl, posts.list/get/insert/patch/publish) + 성과 4개(Search Console sites.list/searchanalytics.query, AdSense accounts.list/reports.generate). 동일 URL의 BEA method는 서로 다른 operation으로 센다. 전 세계 API 전체 개수라 주장하지 않는다.

기존 endpoint 증강 **8개** = SEC submissions/companyfacts, DART 재무, FRED, Eurostat, ECOS, Greenhouse 목록, Lever 목록. 새 endpoint 수에 합산하지 않는다. DART 모든 재무행은 이미 `_dart`에서 유지되고 있으므로 DART에 대해 SEC의 Assets-only 결손을 잘못 적용하지 않는다. 필요한 것은 비교용 concept·기간·통화·statement 매핑과 consumers 전달이다.

미해결 원천 **2개** = MPM 상세/첨부의 정확한 읽기 계약, MPSV live 다운로드 계약. 문서 미확인을 임의 endpoint로 채우지 않으며 현재 공고/첨부 검증·체코 전체 coverage 완료를 주장하지 않는다. 나라장터·NTIS·정부지원 등 추가 원천은 현 CIL에도 미등록이며 이 첫 PREPARE의 15개 신규 operation에서 제외된 후속 범위로 명시한다. 창업 관점은 현재 원천의 계약/기업 신호와 수동 EvidenceBundle로 구성하고 불충분하면 근거 부족이다.

## 데이터·운영의 필수 실패 경계

- 공고 snapshot은 관측 이후에만 존재한다. API가 제공하지 않는 과거 공고와 실제 채용 인원은 생성하지 않는다.
- 재무 회사당 연간/분기와 인력/거시 시계열의 빈도를 억지로 맞추지 않는다. macro 영향력은 분석 적격 조건과 가정이 있을 때만 설명한다.
- 무료 API 접근 성공은 광고 블로그의 상업 재배포권 증명이 아니다. unknown 권리는 링크/허용된 최소 인용 또는 비공개 초안으로 남긴다.
- Blogger content PATCH는 HTML 문자열 전체를 교체하므로 SDK가 사용자 영역을 자동 보존해주지 않는다. 로컬 human 정본에서 다시 결합하고 원격 외부 편집 hash 충돌은 stop한다. If-Match를 원격에서 보장한다고 가정하지 않으며 get→patch 사이 경합 한계가 남는다.
- insert timeout은 uncertain으로 기록하고 content_key marker/원격 목록을 대조한다. 식별 불가능하면 자동 재삽입하지 않는다. exactly-once를 보장한다고 주장하지 않는다.
- 로컬 SQLite 장부의 트랜잭션은 원격 게시와 원자적이지 않다. 단일 writer lock과 보상/reconcile, revision별 append를 사용한다.
- 페이지별 AdSense 수익은 실제 지원 dimensions/channel과 URL 매핑이 검증될 때만 제공한다. Search Console 클릭으로 수익을 임의 배분하지 않는다.
- 서버 GPU 없는 제약은 유지한다. 새로운 학습 모델·벡터 DB·상시 agent 서버·n8n·MCP 게이트웨이는 이 수동 보고서 경로에 필수 아님.

## 종속성 선택

`google-api-python-client` + 최신 google-auth 기반 사용자 OAuth, `Jinja2`, 표준 `sqlite3`를 추천한다. CIL의 DuckDB·analytics·normalization은 유지한다. MCP blogger 서버는 선택 후보였으나 기본 draft 안전성/장부/근거 검증을 대신하지 못하고 추가 Node 경로를 요구하므로 첫 경로에서 유예한다. WordPress/n8n/Activepieces는 Blogger 선택 및 수동 CLI 목적과 달라 필수 채택하지 않는다. 정확한 버전은 현재 release·Python 3.13 호환 검증 후 별도 lock으로 고정하며 DeepWiki의 mutable version 문구는 고정 버전 근거가 아니다.

공식 SDK `build()`와 Jinja `Environment` 확장점은 실제 DeepWiki structure→contents→행별 질의로 확인했다. SDK의 retry/HTML escape는 출처 검증·사용자 소유권·멱등 게시를 제공하지 않는다. 이를 자기 프로그램 테스트로 증명해야 한다. 설치/새 프로그램 테스트는 이번에 하지 않았다.

## 공식 검증 출처

- [Blogger Posts/labels](https://developers.google.com/blogger/docs/3.0/reference/posts), [draft insert](https://developers.google.com/blogger/docs/3.0/reference/posts/insert), [patch](https://developers.google.com/blogger/docs/3.0/reference/posts/patch)
- [AdSense 보고 API](https://developers.google.com/adsense/management/reference/rest/v2/accounts.reports/generate), [Search Console query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
- [DART 직원 현황](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019011), [BEA GetData 가이드](https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf)
- [Greenhouse 상세](https://docs.greenhouse.io/job-board.html), [Lever 목록/상세](https://github.com/lever/postings-api)
- [SDK DeepWiki](https://deepwiki.com/googleapis/google-api-python-client), [Jinja DeepWiki](https://deepwiki.com/pallets/jinja)
- [SDK 행별 질의](https://deepwiki.com/search/given-matrix-i01i04-producer-v_08d14238-51c6-4a4e-aa7c-43e3fc909fee), [Jinja 행별 질의](https://deepwiki.com/search/given-i02-trusted-packaged-tem_7e339e04-97e4-429b-947c-12440d09f0d4)
