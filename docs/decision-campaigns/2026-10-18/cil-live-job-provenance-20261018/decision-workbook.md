# cil-live-job-provenance-20261018 — 의사결정 워크북

> 이 파일은 같은 `campaign.json`·결정 JSON에서 만든 읽기용 화면입니다.
> 현재 상태는 plan·result·검증 attempt와 파일 해시가 맞을 때만 통과로 표시합니다.
> 의도·설계 이유와 최종 해결 여부는 사람이 정본과 근거를 확인해 판단합니다.

## 이번 목적과 사용자 판단

### ClusterSignature 기반 CanonicalJobRecord 및 JobSchemaContract 키 불일치 방어 엔진

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | CanonicalJobRecord 데이터클래스 및 JobSchemaContract 선언적 키 별칭 매핑·검증기 |
| 현재 입력 문제 | src/company_intel/classification.py의 ClusterSignature(5계층)가 이미 확립되어 있음<br>채용 공고 전용 팩토리 함수(from_cz_mpsv_job_record, from_kr_public_job_record 등) 신설 필요 |
| 수정 후 동작 | JobSchemaContract 및 CanonicalJobRecord 도입하여 키 불일치 엄격 차단 (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 공고 누락 없는 신뢰도 100% 데이터셋 확보 |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: 기존의 취약한 .get('job_id') 딕셔너리 수작업 접근 유지<br>B: JobSchemaContract 및 CanonicalJobRecord 도입하여 키 불일치 엄격 차단 (권장) |
| 수용·거부 조건 | JP-D01-O01: 수용 설명 미등록 / 거부 설명 미등록<br>JP-D01-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | tests/test_job_cluster_signature.py 실행하여 스키마 검증 및 URL 합성 단위 테스트 통과 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 2026-10-18 실시간 정본 복원 및 증강 단계 |
| 이번 판단 | 체코 MPSV의 portal_id와 같이 API별로 상이한 반환 키로 인한 무음 결함(None 누락)을 방어하고, 5계층 ClusterSignature와 결합된 표준 채용 레코드를 어떻게 구축할 것인가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[JP-D01 정본과 상세 근거](decisions/01-jp-d01.json)

### 실시간 API 정본 및 링크 생존성 검증 모듈 (JobProvenanceVerifier)

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | JobProvenanceVerifier 모듈 (HTTP HEAD 프로빙, 마감일 기준 Freshness 자동 계산) |
| 현재 입력 문제 | 각국 공고 URL(JOB-ALIO, MPSV, USAJOBS, ÚPSVaR)은 표준 HTTP 프로토콜로 직접 접근 가능함 |
| 수정 후 동작 | JobProvenanceVerifier를 통해 실시간 상태 및 HTTP 유효성 1:1 증명 (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 사용자가 공고 마감 여부를 한눈에 파악 가능 |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: URL 유효성 검증 없이 단순 텍스트 링크만 출력<br>B: JobProvenanceVerifier를 통해 실시간 상태 및 HTTP 유효성 1:1 증명 (권장) |
| 수용·거부 조건 | JP-D02-O01: 수용 설명 미등록 / 거부 설명 미등록<br>JP-D02-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | tests/test_live_job_provenance.py 실행하여 상태 전이 및 HTTP 검증 테스트 통과 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 2026-10-18 실시간 검증 단계 |
| 이번 판단 | 수집된 채용 공고 URL이 실제로 인터넷상에서 유효한지(HTTP 200 OK) 확인하고, 마감일 기준 실시간 상태를 어떻게 자동으로 판정할 것인가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[JP-D02 정본과 상세 근거](decisions/02-jp-d02.json)

### 6대 공공 채용 엑셀 워크북 체코 URL 100% 복원 및 24열 하이퍼링크 증강

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | generate_six_it_management_workbooks.py 리팩토링 및 6대 워크북 24열 갱신 |
| 현재 입력 문제 | 한국(423건/107건)과 슬로바키아(10건/5건)는 이미 URL 100% 보유 중이었음<br>체코 원천 CSV에는 portal_id가 전수 존재하므로 100% 복원 가능함 |
| 수정 후 동작 | 생성 파이프라인에 JobSchemaContract를 영구 결속하고 24열 하이퍼링크 스키마로 확장 (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 원클릭 브라우저 공고 확인 가능 |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: 체코 URL을 단순 수작업으로 채우기<br>B: 생성 파이프라인에 JobSchemaContract를 영구 결속하고 24열 하이퍼링크 스키마로 확장 (권장) |
| 수용·거부 조건 | JP-D03-O01: 수용 설명 미등록 / 거부 설명 미등록<br>JP-D03-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | tests/test_six_workbooks_provenance.py 실행하여 6개 파일 전체 행(741건)의 URL 100% 보유 검증 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 2026-10-18 워크북 갱신 단계 |
| 이번 판단 | 체코 워크북에서 누락되었던 196건의 URL을 어떻게 100% 복원하고, 6개 워크북 전체를 24열 하이퍼링크 구조로 어떻게 업그레이드할 것인가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[JP-D03 정본과 상세 근거](decisions/03-jp-d03.json)

### CLI 기반 동적 API 반환 속성 점검 및 클러스터 조합 검색·추출 파이프라인

| 읽는 질문 | 내용 |
|---|---|
| 사용자 목적 | list-api-attributes 및 export-cluster-jobs CLI 서브커맨드 |
| 현재 입력 문제 | src/company_intel/cli.py에 main() 엔트리포인트와 서브파서 등록 구조가 이미 완비되어 있음 |
| 수정 후 동작 | CLI 정식 서브커맨드로 표준 인터페이스 개통 (권장) |
| 제품 효과 | 설명 미등록 |
| UX 설명 | 원클릭 터미널 명령어로 속성 확인 및 파일 추출 |
| 생산자·소비자 책임 | 설명 미등록 |
| 대안의 차이 | A: 파이썬 스크립트를 매번 직접 수정하여 실행<br>B: CLI 정식 서브커맨드로 표준 인터페이스 개통 (권장) |
| 수용·거부 조건 | JP-D04-O01: 수용 설명 미등록 / 거부 설명 미등록<br>JP-D04-O02: 수용 설명 미등록 / 거부 설명 미등록 |
| 확인 방법 | tests/test_cli_cluster_jobs.py 실행하여 CLI 인자 처리 및 파일 생성 테스트 통과 |
| 확인 한계 | 설명 미등록 |
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 실행 범위 | 2026-10-18 인터페이스 개통 단계 |
| 이번 판단 | 사용자가 터미널에서 원천 API의 실제 반환 속성을 직접 점검하고, 5계층 ClusterSignature를 조건별로 조합하여 워크북을 추출하는 CLI를 어떻게 구현할 것인가? |
| 조건별 다음 행동 | DISCUSS — 목적·조건·판단 설명의 공백을 보완합니다. |

[JP-D04 정본과 상세 근거](decisions/04-jp-d04.json)

## 캠페인 요약

| 항목 | 값 |
|---|---|
| 현재 실행 범위 | 현재 실행 범위 미확인; 결속된 구현·검사 증거를 조회합니다. |
| 작성 당시 목적·범위 | ClusterSignature 기반 실시간 API 속성 정규화, 키 불일치 방어, 6대 엑셀 하이퍼링크 증강 및 CLI 파이프라인 |
| 캠페인 단계 | draft |
| 현재 검증 | 미완료·상세 상태 확인 |

## 의사결정 요약

| No | 작업 단위 | 상태 | 결정 이름 | 권장안 | 선행 결정 | 사용자 결정 |
|---:|---|---|---|---|---|---|
| 1 | CIL-C09-schema-contract | decision-required | ClusterSignature 기반 CanonicalJobRecord 및 JobSchemaContract 키 불일치 방어 엔진 | B | — | — |
| 2 | CIL-C10-live-provenance-verifier | decision-required | 실시간 API 정본 및 링크 생존성 검증 모듈 (JobProvenanceVerifier) | B | JP-D01 | — |
| 3 | CIL-C11-six-workbooks-url-recovery | decision-required | 6대 공공 채용 엑셀 워크북 체코 URL 100% 복원 및 24열 하이퍼링크 증강 | B | JP-D01<br>JP-D02 | — |
| 4 | CIL-C12-cli-cluster-jobs | decision-required | CLI 기반 동적 API 반환 속성 점검 및 클러스터 조합 검색·추출 파이프라인 | B | JP-D01<br>JP-D03 | — |

## 작업 단위별 검증 상태

| 작업 단위 | 현재 상태 | 이유 |
|---|---|---|

## 검증 실패 조건과 실제 해석

| 실패 코드 | 실패 배치 / 표시된 TU | 검증기가 거부하는 정확한 조건 | 실제 확인과 해석 |
|---|---|---|---|
| — | 관측 자료 없음 | 조건 설명 미등록 | 실패가 없다는 뜻이 아님 |

> 배치 실패로 표시된 TU 수는 각 TU의 독립 오류 수가 아닐 수 있습니다.
> 관측 범위·근거의 신선도를 확인하며, 자료 미등록은 실패 0건을 뜻하지 않습니다.

## Plan·결정별 변경 책임과 완료 경계

| Plan / 결정 | 해결하려는 문제·목표 | 연결된 컴포넌트와 책임 | 현재 프로젝트 동작 변화 | 파일 수 | 의미적 완료 여부 |
|---|---|---|---|---:|---|
| — | plan 미준비 | 연결 자료 없음 | 변화 확인 불가 | 미확인 | 의미적 완료 미확인 |

> 파일 수는 해당 plan·결정에 연결된 고유 변경 경로 수(테스트 포함)입니다.
> 공유 경로 때문에 행별 수를 합산하지 않습니다. 계획상 변화나 차단 기준 통과만으로 의미적 완료를 확정하지 않습니다.

## 의사결정 상세

<details>
<summary>의도·설계 근거가 필요할 때 펼치기</summary>

## 1. ClusterSignature 기반 CanonicalJobRecord 및 JobSchemaContract 키 불일치 방어 엔진 (`JP-D01`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | src/company_intel/classification.py의 ClusterSignature(5계층)가 이미 확립되어 있음 (근거: artifacts/public-sector-inventory-2026-09-16/czech_current_jobs.csv) |
| 바꿀 동작 | JobSchemaContract 및 CanonicalJobRecord 도입하여 키 불일치 엄격 차단 (권장) |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — REQUIRED_CANONICAL_FIELDS 별칭 레지스트리 검증, 키 누락 시 KeyAlignmentError 즉시 발생, MPSV 결정론적 URL 자동 합성 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 공고 누락 없는 신뢰도 100% 데이터셋 확보 |
| 통과를 확인할 증거 | tests/test_job_cluster_signature.py 실행하여 스키마 검증 및 URL 합성 단위 테스트 통과 |
| 미결 선택 | A: 기존의 취약한 .get('job_id') 딕셔너리 수작업 접근 유지; B: JobSchemaContract 및 CanonicalJobRecord 도입하여 키 불일치 엄격 차단 (권장) |

## 2. 실시간 API 정본 및 링크 생존성 검증 모듈 (JobProvenanceVerifier) (`JP-D02`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 각국 공고 URL(JOB-ALIO, MPSV, USAJOBS, ÚPSVaR)은 표준 HTTP 프로토콜로 직접 접근 가능함 (근거: src/company_intel/provenance_validator.py) |
| 바꿀 동작 | JobProvenanceVerifier를 통해 실시간 상태 및 HTTP 유효성 1:1 증명 (권장) |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — 경량 HTTP HEAD 요청, 타임아웃 3초 격리, 마감일 기준 LIVE_ACTIVE / APPROACHING_DEADLINE / CLOSED 태깅 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 사용자가 공고 마감 여부를 한눈에 파악 가능 |
| 통과를 확인할 증거 | tests/test_live_job_provenance.py 실행하여 상태 전이 및 HTTP 검증 테스트 통과 |
| 미결 선택 | A: URL 유효성 검증 없이 단순 텍스트 링크만 출력; B: JobProvenanceVerifier를 통해 실시간 상태 및 HTTP 유효성 1:1 증명 (권장) |

## 3. 6대 공공 채용 엑셀 워크북 체코 URL 100% 복원 및 24열 하이퍼링크 증강 (`JP-D03`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | 한국(423건/107건)과 슬로바키아(10건/5건)는 이미 URL 100% 보유 중이었음 (근거: czech-public-sector-it-management-jobs.xlsx) |
| 바꿀 동작 | 생성 파이프라인에 JobSchemaContract를 영구 결속하고 24열 하이퍼링크 스키마로 확장 (권장) |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — JobSchemaContract 적용, Col 16에 =HYPERLINK() 수식 주입, 마감일/실시간상태/학력 컬럼 증강 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 원클릭 브라우저 공고 확인 가능 |
| 통과를 확인할 증거 | tests/test_six_workbooks_provenance.py 실행하여 6개 파일 전체 행(741건)의 URL 100% 보유 검증 |
| 미결 선택 | A: 체코 URL을 단순 수작업으로 채우기; B: 생성 파이프라인에 JobSchemaContract를 영구 결속하고 24열 하이퍼링크 스키마로 확장 (권장) |

## 4. CLI 기반 동적 API 반환 속성 점검 및 클러스터 조합 검색·추출 파이프라인 (`JP-D04`)

| 구분 | 내용 |
|---|---|
| 현재 문제와 근거 | src/company_intel/cli.py에 main() 엔트리포인트와 서브파서 등록 구조가 이미 완비되어 있음 (근거: src/company_intel/cli.py) |
| 바꿀 동작 | CLI 정식 서브커맨드로 표준 인터페이스 개통 (권장) |
| 수정할 코드 경계 | 목표 경로 2개; 정확한 소유 operation은 plan·결정 표의 링크 참조 — argparse 기반 서브커맨드 등록, classification.py 팩토리 및 JobSchemaContract 호출, 워크북 자동 출력 |
| 프로젝트에서 관찰할 변화 | 요약 검토 필요 |
| 별도의 UX 설명 | 원클릭 터미널 명령어로 속성 확인 및 파일 추출 |
| 통과를 확인할 증거 | tests/test_cli_cluster_jobs.py 실행하여 CLI 인자 처리 및 파일 생성 테스트 통과 |
| 미결 선택 | A: 파이썬 스크립트를 매번 직접 수정하여 실행; B: CLI 정식 서브커맨드로 표준 인터페이스 개통 (권장) |

</details>

## 정본과 상세 근거

- [JP-D01 정본 JSON](decisions/01-jp-d01.json)
- [JP-D02 정본 JSON](decisions/02-jp-d02.json)
- [JP-D03 정본 JSON](decisions/03-jp-d03.json)
- [JP-D04 정본 JSON](decisions/04-jp-d04.json)
- [캠페인 정본](campaign.json)


## 변경점 상세

고유 파일 0개 · operation 0개. 컴포넌트 수는 선언된 inventory가 없어 미집계합니다. 파일 수와 기능 수는 다릅니다.

<details>
<summary>모든 소유 변경점과 개별 책임</summary>



</details>
