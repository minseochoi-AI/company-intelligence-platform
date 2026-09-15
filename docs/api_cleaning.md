D-06~D-10 권장안 B 승인 결속, 로컬 구현, 저장된 실제 API 반환물 기반 검증까지 완료했습니다.
캠페인 상태
Cohort	기능	Plan SHA-256	구현·검증
C-04	동료군 기업 스크리너	ad5501…33be	완료
C-05	시간축·가치·AI 사건 분석	367805…c193	완료
C-06	공고 표준화·필터·DataFrame	daba70…1f5f	완료


- 결정: 10/10 ACCEPT
- D-06~D-10 구현 권한: true
- 계획 경로: 13개, 결과 SHA 결속
- 캠페인 검증: VALID
- 캠페인 상태명: decision-approved
- 커밋·푸시·외부 지원 실행: 하지 않음
[전체 호환·기능 검증 보고서](/home/ubuntu/root/company-intelligence-platform/docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.md)
[결정 워크북](/home/ubuntu/root/company-intelligence-platform/docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/decision-workbook.md)
[구현 결과 SHA receipt](/home/ubuntu/root/company-intelligence-platform/docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/receipts/post-implementation-results-D-06-through-D-10-20260911.json)
기능 목적 10개
#	기능	구현 상태	실데이터 제한
1	국가별 기업·공고 분리	구현	US 데이터 있음, KR 표본 만료, CZ 실제 snapshot 미수집
2	기업 데이터 가용성·부적격 분류	구현	원천이 없는 속성은 unavailable
3	실제 공개 공고 확인	구현	저장된 ATS 90건 사용 가능
4	국가·직종·위치·근무형태·연봉 등 필터	구현	unknown은 하드필터 불일치
5	필수·우대 요건·자격 필터	구현	MPM 상세요건은 미검증
6	CSV/XLSX 반환	구현	DataFrame 6종 반환
7	산업·국가·규모 동료군 순위	구현	비교 가능한 기업 표본 필요
8	회사·시장·거시 시간축 비교	구현	동일 회사의 정렬된 시계열 필요
9	근거 제한 미래가치 시나리오	구현	source/time/unit/currency 필수
10	AI 사건 전후 변화 분석	구현	benchmark·control 없으면 association-only


즉, 소프트웨어 경로는 10개 모두 구현됐지만 한국·체코까지 동일 수준의 실시간 데이터 coverage가 완성됐다는 뜻은 아닙니다.
실제 반환물 검증
저장된 2026-09-11 반환물을 직접 사용했습니다.
- Greenhouse Airtable: 16건
- Lever Spotify: 74건
- MPM: 1건 표본, 전체 응답 메타데이터 58,349
- 합계: 91건
- engineer 실제 검색 결과: 49건
- 국가 부족분: CZ 1건, KR 1건
- remote + full-time + USD/year ≥ 100,000 결과: 0건
0건은 오류가 아닙니다. 실제 Greenhouse·Lever 표본에 구조화 급여 필드가 하나도 없어서, 본문에 적힌 OTE·지역별 보상 숫자를 임의 연봉으로 변환하지 않았기 때문입니다.
Greenhouse GET 공고 API는 무인증 공개이며 위치·언어·부서·office·본문을 제공하지만 급여는 선택적 구조입니다. Greenhouse 공식 문서 Lever는 country, workplaceType, commitment, 선택적 salaryRange를 구분합니다. Lever 공식 API 문서 체코 MPSV는 CZ-ISCO, IČO, 급여, 위치, 교육·언어·기술 필드를 공식 스키마로 제공합니다. MPSV 공식 스키마
생성되는 DataFrame
[핵심 검색 구현](/home/ubuntu/root/company-intelligence-platform/src/company_intel/job_search.py)은 다음 여섯 표를 반환합니다.
- companies: 국가별 기업과 일치 공고 수
- jobs: 공고·직종·위치·근무형태·급여
- requirements: skill·language·education·experience·credential
- career_overlap: 여러 공고·기업·국가에서 겹치는 요건
- exclusions: 조건별 제외 사유
- sources: 수집시각·원천·coverage·제한
지원 필터는 국가, 직무 키워드, 직종, 위치, remote/hybrid/on-site, 고용형태, 공고 언어, 산업, 기업유형, 급여 하한·상한, 통화, 급여주기, 필수·우대 요건, 활성 공고, 국가별 목표 수입니다.
급여는 currency + period + basis가 호환될 때만 비교합니다. USD/year와 CZK/month는 환율이나 연환산 가정 없이 절대 합치지 않습니다.
사용 방법
프로필 예:
{
  "countries": ["US", "KR", "CZ"],
  "job_keywords": ["data engineer"],
  "locations": ["Prague", "Seoul", "Remote"],
  "workplace_types": ["remote", "hybrid"],
  "employment_types": ["full-time"],
  "minimum_salary_floor": 100000,
  "salary_currency": "USD",
  "salary_period": "year",
  "required_requirement_terms": ["sql"],
  "preferred_requirement_terms": ["python", "aws"],
  "country_allocation": {"US": 10, "KR": 10, "CZ": 10}
}
실행:
uv run --frozen company-intel job-search \
  --profile profile.json \
  --payload greenhouse=/path/to/greenhouse.json \
  --payload lever=/path/to/lever.json \
  --payload mpm_public_employment=/path/to/mpm.json \
  --output artifacts/career-search
API도 추가했습니다.
- POST /v1/job-search
- POST /v1/company-screener
- POST /v1/company-timeline
- POST /v1/analysis/valuation-scenarios
- POST /v1/analysis/ai-event
검증 결과는 24 passed, 전체 Ruff All checks passed, git diff --check 통과, CLI 및 API route 등록 통과입니다.

  파일 27개를 편집했습니다+1,557-15변경 사항 검토실행 취소리뷰

/tmp/company-intelligence-actual-job-profile.json/tmp/company-intelligence-actual-job-profile.json+5-0
/tmp/company-intelligence-actual-salary-profile.json/tmp/company-intelligence-actual-salary-profile.json+9-0
docs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.mddocs/decision-campaigns/2026-09-11/company-intelligence-cross-region-career-preparation/atomic-api-compatibility-report-2026-09-11.md+77-0
24개 파일 더 보기




오후 7:15








구체적으로 정리된 아래 내용 이외에 문제가 되는 규격 위반 api 데이터들을 찾아서 각 제공자별로 어떻게 처리할지 검증해
D-06~D-10 권장안 B 승인 결속, 로컬 구현, 저장된 실제 API 반환물 기반 검증까지 완료했습니다.
캠페인 상태
Cohort기능Plan SHA-256구현·검증
C-04	동료군 기업 스크리너	ad5501…33be	완료
C-05	시간축·가치·AI 사건 분석	367805…c193	완료
C-06	공고 표준화·필터·DataFrame	daba70…1f5f	완료


- 결정: 10/10 ACCEPT
- D-06~D-10 구현 권한: true
- 계획 경로: 13개, 결과 SHA 결속
- 캠페인 검증: VALID
- 캠페인 상태명: decision-approved
- 커밋·푸시·외부 지원 실행: 하지 않음



기능 목적 10개
#기능구현 상태실데이터 제한
1	국가별 기업·공고 분리	구현	US 데이터 있음, KR 표본 만료, CZ 실제 snapshot 미수집
2	기업 데이터 가용성·부적격 분류	구현	원천이 없는 속성은 unavailable
3	실제 공개 공고 확인	구현	저장된 ATS 90건 사용 가능
4	국가·직종·위치·근무형태·연봉 등 필터	구현	unknown은 하드필터 불일치
5	필수·우대 요건·자격 필터	구현	MPM 상세요건은 미검증
6	CSV/XLSX 반환	구현	DataFrame 6종 반환
7	산업·국가·규모 동료군 순위	구현	비교 가능한 기업 표본 필요
8	회사·시장·거시 시간축 비교	구현	동일 회사의 정렬된 시계열 필요
9	근거 제한 미래가치 시나리오	구현	source/time/unit/currency 필수
10	AI 사건 전후 변화 분석	구현	benchmark·control 없으면 association-only


즉, 소프트웨어 경로는 10개 모두 구현됐지만 한국·체코까지 동일 수준의 실시간 데이터 coverage가 완성됐다는 뜻은 아닙니다.
실제 반환물 검증
저장된 2026-09-11 반환물을 직접 사용했습니다.
- Greenhouse Airtable: 16건
- Lever Spotify: 74건
- MPM: 1건 표본, 전체 응답 메타데이터 58,349
- 합계: 91건
- engineer 실제 검색 결과: 49건
- 국가 부족분: CZ 1건, KR 1건
- remote + full-time + USD/year ≥ 100,000 결과: 0건
0건은 오류가 아닙니다. 실제 Greenhouse·Lever 표본에 구조화 급여 필드가 하나도 없어서, 본문에 적힌 OTE·지역별 보상 숫자를 임의 연봉으로 변환하지 않았기 때문입니다.
Greenhouse GET 공고 API는 무인증 공개이며 위치·언어·부서·office·본문을 제공하지만 급여는 선택적 구조입니다.  Lever는 country, workplaceType, commitment, 선택적 salaryRange를 구분합니다.  체코 MPSV는 CZ-ISCO, IČO, 급여, 위치, 교육·언어·기술 필드를 공식 스키마로 제공합니다.
생성되는 DataFrame
은 다음 여섯 표를 반환합니다.
- companies: 국가별 기업과 일치 공고 수
- jobs: 공고·직종·위치·근무형태·급여
- requirements: skill·language·education·experience·credential
- career_overlap: 여러 공고·기업·국가에서 겹치는 요건
- exclusions: 조건별 제외 사유
- sources: 수집시각·원천·coverage·제한
지원 필터는 국가, 직무 키워드, 직종, 위치, remote/hybrid/on-site, 고용형태, 공고 언어, 산업, 기업유형, 급여 하한·상한, 통화, 급여주기, 필수·우대 요건, 활성 공고, 국가별 목표 수입니다.
급여는 currency + period + basis가 호환될 때만 비교합니다. USD/year와 CZK/month는 환율이나 연환산 가정 없이 절대 합치지 않습니다.
사용 방법
프로필 예:
{
  "countries": ["US", "KR", "CZ"],
  "job_keywords": ["data engineer"],
  "locations": ["Prague", "Seoul", "Remote"],
  "workplace_types": ["remote", "hybrid"],
  "employment_types": ["full-time"],
  "minimum_salary_floor": 100000,
  "salary_currency": "USD",
  "salary_period": "year",
  "required_requirement_terms": ["sql"],
  "preferred_requirement_terms": ["python", "aws"],
  "country_allocation": {"US": 10, "KR": 10, "CZ": 10}
}
실행:
uv run --frozen company-intel job-search \
  --profile profile.json \
  --payload greenhouse=/path/to/greenhouse.json \
  --payload lever=/path/to/lever.json \
  --payload mpm_public_employment=/path/to/mpm.json \
  --output artifacts/career-search
API도 추가했습니다.
- POST /v1/job-search
- POST /v1/company-screener
- POST /v1/company-timeline
- POST /v1/analysis/valuation-scenarios
- POST /v1/analysis/ai-event
검증 결과는 24 passed, 전체 Ruff All checks passed, git diff --check 통과, CLI 및 API route 등록 통과입니다.





더 보기

오후 7:34






15분 6초 동안 작업함



검증 결과, 문제의 핵심은 “API가 잘못된 데이터를 반환했다”기보다 현재 프로그램이 API별 의미 차이를 검사하지 않고 필드가 존재하기만 하면 통과시키는 것입니다.
28개 operation을 다시 실제 호출·저장 반환물·공식 스키마와 대조했습니다.
최종 판정
검증 항목	결과	판정
전체 등록 operation	28	전부 재검토
HTTP·최소 필드 성공	27/28	접근성만 확인
실패	1	BEA 키 비활성
catalog와 실행 probe 규격 불일치	2	IMF, World Bank
빈 필수값인데 통과	1	ALIO 기관
정규화 과정에서 데이터가 잘린 operation	14	분석 입력 사용 금지
요청 목적 국가가 실제 응답에 없음	1	OECD CLI의 CZ
현재 SEC User-Agent 정책 충족	실패	실제 연락처 대신 기본 placeholder
기존 대상 테스트	4/4 통과	의미 오류를 검출하지 못하는 false green


실제 재호출 결과는 [등록형 API 검증 결과](/tmp/cip-provider-semantic-audit-20260911/validation_results.json), 기존 무키 API는 [무키 API 검증 결과](/tmp/company-intelligence-keyless-validation-20260911/validation_results.json)에서 확인했습니다.
현재 validator는 [validation.py (line 123)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/validation.py:123)에서 MISSING 여부만 검사합니다. 따라서 null, "", 잘못된 타입, 잘못된 국가, 오래된 레코드도 통과합니다. 또한 compact()가 배열을 5개까지만 남기므로 [connectors/base.py (line 42)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/connectors/base.py:42)에서 분석용 데이터가 증거 미리보기 데이터로 축약됩니다.
채용·고용 제공자
제공자	확인된 문제	반드시 적용할 처리
ALIO Plus	기관 응답이 apbaId="", apbaNa=null, title="근로복지공단"인데 통과했습니다. PDF v1.6 기관 응답 규격에는 애초에 apbaId가 없고 apbaNa=본점명, title=지점명입니다.	apbaId 계약 삭제. apbaNa/title/apbaGb/siteUrl/adr를 후보 식별자로 보존하고 identity_unresolved로 둡니다. 시설·행사·사업·기관 a~d를 서로 다른 schema로 유지해야 합니다. 연락처 필드는 기본 export에서 제외합니다.
MPM 공공취업	성공 표본이 2008년 마감 공고입니다. 58,349는 현재 공고 수가 아니며 type01/type02도 코드값입니다.	마감일·등록일 범위와 최신 정렬을 필수화하고 active 행이 1건 이상인지 검증합니다. type02를 employment_type_raw에 넣지 말고 posting_category_code로 분리합니다. 상세 URL·요건이 없으면 위치·급여·자격조건은 계속 unavailable입니다.
체코 MPSV	실제 snapshot은 아직 저장 검증되지 않았습니다. 공식 급여 코드 TypMzdy/hod가 현재 코드에서 hour로 변환되지 않고 None이 됩니다.	TypMzdy/hod→hour, TypMzdy/mesic→month 명시적 codebook join을 사용합니다. 교육·언어·기술·직업 ID 역시 각 공식 codebook 버전과 함께 해석해야 합니다. 급여 필드명과 달리 금액은 월급 또는 시급입니다. 공식 schema, 급여 codebook
Greenhouse	16건 모두 구조화 급여가 없었습니다. 현재 수집은 목록 content=true만 호출하지만, 급여는 개별 공고 상세에 pay_transparency=true를 넣어야 반환됩니다. 더구나 공식 필드는 currency_type인데 코드는 currency를 읽고 있으며 공식 급여 구조에는 interval도 없습니다.	목록→상세 2단계 수집. currency_type, min_cents, max_cents, title, blurb를 보존합니다. 기간이 명시되지 않으면 연봉으로 추정하지 않습니다. 다중 지역 급여는 한 숫자로 합치지 않고 별도 행으로 분리합니다. Greenhouse 공식 API
Lever	74건 중 34건이 다중 위치인데 현재 primary location만 사용합니다. 서울 포함 공고 2건도 각각 SG·US로만 분류됩니다. Permanent 66건을 전부 full-time으로 잘못 변환합니다.	allLocations를 job-location 관계표로 explode합니다. country는 primary country로만 보존합니다. Permanent는 계약기간, full-time은 근로시간이므로 contract_duration과 work_time으로 분리합니다. Full Time Contractor도 두 축으로 나눠야 합니다. Lever 공식 API
Lever 요건 추출	실제 bullet 630개 중 명시적 required 234, preferred 23, 판별불가 373개였습니다. 현재는 판별불가 373개를 heading만 보고 required로 승격합니다.	명시적 must/required/minimum 근거가 없으면 unknown. “Who You Are” 제목만으로 필수요건화하지 않습니다. required/preferred/unknown 판정 근거 문장과 규칙 버전을 저장합니다.


검색 결과에 직접 발생한 오류
저장된 기존 engineer 결과 49건을 다시 검사했습니다.
문제	실제 관측	영향
직종 검색 false positive	49건 중 14건은 제목에 engineer가 없음	Product Manager, Accountant, Consultant 등이 엔지니어 결과에 포함
원인	직무명이 아니라 공고 본문 전체에서 engineer 검색	다른 엔지니어와 협업한다는 문장만 있어도 일치
Lever 다중 위치 손실	34/74건	서울·스톡홀름·런던 후보 누락
Permanent→full-time 오분류	66건	근무시간 필터가 사실과 다르게 통과
판별불가 요건의 required 승격	373개 bullet	커리어 공통요건 prevalence가 과장됨
급여 basis 미검사	코드가 currency/period만 비교	base salary와 total compensation이 같은 숫자로 비교될 수 있음
언어 의미 혼합	languages가 지원자 요구 언어가 아니라 posting language 검사	영어 공고와 영어 능력 요건을 혼동


검색 로직의 원인은 [job_search.py (line 532)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/job_search.py:532)에 있습니다. 다음과 같이 분리해야 합니다.
- title_keywords: 직종 후보 판정
- description_keywords: 본문 참고 검색
- occupation_code: 공식 직업코드 필터
- posting_languages: 공고 작성 언어
- required_languages: 지원자 언어 요건
- work_time: full-time/part-time
- contract_type: employee/contractor
- contract_duration: permanent/fixed-term/temporary
- salary_basis: base/total/OTE/hourly/unknown
- job_locations[]: 다중 근무지
- company_identity_status: resolved/unresolved/ambiguous
기업·재무·조달·활동 제공자
제공자	확인된 문제	처리 규칙
SEC	Company Facts의 첫 Assets 값은 2008년이고 최신 값은 2026년입니다. 현재 정규화는 앞 5개만 남겨 오래된 값만 보존합니다. 현재 SEC_USER_AGENT도 실제 연락처가 아닌 placeholder입니다.	전체 fact를 accn/form/filed/fy/fp/start/end/frame/unit로 explode하고 최신 filed/accession 기준으로 선택합니다. placeholder이면 호출 자체를 차단합니다. SEC API는 키가 없지만 실제 호출자 식별과 공정 접근이 필요합니다. SEC 공식 API
OpenDART	실제 229개 행 중 (statement, account_id) 중복 그룹이 16개입니다. -표준계정코드 미사용-가 여러 계정을 대표합니다. 현재 숫자는 float로 변환됩니다.	PK를 receipt+statement+account_id+account_detail+ord로 구성합니다. 비표준 account ID는 자동 합산 금지. KRW 금액은 float가 아닌 정수/Decimal로 저장합니다. status=="000"을 필수화합니다. OpenDART 오류 코드
GLEIF	Apple 고정 표본은 ACTIVE/ISSUED로 정상입니다. 하지만 이름 검색 첫 결과만 선택하면 동명이인·지점·LAPSED LEI 위험이 있습니다.	법인명+관할국가+등록번호+entity status+registration status가 맞을 때만 resolved. 나머지는 후보 집합으로 반환합니다.
ARES	실제 회사에 CZ-NACE 코드가 23개인데 normalized에는 5개만 남습니다.	IČO는 문자열로 보존하고 모든 NACE를 다대다 관계표에 유지합니다. 한 개 NACE를 기업 산업으로 임의 선택하지 않습니다.
TED	실제 total-value=9,070,992가 있지만 통화를 요청하지 않았습니다.	total-value-cur를 함께 요청하고 값·통화·notice status를 한 묶음으로 검증합니다. 정정·취소 notice도 연결합니다. TED 필드 규격
USAspending	2026 기간 필터 결과가 시작일 2013, 종료일 2016 award였습니다. 현재 기간 필터는 award 기간이 아니라 transaction/action 활동에 걸릴 수 있습니다.	사건 시점 분석에는 spending_by_transaction을 사용합니다. Award Amount, obligation, outlay를 별도 필드로 유지하고 hasNext=true이면 전 페이지 수집 전 집계를 금지합니다. 공식 endpoint 설명
GitHub	repo push는 기업의 엔지니어링 활동 proxy일 뿐 AI 도입·고용 증거가 아닙니다.	technology_activity_proxy만 허용. 법인 연결과 AI 사건 날짜는 별도 공식 증거가 있어야 합니다.
OpenAlex	기관 필터 결과는 공동저자·복수기관 논문도 포함합니다.	authorship-institution 관계를 보존하고 연구 산출 proxy로만 사용합니다. 기업 매출·채용·AI 도입 사실로 승격하지 않습니다.
Alpha Vantage	IBM 100일 raw OHLCV는 정상이나 split/dividend 미조정이고 통화·거래소가 응답에 없습니다.	adjustment=raw를 유지하고 split 구간 event study는 제외합니다. ticker→법인→CIK와 거래소·통화는 별도 근거가 필요합니다.


거시 API 제공자
제공자	확인된 문제	처리 규칙
FRED	12개월 FEDFUNDS 응답은 정상입니다. 다만 현재 vintage이므로 과거 사건 분석에 쓰면 수정된 미래정보가 섞일 수 있습니다.	realtime_start/end, units, output_type을 보존하고 사건 연구에는 당시 vintage를 요청합니다. "."는 null 처리합니다. FRED 공식 규격
BEA	HTTP 200이지만 UserId is not active로 실제 실패했습니다. 또한 현재 probe는 수치가 아닌 dataset catalog입니다.	현 credential은 unavailable. 활성화 전에는 BEA 기반 GDP/산업값을 반환하지 않습니다. 활성화 후 별도 GetData operation이 필요합니다.
BLS	실제 body는 성공이지만 validator는 status=="REQUEST_SUCCEEDED"를 검사하지 않습니다. 값은 index가 아니라 해당 series의 관측값이며 footnote가 잘립니다.	status와 message를 검사하고 series_id/year/period/value/footnote/latest/unit을 보존합니다. M13은 연평균으로 월 자료와 분리합니다. BLS 공식 응답 규격
ECOS	369개 일별 행은 정상이나 반환 CYCLE=null, 단위는 연%입니다.	요청 frequency D와 반환 frequency를 따로 기록하고 연%를 percent/year 단위로 명시합니다. null CYCLE을 임의 빈도로 보충하지 않습니다.
Eurostat	한 응답에 GDP 성장률과 1인당 GDP 성장률 두 unit 축이 들어오는데 normalized는 6개 숫자만 저장해 어느 값인지 해독할 수 없습니다.	JSON-stat의 id/size/dimension.category.index로 모든 좌표를 explode해 (geo,time,unit,na_item,freq,value,status) 행으로 만듭니다. Eurostat 공식 JSON-stat 설명
ECB	normalized observation이 숫자가 아니라 {"_type":"array","_length":5}로 대체됐습니다.	SDMX structure와 series/observation index를 함께 해독하고 환율 방향 USD per EUR을 명시합니다. compact 결과 사용 금지.
OECD	oecd_cli를 CZ로 등록했지만 실제 REF_AREA 22개에 CZE가 없습니다. 정규화 코드도 실제 data.structure 대신 data.structures를 읽어 null입니다.	이 operation에서 CZ 태그를 제거해야 합니다. OECD는 현재 CLI를 G20+Spain+5 aggregates 중심으로 제공하므로 체코 분석에는 Eurostat/체코 공식 series를 사용하거나 다른 OECD dataflow를 찾아야 합니다. OECD CLI 대상 국가
IMF	catalog는 periods를 필수로 선언하지만 runtime probe는 검사하지 않습니다. 실제 응답에는 periods가 없고 2025~2031 전망값이 실적과 섞입니다.	연도 key 자체를 period로 사용하되 WEO 발행 vintage와 actual/estimate/projection을 분리합니다. 전망과 실적을 동일 timeline에 무표시 결합하지 않습니다. IMF WEO 설명
World Bank	catalog의 0.countryiso3code는 metadata 위치라 존재할 수 없지만 runtime은 다른 경로를 검사합니다. raw 9행은 CZE/KOR/USA 각 3행인데 normalized에는 CZE 3+KOR 2만 남습니다.	catalog와 probe를 단일 schema로 결속하고 [metadata, observations]를 검증합니다. 페이지 완전성 확인 후 모든 국가 행을 보존합니다. null 값은 미관측으로 처리합니다. World Bank API pagination
CNB 환율	PHP·INR·IDR·JPY·KRW 등은 amount=100/1000인데 현재 rate만 보면 환율이 100배/1000배 틀립니다. normalized에는 첫 5개만 남아 USD·KRW도 사라집니다.	단위 환율은 CZK_per_currency_unit = rate / amount. amount, validFor, currency를 필수화하고 전체 배열을 보존합니다.
CNB CZEONIA	rate=3.42, volumeInCZKmio=5643입니다. volume은 CZK가 아니라 CZK million입니다.	rate는 percent, volume은 CZK_million으로 저장합니다. 절대 CZK가 필요하면 명시적으로 ×1,000,000 하되 원값도 보존합니다.


캠페인 기능 영향
Cohort	기존 주장	이번 검증 판정
C-04 기업 스크리너	구현·검증 완료	계산 코드는 동작하지만 ATS/ALIO/GLEIF/ARES identity와 산업 다대다 계약이 미완성이라 실제 동료군 비교는 DATA-CONTRACT-FAIL
C-05 시간축·가치·AI 분석	구현·검증 완료	ECB·OECD·Eurostat·IMF·World Bank·CNB normalized가 손실되거나 해독 불가하므로 실제 API 기반 분석은 DATA-CONTRACT-FAIL
C-06 공고 표준화·필터	구현·검증 완료	49건 중 14건 직종 false positive, Lever 고용형태·다중 위치·요건 오분류로 SEMANTIC-FAIL


따라서 캠페인의 기계적 상태는 여전히 VALID / decision-approved지만, 기능적 완료 판정은 유지할 수 없습니다. 우선 수정 순서는 다음과 같습니다.
1. required_paths를 path + nonempty + type + enum + query-scope + freshness 계약으로 변경
2. compact() 결과를 validation preview로만 제한하고 production normalized 데이터와 분리
3. OECD CZ 제거, IMF·World Bank catalog/runtime drift 수정
4. Lever·Greenhouse·MPSV 급여·위치·고용형태 정규화 수정
5. title 검색과 description 검색 분리, required unknown 보수 규칙 적용
6. 위 실제 raw 반환물을 regression fixture로 고정
이번에는 진단 요청 범위에 맞춰 저장소 코드는 수정하지 않았습니다. 테스트 4개는 통과했지만, 실제 provider 의미 검증을 포함하지 않아 완료 증거로 사용할 수 없다는 결론입니다.


오후 7:49








컨텍스트 압축됨










오늘 오후 9:43
구체적으로 내가 로직을 정리하여 어떤 검색용 기준 변수들이 있는지 설명해봐. 또 이 기준에 따라 검사가 불가능한 케이스 조합도 설명해서 구체적으로 동일한 의미의 다른 설명값 필드를 통합하여 검색검증하는 것, 특수 필드라서 검색과 정렬에 사용할 수 없는 필드, 중복되는 정보나 필요없는정보 등으로 나눠서 api별로 정리해. 구체적으로 이 작업의 의미가 무엇인지 이해하여 너가 발전시킴으로써 필요한 작업, 즉 특정 api를 폐기하거나 클러스터별로 분류하여 검색하는 형식으로 나눌방법등 검색과정의 인지부조화나 로직문제를 해결할 방법을 찾아







오후 9:43






5분 15초 동안 작업함



결론
이 작업의 본질은 모든 API 응답을 한 표에 억지로 합치는 것이 아닙니다.
정확한 목표는 다음 세 가지입니다.
1. 사용자 조건에 맞는 공고·기업을 MATCH로 판정한다.
2. 정보 부족으로 검사할 수 없는 후보를 NO_MATCH가 아니라 UNKNOWN으로 분리한다.
3. 기업가치·거시경제·공공조달·기술활동처럼 의미가 다른 데이터는 별도 클러스터에서 분석한 뒤, 법인 ID와 시점이 확인된 경우에만 검색 결과에 보조정보로 연결한다.
현재 코드는 17개 검색 입력을 제공하지만, 일부 필드의 이름과 실제 검사 의미가 어긋나 있습니다. 대표적으로:
- job_keywords: 직무 제목이 아니라 설명·위치·부서까지 검색
- languages: 지원자 요구 언어가 아니라 공고 표시 언어 검사
- employment_types: Lever의 Permanent를 full-time으로 잘못 변환
- required_requirement_terms: 요건이 없다는 뜻과 요건 추출이 불가능하다는 뜻을 구별하지 못함
- 급여: 통화·기간만 비교하고 base/OTE, 세전·세후, 지역별 구간을 구분하지 못함
근거 코드는 [job_search.py (line 36)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/job_search.py:36)입니다.
1. 현재 존재하는 검색 기준 17개
구분	현재 변수	실제 의미	문제
국가	countries	공고 근무 국가	다중 근무지와 remote 허용국가를 한 값으로 축약
일반 검색어	job_keywords	제목·본문·위치·부서 전체 중 포함 여부	실제 직종 검색과 설명문 검색이 혼합됨
직종	occupations	직종명 또는 직업코드 문자열	CZ-ISCO와 자유 제목을 같은 방식으로 검색
위치	locations	location_raw 부분 문자열	도시·주·도·국가·다중 위치 구별 없음
근무 장소	workplace_types	remote/hybrid/on-site	remote가 전 세계 근무 가능인지 판별 불가
고용 형태	employment_types	full-time/part-time/contract/internship	정규직 여부와 주당 근무시간을 혼합
언어	languages	현재는 공고 표시 언어	요구 언어가 아님
산업	industries	공고에 포함된 산업 문자열	ATS에는 대개 없으므로 법인정보 결합 필요
기업 유형	company_types	공공기관 등 기업분류	상장·비상장·공기업·정부기관을 분리하지 않음
급여 하한	minimum_salary_floor	공고 급여 하한 비교	급여가 없으면 검사 불가
급여 상한	maximum_salary_ceiling	공고 급여 상한 비교	예산 상한인지 희망 최대급여인지 의미 불명확
급여 통화	salary_currency	USD/KRW/CZK 등	FX 기준일 없음
급여 기간	salary_period	hour/month/year	연환산 정책 없음
필수 요건	required_requirement_terms	required 요건 포함 여부	미추출·미기재·실제 미요구가 혼합됨
선호 요건	preferred_requirement_terms	일치 개수로 정렬	preferred와 required를 모두 hit로 계산할 수 있음
활성 공고	active_only	수집 시점 기준 활성 여부	마감일 없는 ATS 공고의 현재성 보장 불가
국가 배분	country_allocation	국가별 목표 공고 수	현재는 고유 기업 수가 아니라 공고 수 기준


2. 검색 규격을 이렇게 다시 원자화해야 함
직무 검색
job_keywords 하나를 다음으로 분리해야 합니다.
- title_terms: 제목에 반드시 있어야 하는 단어
- description_terms: 본문에서 찾을 기술·업무 단어
- excluded_terms: 제외할 직종·책임
- occupation_codes: CZ-ISCO 등 공식 직업코드
- occupation_system: CZ-ISCO, ISCO-08, 내부 taxonomy
- job_function: engineering, finance, HR 등
- seniority_level: entry, junior, senior, lead, manager
저장된 실제 engineer 검색 49건 중 제목에 engineer가 없는 공고가 14건 포함된 이유가 현재 본문 전체 검색입니다. 제목 일치와 설명문 일치를 별도 점수로 계산해야 합니다.
위치 검색
단일 location_raw 대신 공고×근무지 테이블이 필요합니다.
- country_code
- admin_region
- city
- location_text
- is_primary_location
- remote_scope: global/country/region/timezone/unknown
- remote_eligible_country
- relocation_supported
- location_confidence
Lever 실제 표본 74건 중 34건이 다중 위치였습니다. 현재는 주 위치만 남기므로 Seoul이 보조 위치인 공고가 KR 검색에서 누락됩니다. Lever는 categories.location과 allLocations를 구분합니다. Lever 공식 API
근로계약 검색
employment_type을 다음 독립 차원으로 분리해야 합니다.
- hours_type: full-time/part-time/unknown
- contract_type: employee/contractor/intern/temporary
- duration_type: permanent/fixed-term/unknown
- weekly_hours_min/max
- schedule_type
- shift_type
Permanent는 계약기간이 무기한이라는 뜻이지 full-time이라는 뜻이 아닙니다. 현재 변환 로직은 [job_search.py (line 186)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/job_search.py:186)에서 이를 잘못 합칩니다.
언어 검색
반드시 세 종류로 분리해야 합니다.
- posting_language: 공고를 작성한 언어
- required_language: 지원자에게 요구되는 언어
- language_proficiency: CEFR, native, fluent 등
현재 languages=["english"]는 “영어가 필요한 직무”가 아니라 “영어로 작성된 공고”를 찾습니다.
급여 검색
급여는 다음 필드가 모두 맞을 때만 직접 비교해야 합니다.
- salary_min/max
- currency
- period: hour/month/year
- basis: base/OTE/total/allowance/unknown
- gross_net: gross/net/unknown
- location_tier
- employment_fraction
- fx_rate
- fx_as_of
- conversion_policy
예를 들어 다음 값은 서로 비교할 수 없습니다.
- USD/year base salary
- USD/year OTE
- CZK/month gross
- CZK/hour
- 지역별로 서로 다른 Greenhouse 급여구간
Greenhouse 급여정보는 상세 공고에서 pay_transparency=true를 사용해야 하며 목록 응답만으로 항상 확보되는 것이 아닙니다. Greenhouse 공식 API
자격요건 검색
각 요건은 한 행으로 분리합니다.
provider + job_id + requirement_kind + normalized_key
+ necessity + proficiency/value + evidence_span + confidence
requirement_kind는 최소 다음을 분리해야 합니다.
- skill
- tool/platform
- language
- education
- experience
- certification
- statutory_license
- security_clearance
- work_authorization
- physical_requirement
- other
certification과 법정 license는 같은 것이 아닙니다. AWS 자격증 우대와 체코에서 법적으로 요구되는 전문면허를 한 열에서 비교하면 안 됩니다.
3. 판정 상태는 5가지가 필요함
상태	의미	검색 처리
MATCH	값이 확인됐고 조건을 만족	엄격 일치 결과에 포함
NO_MATCH	값이 확인됐고 조건과 다름	제외
UNKNOWN	원천에 값이 없거나 추출하지 못함	별도 “검사 불가 후보”로 반환
CONFLICT	여러 원천이 서로 다른 값을 제공	수동검토 또는 신뢰도 우선
NOT_APPLICABLE	해당 데이터에 적용할 수 없는 조건	비교대상에서 제외


현재는 UNKNOWN을 대부분 NO_MATCH처럼 제외합니다. 사용자는 결과가 없는 이유가 “조건에 맞는 회사가 없음”인지 “급여정보가 없어서 검사할 수 없음”인지 알 수 없습니다.
4. 검사 불가능하거나 잘못 판정되는 조합
조건 조합	검사 불가능한 경우	올바른 처리
국가 + remote	remote 범위가 전 세계인지 특정 국가인지 없음	UNKNOWN_REMOTE_SCOPE
국가 + 다중 근무지	주 위치만 저장됨	근무지를 별도 행으로 펼친 뒤 ANY 판정
full-time + Permanent	Permanent만 제공됨	hours는 UNKNOWN, duration만 permanent
영어 필요	공고 작성언어만 영어	요구언어 미확인
연봉 10만 USD 이상	급여 필드 없음	UNKNOWN, 10만 미만으로 처리 금지
USD/year 비교	OTE와 base가 혼재	basis가 같을 때만 비교
국가 간 급여 순위	FX 기준일·세전/세후·물가 기준 없음	기본적으로 비교 금지
자격증 필수	본문 추출이 안 됨	“필수 아님”이 아니라 UNKNOWN
특정 산업	ATS에 산업 없음	법인 ID→기업등록원→산업코드 연결 필요
공기업 검색	기관명만 있고 법적 유형 없음	ALIO/ARES/GLEIF 등 identity join 필요
현재 채용	마감일 없고 목록에만 존재	snapshot 시점의 listed 상태만 표시
국가별 기업 수	한 회사가 공고 20건 게시	공고 수와 고유 법인 수 별도 집계
기업가치 + 채용	ATS board slug만 존재	법인 ID가 해결되기 전 결합 금지
기업 간 재무 순위	통화·기간·회계개념이 다름	동일 peer·unit·period·concept 안에서만 순위
AI 도입 효과	GitHub push만 존재	도입 사건 증거가 아니라 활동 proxy
거시 상관분석	시점·빈도·공개시점이 다름	point-in-time 정렬 전 분석 부적격
국가 간 자격증 비교	공식 동등성 근거 없음	명칭 유사성만으로 통합 금지


5. 동일 의미로 통합할 수 있는 필드
공통 의미	원천별 설명값	통합 조건
공고 ID	GH id, Lever id, MPM idx, MPSV portalId	반드시 provider namespace 포함
공고 제목	GH title, Lever text, MPM title, MPSV pozadovanaProfese	원문과 정규화 제목을 모두 보존
기관/회사 표시명	GH company, Lever board, MPM insttname, MPSV zamestnavatel.nazev	표시명일 뿐 법인 동일성은 별도 확인
법인 식별자	SEC CIK, DART corp code, GLEIF LEI, ARES/MPSV IČO	namespace별 유지, crosswalk로만 연결
국가	ISO2, ISO3, 현지 국가코드, 위치 문자열	ISO 변환표와 매핑 근거 필요
산업	ARES CZ-NACE, USAspending NAICS, 기업 공시 산업	ISIC 등 공통분류로 crosswalk하되 원코드 보존
날짜	created/posted/updated/closing/snapshot/available	같은 date로 합치지 않고 날짜 의미를 분리
급여	min/max/currency/period	basis와 단위가 동일한 경우만 비교
요구사항	구조 필드와 명시 공고 문장	kind + normalized_key + necessity가 같을 때만 겹침 계산
거시 관측	FRED/BLS/ECOS/Eurostat/IMF/WB/CNB	series·geo·frequency·unit·vintage 전체가 일치해야 비교


6. API별 검색 사용 규칙
현재 카탈로그는 28개 operation이고, 코드에만 있는 체코 MPSV 후보를 포함하면 29개입니다.
채용·요건 클러스터
API	검색에 사용할 필드	검색·정렬 금지/중복	조치
Greenhouse	공고 ID·제목·위치·부서·본문·갱신일	임의 metadata, 본문 숫자를 급여로 승격, board를 법인으로 간주	유지. 공고별 상세·pay transparency 추가
Lever	ID·제목·country·workplaceType·allLocations·commitment·lists	Permanent→full-time 금지, board slug=법인 금지, 불명확 bullet=required 금지	유지하되 정규화 수정
MPM 공공취업	idx/title/insttname/type01/type02/regdate/enddate	목록만으로 위치·급여·요건·근로형태 판정 금지	metadata 검색 전용. 현재 공고 쿼리와 상세 API 필요
MPSV 체코	portal ID·IČO·CZ-ISCO·위치·급여·교육·언어·기술	codebook ID를 라벨로 간주 금지, 연락처 PII 제외	실제 snapshot 검증 후 정식 카탈로그 편입


기업 식별·재무·시장 클러스터
API	사용할 정보	검색·정렬 금지/중복	조치
SEC Submissions	CIK·법인명·accession·form·filed date	“최신 제출=최신 재무제표” 가정 금지	미국 법인 및 filing index
SEC Company Facts	concept·unit·period·form·filing·value	배열 첫 값, concept 이름만으로 순위 금지	전체 fact를 행으로 펼침
OpenDART	corp code·계정·기간·통화·receipt	account name만으로 중복 제거 금지, float 금액 금지	상세 composite key와 Decimal 사용
GLEIF	LEI·법정명·국가·등록상태	LEI 상태를 기업가치 점수로 사용 금지	identity resolution 전용
ARES	IČO·법정명·주소·CZ-NACE	복수 NACE를 첫 코드 하나로 축약 금지	체코 법인·산업 연결 전용
Alpha Vantage	symbol별 날짜·OHLCV	IBM 고정 probe를 전체 기업 검색에 사용 금지, raw close를 조정주가로 간주 금지	검증 probe와 동적 symbol 작업 분리


SEC API는 무료·키 불필요지만 실제 연락처가 포함된 User-Agent가 필요합니다. 현재 저장소 값은 placeholder이므로 운영 호출을 차단해야 합니다. SEC 공식 API 안내
거시·국가 환경 클러스터
API	통합 필드	사용할 수 없는 방식	조치
FRED	series/date/value/unit/vintage	회사 성과로 귀속	유지, 과거분석은 빈티지 사용
BLS	series/period/value/unit/footnote	채용 완료·개별기업 고용으로 해석	미국 고용환경 전용
BEA catalog	dataset name·description	GDP 값처럼 검색·정렬	현재 operation은 사용자 검색에서 폐기; 실제 관측 operation으로 교체
ECOS	series/item/frequency/time/value/unit	요청 주기를 실제 반환 주기로 단정	한국 거시 보조
Eurostat	dimension 좌표·geo·unit·time·value	flat 배열 index로 값 해석	JSON-stat cube를 완전 전개
ECB	series key·통화쌍·frequency·time·value	series object 자체를 값으로 정렬	구조 metadata와 관측값 전개
OECD CLI	포함 국가·time·value·unit	현재 operation을 체코 지표로 사용	CZ capability 제거 또는 다른 dataflow로 교체
IMF WEO	country/year/value/vintage/status	전망치를 실적으로 혼합	actual/estimate/projection 분리
World Bank	country/indicator/year/value/unit	metadata 배열과 관측 배열 혼합	페이지 전체 보존 및 국가별 전개
CNB 환율	currency/amount/rate/date	rate만 비교	실제 단위환율은 rate ÷ amount
CNB CZEONIA	date/rate/volume	volume을 단순 CZK로 표현	금리는 %, 거래량은 CZK million
BEA 실패 상태	현재 키 비활성	HTTP 200을 성공으로 처리	키 복구 전 UNAVAILABLE


Eurostat와 World Bank처럼 다차원·메타데이터 배열을 가진 API는 배열 위치 자체가 의미가 아닙니다. 차원과 관측값을 결합해서 행으로 풀어야 합니다. Eurostat API, World Bank API
공공수요·기관맥락 클러스터
API	유효 용도	검색·정렬 금지/중복	조치
ALIO 기관	기관·지점 표시명과 기관유형	빈 apbaNa, 존재하지 않는 apbaId 계약, 연락처	응답규격 수정 후 기관 연결 보조
ALIO 시설	기관 시설 활동	채용공고로 변환 금지	job search에서 제거, context 전용
ALIO 행사	기관 행사 활동	채용 수요로 해석 금지	context 전용
ALIO 사업	기관 사업명	회사 매출·채용으로 해석 금지	context 전용
TED	notice·buyer·winner·금액·통화·날짜	정정·취소 notice 중복, 통화 없는 금액 비교	조달수요 신호 전용
USAspending	award·recipient·obligation/outlay·NAICS	award start date를 이벤트 발생일로 사용	거래/액션 endpoint와 분리


기술·연구 활동 proxy
API	유효 용도	사용 금지	조치
GitHub	저장소 활동 보조지표	AI 도입, 채용, 기업가치의 직접 증거	독립 proxy 클러스터로 강등
OpenAlex	기관 연계 연구성과 보조지표	사업성과·AI 채택·고용 증가의 직접 증거	독립 proxy 클러스터로 강등


7. 중복 제거 키
중복은 표시 문자열이 아니라 다음 원자키로 제거해야 합니다.
데이터	중복 제거 키
공고 snapshot	provider + job_id + snapshot_at
현재 공고	provider + job_id 중 최신 snapshot
법인	identifier_namespace + identifier_value
공고 위치	provider + job_id + normalized_location_id
요구사항	provider + job_id + normalized_key + necessity + evidence_span_hash
재무 사실	entity + taxonomy + concept + period + unit + filing + frame
거시 관측	provider + series_key + geo + frequency + unit + adjustment + period + vintage
조달	provider + notice/award_id + revision/action_id
활동 proxy	provider + object_id + event_date


원문과 정규화 결과는 중복이 아닙니다. 원문은 증거이고 정규화 행은 검색용 파생물입니다. 둘을 lineage로 연결해야 합니다.
8. API를 클러스터별로 검색하는 최종 방식
사용자 프로필
  ├─ 채용 클러스터 → 현재 공고 후보
  ├─ 요건 클러스터 → 필수/우대/불명 요건
  ├─ 법인 식별 클러스터 → 공고 회사와 법인 연결
  ├─ 재무·시장 클러스터 → 비교 가능한 회사만 가치분석
  ├─ 거시 클러스터 → 국가·시점 통제변수
  ├─ 공공수요 클러스터 → 정부 수요 보조신호
  └─ 활동 proxy 클러스터 → 설명용 보조지표
처리 순서는 다음이어야 합니다.
1. 공급자별 원문을 손실 없이 저장합니다. 현재 compact()는 목록을 5개로 자르므로 운영 정규화에 사용할 수 없습니다. [base.py (line 42)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/connectors/base.py:42)
2. 공급자별 adapter가 공통 fact table로 변환합니다.
3. 법인·직업·산업·지역·언어 codebook을 연결합니다.
4. 각 조건을 5상태 판정합니다.
5. strict_matches, unverifiable_candidates, excluded_candidates, conflicts를 따로 반환합니다.
6. 정렬은 비교 가능한 cohort 내부에서만 수행합니다.
7. 모든 결과에 원천 URL·레코드 ID·수집일·변환 규칙·신뢰도를 붙입니다.
9. 폐기·격리해야 할 현재 작업
즉시 사용자 검색에서 제외하거나 격리할 대상은 다음과 같습니다.
- bea_dataset_catalog: 데이터 발견용이지 GDP 관측값이 아님
- oecd_cli의 CZ capability: 현재 반환군에 체코가 없어 잘못된 지역 선언
- ALIO 시설·행사·사업: 채용 검색 대상이 아님
- GitHub/OpenAlex: 채용·AI 도입·기업가치의 직접 필터가 아님
- Apple·Samsung·IBM·Microsoft·Airtable·Spotify 고정 operation: API 연결 검증 fixture이지 전체 기업 검색 endpoint가 아님
- MPM 목록: 위치·급여·요건 검색에서는 격리
- SEC: 올바른 User-Agent 전까지 비활성
- MPSV: 실제 snapshot과 codebook 검증 전 candidate
- compact() 적용 normalized 결과: 미리보기 전용, 분석·검색 입력 금지
- ALIO의 빈 값도 통과시키는 현재 필드 검사: 운영 성공 판정에서 폐기
현재 validator는 필드가 “존재하는지”만 확인하고 null·빈 문자열·자료형·코드 의미를 확인하지 않습니다. [validation.py (line 118)](/home/ubuntu/root/company-intelligence-platform/src/company_intel/validation.py:118)
따라서 현 상태의 올바른 판정은 검색 파이프라인은 실행 가능하지만 의미 검증은 미완료입니다. C-06은 기능적으로 SEMANTIC-FAIL, C-04·C-05는 데이터 계약을 고친 뒤에만 실제 비교 가능한 상태입니다. 캠페인의 기계적 decision-approved와 제품의 실제 검색 정확도는 별개입니다. 이번 답변에서는 분석만 수행했고 코드나 캠페인 파일은 변경하지 않았습니다.