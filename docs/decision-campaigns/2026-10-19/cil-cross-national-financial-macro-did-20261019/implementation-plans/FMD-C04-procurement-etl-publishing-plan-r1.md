# Implementation plan: FMD-C04-procurement-etl-publishing-plan-r1

Status: `contract-ready`

## FMD-C04-procurement-etl-publishing-S01: KONEPS 조달 어댑터, DuckDB 증분 ETL, 서킷브레이커 및 노션-Blogger 배포

### 바꿀 동작과 확인

| 현재 문제 | 바꿀 동작 | 수정 이유 | 확인 기준 | Operation | Path | Decisions / Obligations | Symbols | ID | Dependencies |
|---|---|---|---|---|---|---|---|---|---|
| 공공조달 커버리지에 한국 조달청 나라장터(KONEPS) 부재 | `koneps.py` 어댑터를 구축하여 공공데이터포털 입찰/낙찰 정보를 `CanonicalProcurementRecord`로 정규화 수집 | 한국 공공조달 계약 수주 기업 식별을 가능하게 하기 위함 | FMD-C04-K01 | CREATE | src/company&#95;intel/connectors/koneps.py | FMD-D04<br>FMD-D04-O01 | KONEPSConnector<br>normalize&#95;koneps&#95;bid | file-change-fmd-d04-01 | — |
| `warehouse.py`가 전체 재적재 방식으로만 동작하여 API 쿼터 소진 및 중복 발생 | DuckDB `etl_sync_watermarks` 테이블 기반 증분 적재(Incremental Sync) 엔진 구축 | `last_modified` 이후 신규/수정 레코드만 머지하여 API 호출량을 90% 절감하기 위함 | FMD-C04-K01 | MODIFY | src/company&#95;intel/warehouse.py | FMD-D04<br>FMD-D04-O02 | incremental&#95;sync<br>get&#95;watermark | file-change-fmd-d04-02 | file-change-fmd-d04-01 |
| API 호출 한도 초과 시 연속 429로 인한 IP 밴 위험 상존 | Provider별 토큰 버킷 버퍼 및 연속 3회 실패 시 60초 자동 격리 서킷 브레이커 미들웨어 구축 | 샌드박스 안정성 및 쿼터 관리 무결성을 보장하기 위함 | FMD-C04-K01 | CREATE | src/company&#95;intel/middleware/rate&#95;limiter.py | FMD-D04<br>FMD-D04-O03 | TokenBucket<br>CircuitBreaker<br>intercept&#95;request | file-change-fmd-d04-03 | file-change-fmd-d04-02 |
| 노션 결재 큐가 프로세스 재시작 시 휘발되고, Blogger 자동 배포 CLI 부재 | `data/notion_queue.json` 영속 큐 연동 및 `cil publish-blog --from-notion` CLI 원클릭 배포 파이프라인 완성 | 스마트폰에서 '발행 승인' 시 즉시 애드센스 HTML로 블로그 자동 발행을 실현하기 위함 | FMD-C04-K01 | MODIFY | src/company&#95;intel/cli.py | FMD-D04<br>FMD-D04-O04 | notion&#95;sync&#95;command<br>publish&#95;blogger&#95;command | file-change-fmd-d04-04 | file-change-fmd-d04-03 |

### Completion criteria

- `FMD-C04-K01` [planned] `decision-campaign-workbook` phase=VALIDATE, depends=-, obligations=FMD-D04-O01, FMD-D04-O02, FMD-D04-O03, FMD-D04-O04, changes=file-change-fmd-d04-01, file-change-fmd-d04-02, file-change-fmd-d04-03, file-change-fmd-d04-04: KONEPS 조달 어댑터, DuckDB 증분 ETL, 서킷브레이커 및 노션-Blogger 배포
