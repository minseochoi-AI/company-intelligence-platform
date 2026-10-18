# Implementation plan: JP-C04-cli-pipeline-plan-r1

Status: `contract-ready`

## JP-C04-cli-pipeline-S01: CLI 기반 동적 API 반환 속성 점검 및 클러스터 조합 검색·추출 파이프라인

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 원천 API의 반환 속성을 터미널에서 점검하거나 동적 클러스터 시그니처로 워크북을 추출하는 CLI 부재 | `list-api-attributes` 및 `export-cluster-jobs` CLI 명령어 추가 | 사용자가 API 원천 반환 속성을 직접 확인하고 조건별(지역, 부문, 계약, 학위 등)로 워크북을 자유롭게 추출하기 위함 | JP-C04-cli-pipeline-K01 | MODIFY | src/company&#95;intel/cli.py | JP-D04<br>JP-D04-O01 | list&#95;api&#95;attributes&#95;cmd<br>export&#95;cluster&#95;jobs&#95;cmd | file-change-jp-d04-01 | file-change-jp-d01-01, file-change-jp-d03-01 |
| CLI 클러스터 검색 및 속성 점검 테스트 부재 | CLI 서브커맨드 실행 및 엑셀 출력 회귀 테스트 작성 | CLI 인자 파싱 및 엑셀 파일 생성 정상 동작 검증 | JP-C04-cli-pipeline-K01 | CREATE | tests/test&#95;cli&#95;cluster&#95;jobs.py | JP-D04<br>JP-D04-O02 | test&#95;cli&#95;list&#95;api&#95;attributes<br>test&#95;cli&#95;export&#95;cluster&#95;jobs | file-change-jp-d04-02 | file-change-jp-d04-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-jp-d04-01 | — | — |
| file-change-jp-d04-02 | — | — |

</details>

### Routed skills

- JP-C04-cli-pipeline-route → decision-campaign-workbook (VALIDATE, required): CLI 서브커맨드 테스트 검증

### Completion criteria

- `JP-C04-cli-pipeline-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=JP-C01-schema-contract-K01, JP-C03-six-workbooks-K01, obligations=JP-D04-O01, JP-D04-O02, changes=file-change-jp-d04-01, file-change-jp-d04-02: CLI 기반 동적 API 반환 속성 점검 및 클러스터 조합 검색·추출 파이프라인
