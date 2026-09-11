# 공식 원천·접근 검증 기준 — 2026-09-11

이 문서는 공식 문서와 2026-09-11의 제한된 read-only 호출로 확인한 설계 근거의
스냅샷이다. 개인정보 수집·유료 사용·제한 원천 자동 추출은 수행하지 않았다. endpoint가
존재하고 표본 호출이 성공했다는 사실은 특정 기업·직무·재무·채용 데이터의 완전성,
장기 무료 쿼터 또는 재배포 권한을 뜻하지 않는다.

## 공통 판정 어휘

- `KEYLESS_PUBLIC`: 키 없이 공개된 read-only endpoint. 공정 사용, 식별 헤더, 캐시·재시도 규칙은 별도 준수한다.
- `FREE_REGISTERED`: 무상 등록 키·계정·이메일 검증이 필요하다. 비밀값과 호출 한도는 코드·스프레드시트에 기록하지 않는다.
- `APPROVAL_REQUIRED`: 가입·심사 또는 공급자 승인 뒤에만 호출한다.
- `DOCUMENT_ONLY`: 공식 문서는 공개되지만 구조화된 fact API 또는 자동 추출 권한이 확인되지 않았다.
- `AGGREGATE_ONLY`: 국가·산업·지역 집계이며 개별 기업 재무·고용·공고의 증거가 아니다.
- `EXTRACTION_RESTRICTED`: 원시 공고 등의 자동 추출·재배포가 일반 사용자에게 허용되지 않은 원천이다.

## 미국·한국

| 원천 | 현재 접근 상태 | 데이터 역할 | 플랫폼에서의 보수적 분류 | 공식 근거 |
|---|---|---|---|---|
| SEC EDGAR | `KEYLESS_PUBLIC`; 선언된 User-Agent와 초당 10건 이하가 필요 | CIK, 신고 이력, XBRL 재무 | `company_financial_disclosure` | [EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [자동 접근 FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions) |
| BLS | 공개 API; 무등록·등록 한도와 series 범위가 다름 | 고용·임금·물가 조사 시계열 | `labor_market_aggregate_only` | [BLS API FAQ](https://www.bls.gov/developers/api_FAQs.htm) |
| FRED/ALFRED | `FREE_REGISTERED`; API key와 저속·캐시 호출 필요 | 거시·지역 시계열과 빈티지 | `macro_series_only` | [FRED 오류·제한](https://fred.stlouisfed.org/docs/api/fred/errors.html), [이용약관](https://fred.stlouisfed.org/docs/api/terms_of_use.html) |
| BEA | `FREE_REGISTERED`; 이메일 검증 UserID | GDP·산업·지역·국제/MNE 집계 | `macro_industry_regional_aggregate` | [BEA API 가이드](https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf) |
| OpenDART | `FREE_REGISTERED`; `crtfc_key`가 필요 | 공시 원문·분기/연간 재무 | `company_financial_disclosure` | [OpenDART](https://opendart.fss.or.kr/intro/main.do), [약관](https://opendart.fss.or.kr/intro/terms.do) |
| ECOS | `FREE_REGISTERED`; 정확한 호출 한도는 구현 전 재확인 | 통화·금융·환율·GDP 등 | `macro_series_only` | [ECOS Open API](https://ecos.bok.or.kr/api/) |
| ALIO Plus 시설·행사·사업·기관 | `FREE_REGISTERED`; 서비스별 키, 가이드 v1.6의 HTTP form 전송 | 공공기관 식별·시설·행사·사업 맥락 | `public_institution_context_only`; 채용·고용·재무로 승격 금지 | 로컬 [ALIO Plus API 가이드 v1.6](../../../알리오%20플러스%20API%20가이드%201.6.pdf) |
| 인사혁신처 공공취업정보 | `FREE_REGISTERED`; data.go.kr 활용신청 서비스키 | 국가·지방·공공기관·교육청 공고 목록의 ID·기관·제목·유형·등록·마감일 | `public_job_posting_metadata`; 상세 자격 근거 미확인 | [공공취업정보 조회 서비스](https://www.data.go.kr/data/15156780/openapi.do) |

Work24와 유료 sec-api.io는 현재 실행 코드·설정의 공급자가 아니다. `SEC_USER_AGENT`는
공식 SEC 호출의 연락처 식별 헤더이고 API key가 아니며, `DATABASE_URL`은 현재 로컬
DuckDB 파일 경로다.

## EU·체코

| 원천 | 현재 접근 상태 | 데이터 역할 | 플랫폼에서의 보수적 분류 | 공식 근거 |
|---|---|---|---|---|
| ARES | `KEYLESS_PUBLIC` read-only REST; IČO·기업 식별 중심 | 법인명, IČO, 법적 형태, CZ-NACE | `company_identity_registry` | [ARES OpenAPI](https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/v3/api-docs) |
| 체코 Public Register/Collection of Deeds | 검색 UI와 등기 Open Data는 공개이나 구조화 재무 fact API는 미확인 | 등기·임원·지분·개별 제출 문서 | `financial_document_available`, `financial_document_absent`, `financial_parse_failed`, `unknown`을 분리 | [Public Register](https://www.or.justice.cz/ias/ui/rejstrik), [Justice Open Data](https://dataor.justice.cz/) |
| CNB Central Storage(OAM) | 무료·비차별 웹 문서 저장소; 공개 REST/벌크 API는 미확인 | 상장 발행인 연·반기·규제 공시 문서 | `listed_issuer_document_only` | [CNB OAM](https://www.cnb.cz/en/supervision-financial-market/information-published-issuers/index.html) |
| CNB ARAD | `FREE_REGISTERED`; 계정·API key와 호출 절제가 필요 | 금리·환율·통화 등 시계열 | `macro_covariate_only` | [ARAD REST](https://www.cnb.cz/aradtest/docs/api/rest-api.html) |
| CZSO DataStat | `KEYLESS_PUBLIC` REST/JSON-STAT/CSV/XLSX | 체코 고용·임금·산업·물가·GDP 집계 | `macro_industry_only` | [DataStat API](https://csu.gov.cz/zakladni-informace-pro-pouziti-api-datastatu) |
| Eurostat | `KEYLESS_PUBLIC`; 병렬 대량호출 대신 캐시·직렬 수집 | EU 국가·지역·산업·노동·경제 집계 | `macro_covariate_only` | [Statistics API](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api), [비동기 지침](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/asynchronous-api) |
| MPSV/노동청 공개 구인 | 조사상 `KEYLESS_PUBLIC` 전체 JSON과 일별 증분 후보이나 현재 28개 실행 Probe에는 없음 | CZ-ISCO, 급여, 교육·언어·기술·경력, 공개 고용주의 IČO | 구현 전 실제 필드·약관 검증이 필요한 `candidate_source` | [공개 구인](https://data.mpsv.cz/web/data/volna-mista-za-celou-cr), [스키마](https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.schema.json) |
| NSP / NSK | 조사상 NSP JSON API·NSK 공적 레지스트리 후보이나 현재 adapter에는 없음 | 직무 역량·교육·자격·CZ-ISCO/ESCO/EQF 연결 | 구현 전 검증할 `national_baseline_candidate`; 현재 결과 생성 금지 | [NSP API](https://www.nsp.cz/index.php/napoveda/api), [NSK](https://msmt.gov.cz/vzdelavani/dalsi-vzdelavani/narodni-soustava-kvalifikaci/pravni-ramec) |
| EURES | 집계 통계는 공개이나 원시 vacancy 자동 추출은 일반 사용자 범위에서 제외 | 국가·직종·학력·언어 등의 수요 집계 | `aggregate_demand_only`, `EXTRACTION_RESTRICTED` | [EURES vacancy statistics](https://eures.europa.eu/eures-services/eures-portal-statistics/job-vacancy-statistics_en) |
| ESCO / ILO ISCO | 공개 직업·기술 crosswalk | 직업·기술·국제 코드 매핑 | `crosswalk_only` | [ESCO API](https://esco.ec.europa.eu/en/use-esco/use-esco-services-api/esco-web-service-api), [ILO ISCO-08](https://isco.ilo.org/en/isco-08/) |

## 설계 보호 규칙

1. 채용공고는 채용 완료·퇴직·직원 수의 증거가 아니다.
2. 재무 문서 부재는 재무 값 0이 아니며, `document_only`와 `structured_verified`를 혼동하지 않는다.
3. 법인 식별자와 기간·산업/지역·point-in-time 가용성이 모두 확인된 경우에만 `correlation_candidate`로 표시한다. 이는 인과 증거가 아니다.
4. 자격 요건은 `vacancy_specific`, `national_baseline`, `crosswalk_only`를 분리하며, 국가 간 동등성은 직업 코드만으로 확정하지 않는다.
5. 모든 스프레드시트 행에는 `source_name`, `source_record_id`, `source_url`, `retrieved_at`, `license_attribution_status`, `company_match_confidence`, `classification_reason`을 보존한다.
6. 체코 문서형 재무는 상장·비상장 혼합 표본의 저빈도 preflight에서 문서 URL·기간·파싱 성공률을 확인한 뒤에만 `structured_verified`로 승격한다.

## 실제 접근성·필드 검증 스냅샷

| 범위 | 결과 | 증명하는 것 | 증명하지 않는 것 |
|---|---|---|---|
| 키 없는 18개 원자 작업 | 18/18 `passed`, 모두 HTTP 200·`required_paths` 충족 | 해당 시점의 접근성과 최소 응답 필드 계약 | 장기 쿼터, 전체 기업 coverage, 재배포 권한 |
| ALIO Plus 4개 작업 | 4/4 `passed`, 시설/행사/사업/기관별 식별 필드 충족 | 각 서비스키와 HTTP form 요청의 현재 동작 | 채용공고·고용 완료·재무 정보 |
| 인사혁신처 공공취업정보 목록 | 1/1 `passed`, HTTP 200·XML `resultCode` 충족 | 현재 서비스키 인증과 목록 응답 | 공고 상세 자격증·학력·기술·실제 채용 완료 |

세부 원자 필드와 사용 경계는
`atomic-api-compatibility-report-2026-09-11.md`를 기준으로 한다. 외부 호출 증적은 비밀과
원문을 문서에 복사하지 않도록 임시 디렉터리에서 검증했고, canonical decision에는 결과
상태와 필드 계약만 보존한다.

## 입력 문서 근거와 비밀 보호

사용자가 제공한 문서는 SHA-256 `42f0a077efe802d2bef97d11464f0b449ae1be95f2ba16e8137fd74b789aaa87`이며,
국가별 공식 데이터 연결은 41–96행, 채용 데이터 한계는 221–342행, 시간 구조는 347–381행,
API 조합은 383–690행과 1105–1190행에 제시되어 있다. 문서에 포함될 수 있는 인증정보·키·개인정보는
이 문서, 코드, 로그, 스프레드시트에 재기록하지 않는다.
