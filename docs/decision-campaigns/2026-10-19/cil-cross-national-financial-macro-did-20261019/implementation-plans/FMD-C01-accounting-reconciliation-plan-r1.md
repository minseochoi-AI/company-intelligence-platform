# Implementation plan: FMD-C01-accounting-reconciliation-plan-r1

Status: `contract-ready`

## FMD-C01-accounting-reconciliation-S01: 3국 이기종 회계기준 달력분기 동기화 및 4대 핵심 재무비율 크로스워크 계약

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 한국(12월 결산), 미국(애플 9월, MS 6월 결산), 체코 회계분기 불일치로 직접 시계열 비교 시 3개월 시차 왜곡 발생 | `CalendarQuarterNormalizer`를 구축하여 보고기간 종료일(`period_end_date`) 기준 `CY-YYYY-Qk` 글로벌 달력 분기로 일원화 정렬 및 손익 YTD 순발생액 차분 계산 | 동일 시계열 슬라이스에서 거시 충격(금리·환율)과 기업 재무 간 인과관계를 정확히 동기화하기 위함 | FMD-C01-K01 | MODIFY | src/company&#95;intel/normalization.py | FMD-D01<br>FMD-D01-O01 | CalendarQuarterNormalizer<br>normalize&#95;to&#95;calendar&#95;quarter<br>calculate&#95;quarterly&#95;flow | file-change-fmd-d01-01 | — |
| DART(K-IFRS), SEC(US-GAAP), ARES(CAS)의 서로 다른 계정과목 태그로 인해 유동비율, 당좌비율, 부채비율, ICR 산출 혼선 | 4대 핵심 재무비율 크로스워크 매핑 계약을 선언적 매핑 테이블로 확립하고 이상치(변동률 > 50%) 가드 장착 | 국가 간 회계 택소노미 불일치를 해소하고 왜곡 없는 유동성·부채비율을 보장하기 위함 | FMD-C01-K01 | MODIFY | src/company&#95;intel/analytics.py | FMD-D01<br>FMD-D01-O02 | CROSSWALK&#95;FINANCIAL&#95;METRICS<br>reconcile&#95;cross&#95;national&#95;financials | file-change-fmd-d01-02 | file-change-fmd-d01-01 |
| 3국 달력분기 동기화 및 핵심비율 검증 테스트 부재 | 단위 테스트 작성하여 애플 9월 결산과 카카오 12월 결산이 `CY2023-Q4`로 정상 정렬되는지 검증 | 무음 결함 방지 및 시계열 연속성 보장 | FMD-C01-K01 | CREATE | tests/test&#95;calendar&#95;quarter&#95;reconciliation.py | FMD-D01<br>FMD-D01-O01 | test&#95;calendar&#95;quarter&#95;normalization<br>test&#95;cross&#95;national&#95;ratios | file-change-fmd-d01-03 | file-change-fmd-d01-02 |

### Completion criteria

- `FMD-C01-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=FMD-D01-O01, FMD-D01-O02, changes=file-change-fmd-d01-01, file-change-fmd-d01-02, file-change-fmd-d01-03: 3국 이기종 회계기준 달력분기 동기화 및 4대 핵심 재무비율 크로스워크 계약
