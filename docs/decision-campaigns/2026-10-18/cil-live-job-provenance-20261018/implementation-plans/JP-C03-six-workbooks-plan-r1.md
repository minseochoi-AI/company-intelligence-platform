# Implementation plan: JP-C03-six-workbooks-plan-r1

Status: `contract-ready`

## JP-C03-six-workbooks-S01: 6대 공공 채용 엑셀 워크북 체코 URL 100% 복원 및 24열 하이퍼링크 증강

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 체코 196건 공고 URL 누락(0.0%) 및 단순 텍스트 URL로 클릭 불가 | `portal_id` 정규 바인딩으로 체코 URL 100% 복원 및 Col 16에 `=HYPERLINK()` 수식과 실시간 상태/마감일/학력 열 추가(총 24열 확장) | 엑셀에서 원클릭으로 웹 공고를 바로 확인하고, 실시간 마감 여부를 판별하기 위함 | JP-C03-six-workbooks-K01 | MODIFY | scripts/generate&#95;six&#95;it&#95;management&#95;workbooks.py | JP-D03<br>JP-D03-O01 | generate&#95;file&#95;1&#95;kr&#95;bachelor<br>generate&#95;file&#95;2&#95;cz&#95;prague&#95;bachelor<br>style&#95;worksheet | file-change-jp-d03-01 | file-change-jp-d01-01, file-change-jp-d02-01 |
| 6개 워크북의 물리적 URL 복원율 및 하이퍼링크 검증 부재 | 6개 워크북 전수 물리적 검증 테스트 작성 (741건 전수 URL 100% 보유 검증) | 체코 URL 보유율 0% -> 100% 복원 및 하이퍼링크 수식 무결성 검증 | JP-C03-six-workbooks-K01 | CREATE | tests/test&#95;six&#95;workbooks&#95;provenance.py | JP-D03<br>JP-D03-O02 | test&#95;six&#95;workbooks&#95;url&#95;coverage<br>test&#95;hyperlink&#95;formula&#95;syntax | file-change-jp-d03-02 | file-change-jp-d03-01 |

<details>
<summary>정확한 원본·결과 해시</summary>

| ID | Source hash | Result hash |
|---|---|---|
| file-change-jp-d03-01 | — | — |
| file-change-jp-d03-02 | — | — |

</details>

### Routed skills

- JP-C03-six-workbooks-route → decision-campaign-workbook (VALIDATE, required): 6개 엑셀 파일 재생성 및 물리적 검증

### Completion criteria

- `JP-C03-six-workbooks-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=JP-C01-schema-contract-K01, JP-C02-live-provenance-K01, obligations=JP-D03-O01, JP-D03-O02, changes=file-change-jp-d03-01, file-change-jp-d03-02: 6대 공공 채용 엑셀 워크북 체코 URL 100% 복원 및 24열 하이퍼링크 증강
