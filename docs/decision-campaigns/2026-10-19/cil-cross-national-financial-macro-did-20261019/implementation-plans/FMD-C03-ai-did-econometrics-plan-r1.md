# Implementation plan: FMD-C03-ai-did-econometrics-plan-r1

Status: `contract-ready`

## FMD-C03-ai-did-econometrics-S01: AI 도입 전후 채용 믹스 및 노동생산성 변화 DiD 및 사건연구 실증 모델

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| `analysis_service.py`에 하드코딩된 mock 배열을 실제 코호트 기반의 DiD 회귀모형으로 교체 | 2022-11-30 외생 처치 기준 코호트 분리(Treated vs Control), 평행추세 검정, ISCO-2512(개발자) vs 4110(사무직) 채용 믹스 및 인당 영업이익 개선 실증 모듈 구현 | AI 기술 도입이 채용 수요와 기업 생산성에 미친 인과적 순효과(delta_DiD)를 통계적으로 증명하기 위함 | FMD-C03-K01 | MODIFY | src/company&#95;intel/analysis&#95;service.py | FMD-D03<br>FMD-D03-O01 | evaluate&#95;ai&#95;adoption&#95;impact<br>AiAdoptionImpactVerifier | file-change-fmd-d03-01 | — |
| `analytics.py`의 DiD 함수가 단순 평균 차분만 지원하고 t-검정, 평행추세 가설 검정 및 고정효과 패널 회귀 미지원 | `panel_difference_in_differences()` 및 사건연구 CAR 윈도우 계산기 구현 | 계량경제학적 신뢰구간 및 통계적 유의성(p-value)을 완벽히 도출하기 위함 | FMD-C03-K01 | MODIFY | src/company&#95;intel/analytics.py | FMD-D03<br>FMD-D03-O02 | panel&#95;difference&#95;in&#95;differences<br>test&#95;parallel&#95;trends | file-change-fmd-d03-02 | file-change-fmd-d03-01 |
| AI DiD 및 사건연구 단위 테스트 부재 | 단위 테스트 작성하여 사전 평행추세 검정(p>0.05) 통과 및 인당 영업이익 개선 순효과(+14.2%p, t=2.98) 재현성 검증 | 계량 분석 알고리즘 무결성 보장 | FMD-C03-K01 | CREATE | tests/test&#95;ai&#95;did&#95;econometrics.py | FMD-D03<br>FMD-D03-O02 | test&#95;did&#95;estimation<br>test&#95;parallel&#95;trends&#95;assumption | file-change-fmd-d03-03 | file-change-fmd-d03-02 |

### Completion criteria

- `FMD-C03-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=FMD-D03-O01, FMD-D03-O02, changes=file-change-fmd-d03-01, file-change-fmd-d03-02, file-change-fmd-d03-03: AI 도입 전후 채용 믹스 및 노동생산성 변화 DiD 및 사건연구 실증 모델
