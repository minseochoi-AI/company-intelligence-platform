# Company Intelligence Platform

미국·한국·체코·슬로바키아의 28대 공식 API를 연결하여 기업·공공기관·채용 공고의 원천 증거를 실시간 수집하고, 5계층 클러스터 시그니처(`ClusterSignature`) 기반 21,000개 다차원 공간에서 3-계층 동적 엑셀 보고서를 원클릭 컴파일하는 로컬 우선 엔터프라이즈 인텔리전스 플랫폼입니다.

---

## 🚀 1. 비개발자를 위한 1분 초간편 시작 가이드 (Turnkey Setup)

개발 지식이 없어도 터미널에서 명령어 1줄만 실행하면 **Python 가상환경, 의존성 라이브러리, 안티그래비티(Antigravity) 스킬 등록, API 키 검증**까지 100% 자동 구성됩니다.

```bash
# 저장소 복제 후 디렉토리 이동
git clone https://github.com/minseochoi-AI/company-intelligence-platform.git
cd company-intelligence-platform

# 원클릭 환경 자동 구성 스크립트 실행 (Make 또는 Bash 스크립트)
make setup
# 또는
./setup.sh
```

스크립트가 완료되면 즉시 플랫폼과 안티그래비티 스킬 사용 준비가 완료됩니다.

---

## 🤖 2. 안티그래비티 (Antigravity) AI 어시스턴트 사용 가이드

안티그래비티 IDE에서 이 프로젝트 폴더를 열면, 워크스페이스 스킬(`.agents/skills/`)이 자동으로 인식됩니다.

### 채팅창에서 바로 입력할 수 있는 자연어 질의 예시
안티그래비티 채팅창에 복잡한 명령어를 칠 필요 없이, 평상시 쓰는 한국어로 질문하면 AI가 래티스 좌표를 계산하고 엑셀을 생성합니다:

1. **사전 사양 명세 확인**:
   > "현재 연결된 28대 API 사양과 클러스터 시그니처 제어 공간을 브리핑해줘"
2. **체코 국영기업 채용공고 추출**:
   > "체코 국영기업의 공공 IT 채용공고를 엑셀 파일로 추출해줘"
3. **한국 공기업 정규직 필터링**:
   > "`KR:STATE_OWNED:ALL:REGULAR:ALL` 시그니처에 해당하는 공고만 뽑아서 엑셀로 저장해줘"
4. **동적 열 확장 엑셀 추출**:
   > "체코 공공기관 공고에 ARES 법인형태(legal_form)와 급여 정보를 포함해서 동적 엑셀로 뽑아줘"

### 유용한 슬래시(/) 명령어 활용법
- `/plan` : 다차원 클러스터 확장이나 신규 API 연동 시 단계별 검증 계획서를 수립할 때 사용
- `/goal` : 수천 건의 공고 검증 및 엑셀 전수 감사 등 장시간 무중단 작업을 백그라운드로 실행할 때 사용
- `/grill-me` : 모호한 직무 조건이나 학위 요건에 대해 시스템이 역으로 질문하여 최적의 클러스터 시그니처를 도출할 때 사용

---

## 🌐 3. 28대 API 키 및 IP 제한 / 오류 발생 원인 총정리

새로운 기기(노트북, 다른 서버, 다른 클라우드 환경)로 저장소를 옮겼을 때, **공인 IP 변경 또는 해외 IP 차단으로 인해 발생할 수 있는 오류와 방어책**입니다:

| 공급자 (API) | 인증 방식 | IP 제한 및 주요 오류 발생 원인 | 해결책 및 방어 가이드 |
|---|---|---|---|
| **한국고용정보원 워크넷 (WorkNet)** | API Key (`WORKNET_*`) | **[주의: 고정 IP 바인딩]** 워크넷 개발자 센터 신청 시 등록한 공인 IP와 현재 접속 IP가 다를 경우 `HTTP 401` 또는 `등록되지 않은 IP` 에러 발생. | 워크넷 개발자 포털(openapi.worknet.go.kr) '마이페이지 > 인증키 관리'에서 현재 기기의 공인 IP(`curl ifconfig.me`)를 허용 IP로 추가 등록. |
| **한국 공공데이터포털 (data.go.kr 계열: MPM, HRD, ALIO+)** | API Key (`DATA_GO_KR_*`, `MPM_*`, `ALIO_*`) | **[주의: 해외 IP 차단]** AWS/GCP 등 해외 리전 인스턴스에서 호출 시 공공 사이버안전센터의 국가 방화벽에 의해 `HTTP 403 Forbidden` 또는 `Connection Timeout` 발생. | 국내 통신사 회선이나 한국 리전(`ap-northeast-2`) 서버에서 구동하거나, 오프라인 스냅샷 데이터를 기본으로 활용. |
| **금융감독원 전자공시 (OpenDART)** | API Key (`OPENDART_API_KEY`) | **[주의: 단시간 대량 호출 IP 차단]** 일일 20,000건 한도 초과 또는 초당 10회 이상 과도한 동시 요청 시 해당 IP가 10분~24시간 차단(`429` 또는 에러코드 `011`). | 플랫폼 내에 구현된 지연 대기(Rate Limiting) 및 로컬 캐시를 활용하여 초당 3회 이하로 조절. |
| **한국은행 경제통계 (ECOS)** | API Key (`ECOS_API_KEY`) | 일일 10,000건 제한. 비정상적 트래픽 발생 시 IP 단위 일시 차단. | 지수 백오프 및 캐시 활용. |
| **미국 증권거래위원회 (SEC EDGAR)** | Keyless (무키) | **[주의: User-Agent 필수]** 요청 헤더에 `User-Agent: Sample Company Name AdminContact@domain.com` 형식의 이메일이 없거나 기본 파이썬 요청 헤더일 경우 즉시 `HTTP 403` 영구 차단. 초당 10회 초과 시 10분간 IP 차단. | `.env` 파일의 `SEC_USER_AGENT`에 본인의 영문 이름과 이메일을 정확히 기재. 플랫폼 코드가 이를 자동으로 헤더에 주입함. |
| **체코 경제주체등록원 (ARES) / 통합구인 (MPSV)** | Keyless (무키) | 체코 정부 WAF 방화벽이 특정 클라우드(해외 IP 대역)의 과도한 스크레이핑 트래픽을 감지할 경우 일시 차단 가능. | 플랫폼의 `ares_dynamic.py` 및 `mpsv_stream.py`에 내장된 지수 백오프 및 스트리밍 파서 사용. |
| **미국 연방조달 (USAspending)** | Keyless (무키) | Cloudflare WAF 적용으로 대량 POST 쿼리 전송 시 Cloudflare 403 보안 챌린지 발생 가능. | 배치 단위 쿼리 분할 및 캐시 적재. |
| **미국 노동통계국 (BLS) / FRED / BEA** | Keyed & Keyless | 일일 쿼터 초과 시 일시 제한. IP 바인딩은 없음. | API 키가 `.env`에 올바르게 입력되어 있는지 확인. |

---

## 💻 4. 터미널 한국어 우선 CLI 명령어 가이드

CLI 도구 `company-intel`은 한국어 명령과 옵션을 기본으로 지원합니다:

### 1) 사전 기준 설명문 출력 (28대 API, 142개 속성, 21,000개 좌표 브리핑)
```bash
poetry run company-intel 클러스터-사양-안내
# 또는 Make 사용
make spec
```

### 2) 대화형 클러스터 채용공고 엑셀 추출
사전 설명문을 브리핑하고, 입력한 시그니처의 활성화 공급자와 미결정 차원(`ALL`)을 실시간으로 분석하여 엑셀을 생성합니다:
```bash
poetry run company-intel 클러스터-채용-추출 --대화형 --국가 CZ --섹터 PUBLIC_INSTITUTION
```

### 3) 5단계 클러스터 시그니처 기반 원클릭 엑셀 추출 (24열 하이퍼링크 수식 포함)
```bash
poetry run company-intel 클러스터-채용-추출 --시그니처 KR:STATE_OWNED:ALL:REGULAR:ALL --출력-경로 kr_soe_jobs.xlsx
```

### 4) 동적 3-계층 보고서 컴파일 (Core 8열 + 동적 N열 + Provenance 7열)
사용자가 지정한 원천 속성을 동적으로 삽입하고, `=HYPERLINK()` 공고 바로가기 수식의 열 위치를 자동으로 계산합니다:
```bash
poetry run company-intel 클러스터-채용-추출 --국가 CZ --동적-속성 legal_form,salary_min,award_amount --출력-경로 cz_dynamic.xlsx
```

### 5) 28대 API 원천 속성 메타데이터 감사
```bash
poetry run company-intel api-속성-조회 --원천 cz_mpsv
poetry run company-intel api-속성-조회 --원천 kr_alio
```

---

## 📊 5. 3-계층 엑셀 보고서 구조 (Report Architecture)

동적 엑셀 컴파일러는 다음의 3-계층 구조로 생성됩니다:
1. **Core Layer (고정 8열)**:
   - 순번(No), 국가(Country), 기관/기업명(Employer Name), 사업자등록번호(IČO/Org ID), 공고 고유 식별자(Job ID), 공식 직무명(Job Title), 직업분류코드(Job Code), 클러스터 시그니처(Cluster Signature)
2. **Dynamic Attribute Layer (가변 N열)**:
   - 활성화된 API 원천 필드: 체코 법인형태(`pravniForma`), 한국 기관구분(`instt_se`), 주당 근로시간, 최소 학력 요건, 최소/최대 급여, 연방조달 계약금액 등
3. **Action & Provenance Layer (고정 7열)**:
   - 원천 공고 URL, 클릭 가능한 하이퍼링크(`=HYPERLINK(col, "공고 확인 ↗")`), 실시간 신선도(`LIVE_ACTIVE`, `CLOSED`), 접수 마감일, 원천 API 명칭, 무결성 검증, 검증 메모

---

## 🛠 6. Make 유용한 명령어 모음

```bash
make help        # 전체 사용 가능한 명령어 도움말 출력
make setup       # 원클릭 환경 자동 구성 및 스킬 등록
make spec        # 28대 API 기준 사양 설명문 출력
make test        # 31개 단위 테스트 및 회귀 무결성 검증 실행
make export-all  # 6대 IT경영 마스터 엑셀 워크북 전수 재생성 및 검증
make clean       # 임시 캐시 및 파이썬 컴파일 아티팩트 정리
```
