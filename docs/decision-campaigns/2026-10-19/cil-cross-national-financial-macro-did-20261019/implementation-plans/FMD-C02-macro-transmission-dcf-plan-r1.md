# Implementation plan: FMD-C02-macro-transmission-dcf-plan-r1

Status: `contract-ready`

## FMD-C02-macro-transmission-dcf-S01: 거시경제 큐브 연동 3대 파급효과 및 동적 DCF 파이프라인

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| BEA/Eurostat 실질 GDP 및 ECOS/FRED 금리 시계열이 단편적 프로브로만 존재하고 로컬 다차원 큐브 미적재 | `macro_cubes.py`를 신설하여 분기별 실질 GDP, 환율, 기준금리 시계열을 DuckDB 테이블 `macro_observations_ts`에 통합 적재 | 거시 충격 시나리오 분석에 필요한 정본 관측치 기반을 로컬 웨어하우스에 구축하기 위함 | FMD-C02-K01 | CREATE | src/company&#95;intel/macro&#95;cubes.py | FMD-D02<br>FMD-D02-O01 | BEACubeLoader<br>EurostatCubeLoader<br>load&#95;macro&#95;cube | file-change-fmd-d02-01 | — |
| DCF 할인율(WACC=9%) 및 FCF 마진이 고정 상수로 하드코딩되어 금리·환율 변동 파급효과 미반영 | 기준금리 변동 시 CAPM Ke와 WACC를 동적 재계산하고, 환율 변동률 기반 FCF 마진 탄력성을 결합하는 `dynamic_macro_linked_dcf` 구현 | 금리 인하(3.50%->3.25%)가 기업 적정가치와 안전마진(+28.5%)에 미치는 충격 민감도를 실측하기 위함 | FMD-C02-K01 | MODIFY | src/company&#95;intel/analytics.py | FMD-D02<br>FMD-D02-O02 | dynamic&#95;macro&#95;linked&#95;dcf<br>calculate&#95;dynamic&#95;wacc | file-change-fmd-d02-02 | file-change-fmd-d02-01 |
| 거시 연동 DCF 감응도 단위 테스트 부재 | 단위 테스트 작성하여 금리 50bp 인하 시 WACC 하락 및 적정주가 상승 방향성 정밀 검증 | 재무 가치평가 수학적 무결성 보장 | FMD-C02-K01 | CREATE | tests/test&#95;macro&#95;linked&#95;dcf.py | FMD-D02<br>FMD-D02-O02 | test&#95;dynamic&#95;wacc&#95;sensitivity<br>test&#95;fx&#95;margin&#95;elasticity | file-change-fmd-d02-03 | file-change-fmd-d02-02 |

### Completion criteria

- `FMD-C02-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=FMD-D02-O01, FMD-D02-O02, changes=file-change-fmd-d02-01, file-change-fmd-d02-02, file-change-fmd-d02-03: 거시경제 큐브 연동 3대 파급효과 및 동적 DCF 파이프라인
