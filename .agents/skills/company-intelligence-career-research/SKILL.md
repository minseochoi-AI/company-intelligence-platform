---
name: company-intelligence-career-research
description: 미국·한국·체코의 기업·직무 요건·자격증·준비사항을 근거 기반으로 조사한다. Company Intelligence Platform의 기업 검색·스프레드시트 요청에 사용하며, 입사 지원이나 투자 조언에는 사용하지 않는다.
---

# Company Intelligence Career Research

이 스킬은 Company Intelligence Platform 체크아웃에서 근거 기반 기업·커리어
조사를 수행할 때 사용한다. 산출물은 검토 가능한 데이터 제품이며, 특정 기업이
실제 채용 중이라는 주장, 자격증이 입사 자격을 보장한다는 주장, 경제 상관관계가
인과라는 주장을 만들지 않는다.

## 활성 의사결정 캠페인부터 확인

1. 저장소 루트를 확인한 뒤 `docs/decision-campaigns/index.json`, 활성
   `campaign.json`, `scope-lock.json`을 먼저 읽고 넓은 코드·공급자 조사를 시작한다.
2. 캠페인의 현재 action과 승인된 plan을 따른다. `decision-required` 상태에서는
   분석과 제안만 가능하며, 코드 변경·공급자 호출·스프레드시트 외부 배포·통합 완료
   주장을 허용하지 않는다.
3. 원천 검증일이 없거나 오래됐으면 한계로 표시한다. 약관, 쿼터, 등록, 추출 권한이
   바뀔 수 있는 endpoint는 활성화 전에 현재 공식 문서를 재검증한다.

## 검색 프로필을 먼저 확보

기업을 순위화하거나 반환하기 전에 대상 국가와 국가별 후보 배분, 직무 또는 직업,
현지 직무명↔직업 코드 매핑 기준, 산업, 경력 수준, 언어, 취업 자격 제약, 선호
지역·근무 방식, 후보 수, 요청 갱신일, 자격요건 증거 범위(공고별·국가 기준·둘 다)를
포함한 프로필을 확보하거나 찾는다. 기업명으로 개인의 자격·체류 상태·경력 선호를
추정하지 않는다.

중요한 항목이 없으면 원천과 스키마 근거만 준비하고, 적합한 기업이나 자격증을
만들어 내지 말고 해당 항목을 요청한다.

## 데이터 가능성과 결론을 분리

모든 기업-원천 연결에는 원천명, 원천 레코드 ID, URL, 수집 시각, 라이선스·출처
표시 상태, 매칭 신뢰도, 분류 근거를 기록한다. 다음은 독립 필드로 유지한다.

- `company_financial_disclosure`, `workforce_disclosure`,
  `job_posting_requirements`, `market_data`, `macro_series`
- `identity_resolved`, `identity_unresolved`
- `correlation_candidate`, `correlation_ineligible`,
  `causal_analysis_ineligible`

채용공고는 모집 수요이지 실제 채용·퇴직이 아니다. 집계 고용·거시 시계열은
맥락이지 기업별 고용·재무 사실이 아니다. 법인 연결, 기간 범위, 산업·지역 매핑,
point-in-time 가용성이 모두 근거로 확인된 경우에만
`correlation_candidate`를 표시하고, 이를 인과 증거로 표현하지 않는다.

## 직무 요건은 보수적으로 검증

직무별 요건에는 고용주의 현재 공고를 우선하고, 법정·직업 자격에는 관할 공식
규제기관 또는 국가 자격 원천을 우선한다. 정확한 URL, 확인일, 근거 문구 또는
구조화 필드, 국가, 직업 코드, `required`·`preferred`·`unknown` 상태를 보존한다.

고용주의 우대사항을 법정 요건으로 바꾸지 않는다. 직무명만으로 자격증을 추정하지
않으며, 직업 코드 crosswalk만으로 국가 간 자격 동등성을 선언하지 않는다. 현지
직무명과 코드의 매핑 근거도 보존한다. 검증하지 못한 요건은 숨기지 말고 미해결
상태로 남긴다.

## 1. 사전 기준 설명문 선행 출력 프로토콜 (Pre-flight Baseline Disclosure: 필수 1단계)

조사 착수 또는 사용자 질의 응답 전, 일방적인 설문지를 전개하지 않고 **현재 시스템에 연결된 28대 API 사양, 142개 원천 속성 풀, 21,000개 이론적 클러스터 좌표 공간을 명시한 고정 설명문**을 가장 먼저 출력하여 시스템 경계를 브리핑한다.

- **CLI 실행**: `company-intel cluster-spec` 또는 `company-intel 클러스터-사양-안내`
- **JSON 사양 추출**: `company-intel cluster-spec --json-output`

### 28대 연결 API 및 142개 원천 속성 카탈로그
- **한국 (KR: 6)**: ALIO(경영공시/채용), WorkNet(통합고용), OpenDART(기업공시/임원), HRDKorea(NCS 역량단위), ECOS(한국은행 거시), MPM(국가공무원채용)
- **체코 (CZ: 3)**: ARES(경제주체등록원·법인형태), MPSV(통합구인포털), CNB(체코국립은행 환율/금리)
- **슬로바키아 (SK: 3)**: ÚPSVaR(고용포털), RPO(법인등록원), SAV(국립과학원 연구기관)
- **미국 (US: 6)**: SEC EDGAR(공시/XBRL), USAspending(연방조달계약), USAJobs(연방채용), BLS(노동통계), FRED(세인트루이스연은), BEA(경제분석국)
- **글로벌/EU (10)**: GLEIF(LEI), TED(EU공공조달), Greenhouse, Lever, GitHub, OpenAlex, Eurostat, ECB, OECD, WorldBank

---

## 2. API 호출 결과 자체의 AI 개입 절대 배제 (Zero AI Mutation)

1. API가 반환한 원천 페이로드(Raw JSON/XML)의 파싱, 키 매핑, 타입 변환, 유효성 검증은 **100% 결정론적 코드([`JobSchemaContract`](file:///home/ubuntu/root/company-intelligence-platform/src/company_intel/classification.py#L452) 및 [`DynamicJobSchemaRegistry`](file:///home/ubuntu/root/company-intelligence-platform/src/company_intel/classification.py#L346))**로만 실행한다.
2. LLM(AI 어시스턴트)이 임의로 원천 필드 값을 마사지, 축약, 추정, 가공하여 엑셀 셀이나 데이터셋에 삽입하는 행위를 원천 차단한다.
3. 누락되거나 불일치하는 키는 `KeyAlignmentError`를 발생시켜 정규화 매핑 테이블에서 사전에 방어한다.

---

## 3. 3-계층 동적 보고서 컴파일러 (Dynamic Report Schema Compiler)

고정된 30열 템플릿에 구애받지 않고, 사용자가 지정한 시그니처와 활성화된 API의 속성 집합에 따라 엑셀 열(Columns) 및 시트(Tabs) 스키마를 동적으로 컴파일한다.

1. **Core Layer (고정 8열)**:
   - 순번(No), 국가(Country), 기관/기업명(Employer Name), 사업자번호(IČO/Org ID), 공고 식별자(Job ID), 공식 직무명(Job Title), 직무코드(Job Code), 클러스터 시그니처(Cluster Signature)
2. **Dynamic Attribute Layer (가변 N열)**:
   - 활성화된 API의 특화 속성: ARES `pravniForma`, USAspending `Award Amount`, SEC `Assets USD`, 근로시간, 최소학력 등
3. **Action & Provenance Layer (고정 7열)**:
   - 원천 공고 URL(Posting URL), 클릭 가능한 공고 바로가기(`=HYPERLINK(col_letter{row}, "공고 확인 ↗")`), 실시간 신선도(`LIVE_ACTIVE`, `CLOSED`), 접수 마감일, 원천 API 명칭, 무결성 검증, 검증 메모
   - **동적 하이퍼링크 계산**: 동적 속성이 N개 추가되더라도, 수식은 정확하게 원천 URL 열 문자를 자동 계산하여 바인딩한다.

---

## 4. 조건부 래티스 인터뷰 엔진 (Conditional Lattice Grill-Me)

고정된 선형 설문지를 완전히 배제하고, 사용자가 입력한 클러스터 시그니처(`ClusterSignature`)의 래티스 좌표 상태에 따라 미결정 차원(`ALL`)과 활성 공급자에 대해서만 역으로 질문을 분기한다.

- `CZ:STATE_OWNED:ALL:ALL:ALL` 진입 시:
  - 활성화 공급자: ARES, MPSV, CNB
  - 미결정 차원: 티어(`CZ_STATNI_PODNIK` vs `CZ_PRISPEVKOVA_ORG`), 고용형태, 근무형태
  - 질문: 지역을 프라하(`CZ0100`)로 한정하는지, 정규직(`REGULAR`)만 보는지, 학사/석박사 코호트 분리가 필요한지만 질문.
- `US:PUBLIC_INSTITUTION:FEDERAL_GS:REGULAR:ONSITE` 진입 시:
  - 미결정 차원 없음(`is_micro_cohort=True`). 추가 질문 없이 즉시 동적 엑셀 및 감사 영수증 파일 추출.

---

## 5. 안전과 권한

이 데이터 제품은 근거 기반 기업·공고 조사 결과일 뿐 입사 지원, 채용 결과, 비자·체류
자격, 자격증 취득의 필요성이나 합격을 보장하는 개인화 조언이 아니다.

API 키, 구직자 개인정보, 자격증 원본, 비밀이 섞인 공급자 응답을 source control,
스프레드시트, 로그, 캠페인 산출물에 복사하지 않는다. 유료·등록 필요·약관 제한
공급자는 접근과 출력 권한이 명시적으로 승인될 때까지 사용하지 않는다. 자동 추출을
금지하는 원천을 스크레이핑하지 않는다. 저장소 구현은 승인된 캠페인 plan과 검증
기준에 계속 묶여 있어야 한다.
