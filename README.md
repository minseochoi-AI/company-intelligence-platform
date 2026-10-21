# Company Intelligence Platform

선택한 채용 공고·기업·직무의 저장 근거를 비교한다. 5축 클러스터 시그니처와 명시한 조사 요청으로 결정론적 Excel을 만들고, AI 해석 보고서는 봉인한 결과의 별도 파생물로 검증한다.

## 설치와 실행

Python 3.11 이상, uv workspace를 사용한다.

```bash
uv sync --all-extras --locked
uv run --locked --no-sync company-intel cluster-spec
uv run --locked --no-sync company-intel research validate --request request.json --snapshot snapshot.json
uv run --locked --no-sync company-intel research run --request request.json --snapshot snapshot.json --output artifacts/research
uv run --locked --no-sync company-intel research verify --bundle artifacts/research/RUN_ID --manifest-sha256 HASH
uv run --locked --no-sync company-intel research report --bundle artifacts/research/RUN_ID --manifest-sha256 HASH --narrative report.md --claims claims.json
```

명령은 `--help`로 인자를 확인한다. 저장된 자료의 `source_kind`는 observed/fixture/demo/unknown을 구별한다. `tests/research/fixtures`의 예시는 시연 자료다. 샘플 실행의 검증 성공은 실시간 API 수신 성공을 뜻하지 않는다.

`research`는 provider 호출이나 모델 호출을 하지 않는다. 사용자가 확정한 JSON과 저장 snapshot을 읽어 17개 논리 dataset, 원문 archive, cell 참조, 재현 가능한 XLSX, 파일 해시 manifest를 생성한다. NEEDS_INPUT·NEEDS_EVIDENCE는 실행 입력 부족, PARTIAL은 근거 공백이 남은 결과다. 알 수 없는 값은 0이나 임의의 수치로 채우지 않는다.

## 책임과 경로

| 경로 | 책임 | 의존 방향 |
|---|---|---|
| packages/contracts / cil_contracts | 요청·원천·결과 계약, 버전별 schema | 표준 라이브러리 |
| packages/domain / cil_domain | 필터·지표·비교·관계 검증 | contracts |
| packages/application / cil_application | 실행 순서·권한·포트·봉인 | domain, contracts |
| packages/integrations / cil_integrations | provider, 저장소, HTTP, 환경·리소스 | 내부 포트·계약 |
| packages/reporting / cil_reporting | 표·Excel의 결정론적 투영 | domain, contracts |
| apps/cli / cil_cli | 인자·조합·console 진입점 | application + 실제 어댑터 |
| apps/api / cil_api | HTTP 요청·조합·응답 | application + 실제 어댑터 |
| src/company_intel | 기존 공개 import 호환 | 명시한 정본 심볼 재노출 |

내부 코드는 정본 `cil_*` 경로를 사용한다. `sys.path` 조작이나 `import *`로 경계를 우회하지 않는다. 환경값의 상대 artifact 경로는 선택한 project root를 기준으로 해소한다. 기본 provider catalog와 SQL은 wheel 리소스에 포함한다.

## 입력과 해석

`ReportRequest` v2.0.0의 purpose는 selected-posting/financial/work-future/path/portfolio/venture를 선택한다. 시그니처는 Region:Sector:Tier:Contract:Workplace의 5개 축이다. 상세 API 필터·자격 조건·기간·계산법·표현 옵션은 별도 명명 필드다. 새 축이나 알 수 없는 옵션을 묵인하지 않는다. 각 인자의 출처는 argument_origins에 기록한다.

경쟁률은 같은 전형·직무·지역·시점의 공식 분모를 요구한다. 개인 합격확률을 만들지 않는다. 재무 비교는 공개 시점·연결 범위·통화·단위·기간을 맞춘다. AI 노출은 업무 구성과 연구 척도에 따른 값이며 개인 대체확률이 아니다. 임금 연환산은 명시한 근무시간·지급 횟수와 통화를 보존한다.

내부 트랙은 조직 구조, 역할, 이동 관계를 구별한다. 직업 유사도나 외부 프레임워크를 회사 승진 규정으로 바꾸지 않는다. 포트폴리오와 창업은 근거에 연결한 실험 제안이다. 공개 이슈를 유료 수요나 관측 매출로 바꾸지 않는다.

## API 확장과 보고서

`CapabilityRegistry`에 operation·provider·schema version·field 의미·grain·권리를 등록하고 정규화 어댑터를 연결한다. `ingest_saved`는 명시한 원문 페이지의 새 키와 False/0/null을 보존한다. 미완료 페이지와 unknown은 coverage·gap에 남긴다. 등록 수, provider 수, 의미 매핑 수, 실제 응답 전체 키 수는 다른 지표다. 새 실제 API 통합은 별도 인증·응답·페이지·권리 확인이 필요하다.

Excel 생성은 AI와 네트워크를 사용하지 않는다. AI가 작성한 경로·시나리오·개발/창업 제안은 proposals namespace에 분리된다. AI 보고서는 허용 투영과 봉인된 table/row/column 참조를 사용한다. 검증은 해시·참조·정확한 숫자와 단위를 확인한다. 문장 전체 의미와 현실 자료의 진실성은 사람의 내용 검토가 필요하다.

Codex 스킬 정본은 `.agents/skills`의 S01~S08이다. 목적별 최소 스킬만 사용한다. 상세 사용법은 [조사 프로토콜](docs/skill-protocols/research-skills.md)에 있다. `.codex/skills`는 예전 경로의 포인터이며 v1 interop artifact는 그대로 유지한다.

이전 6개 XLSX는 역사 자료다. 재생성은 명시한 인스턴스 목록을 `scripts/generate_six_it_management_workbooks.py --instances ... --output ...`으로 전달한다. 파일 수·국가·학위·에너지 관심사를 제품 기본값으로 고정하지 않는다.

## 검증

```bash
uv run --locked --no-sync python -m pytest -q
```

브라우저 렌더 검증은 Chromium을 실행할 수 있는 로컬 환경이 필요하다. 임시 DB 테스트는 운영 DB와 분리한다. 기존 Excel의 자체 PASS 문구를 원천 검증으로 사용하지 않는다. 봉인되지 않은 문서는 UNVERIFIED로 남긴다.
