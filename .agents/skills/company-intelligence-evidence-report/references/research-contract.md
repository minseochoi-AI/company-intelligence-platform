# S08 조사 실행 계약

책임: 사실 입력을 변경하지 않고 AI 해석을 작성·검증한다. 먼저 manifest와 각 파일 해시를 확인한다. ai-input.json의 허용 자료로 report.md와 research-claims-v1 claims.json을 작성한다. 주장은 table_id·row_id·column_id에 연결한다. 수치·단위는 봉인된 값과 같아야 한다. 추론·가정·제안은 assumptions를 붙인다. fixture/demo는 시연이라고 밝힌다. 검증기는 참조·숫자·변조만 확인하며 문장 전체 의미의 진실성을 보장하지 않는다.

요청은 `cil_contracts.requests.ReportRequest` v2.0.0 한 parser를 사용한다. `sealed bundle path, manifest_sha256, narrative, claims, report_spec`를 [구현된 요청 계약](../../../../packages/contracts/src/cil_contracts/requests.py)의 허용 이름으로 입력한다. 지원하지 않는 root·nested 옵션은 거부한다. 5축 시그니처는 선택 공고·상세 필터·계산·표현 옵션을 대신하지 않는다.

```bash
company-intel research validate --request request.json --snapshot snapshot.json
company-intel research run --request request.json --snapshot snapshot.json --output artifacts/research
company-intel research verify --bundle artifacts/research/RUN_ID --manifest-sha256 HASH
company-intel research report --bundle artifacts/research/RUN_ID --manifest-sha256 HASH --narrative report.md --claims claims.json
```

validate/run은 saved snapshot만 소비한다. AI 호출·provider refresh 없이 원천 보존→정규화·계산→17개 논리 dataset→결정론적 XLSX→해시 manifest를 생성한다. 출력의 source_kind와 unknown/conflict·GapsConflicts·Lineage를 함께 읽는다. PARTIAL은 근거 공백이 있는 조사 결과다. NEEDS_INPUT/NEEDS_EVIDENCE는 성공한 결과가 아니다.

보고서 작성자는 `ai-input.json`과 `cell-refs.json`을 읽는다. 원천 전체와 개인 profile은 기본 AI 투영에 포함하지 않는다. selected_skills는 호출 경로 제안이며 실제 에이전트 실행 기록이 아니다. fact run은 narrative_status=not_generated로 봉인한다. AI 보고서는 모든 실질적인 문장을 주장에 연결하고 별도 reports namespace에 저장한다. 사실·제안·시연을 구별하고 자료의 모집단·단위·시점을 그대로 해석한다.

표준 결과: Run, Sources, RawFields, Postings, Requirements, Competition, FinancialHistory, WageBenchmarks, TaskExposure, CareerEvidence, OpportunityEvidence, Scenarios, ProposedPaths, PortfolioPlans, VentureHypotheses, GapsConflicts, Lineage. report_spec의 시트·열 투영은 봉인된 전체 facts와 raw archive를 삭제하지 않는다.
