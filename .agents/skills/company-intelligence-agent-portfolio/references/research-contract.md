# S06 조사 실행 계약

책임: 관측된 업무와 작성한 개발 실험을 연결한다. 대상 업무·gap_refs·기존 방식 baseline·평가 데이터·지표·실패 조건·데이터 권리·예산 통화를 기록한다. 공개 이슈는 문제 근거이며 유료 수요 증거가 아니다. 개발 완료·채용 성공으로 보고하지 않는다. 실제 구현은 별도 사용자 작업 범위다.

요청은 `cil_contracts.requests.ReportRequest` v2.0.0 한 parser를 사용한다. `portfolio_spec, profile_ref, subject_refs, role_mapping_ref, as_of`를 [구현된 요청 계약](../../../../packages/contracts/src/cil_contracts/requests.py)의 허용 이름으로 입력한다. 지원하지 않는 root·nested 옵션은 거부한다. 5축 시그니처는 선택 공고·상세 필터·계산·표현 옵션을 대신하지 않는다.

```bash
company-intel research validate --request request.json --snapshot snapshot.json
company-intel research run --request request.json --snapshot snapshot.json --output artifacts/research
company-intel research verify --bundle artifacts/research/RUN_ID --manifest-sha256 HASH
company-intel research report --bundle artifacts/research/RUN_ID --manifest-sha256 HASH --narrative report.md --claims claims.json
```

validate/run은 saved snapshot만 소비한다. AI 호출·provider refresh 없이 원천 보존→정규화·계산→17개 논리 dataset→결정론적 XLSX→해시 manifest를 생성한다. 출력의 source_kind와 unknown/conflict·GapsConflicts·Lineage를 함께 읽는다. PARTIAL은 근거 공백이 있는 조사 결과다. NEEDS_INPUT/NEEDS_EVIDENCE는 성공한 결과가 아니다.

보고서 작성자는 `ai-input.json`과 `cell-refs.json`을 읽는다. 원천 전체와 개인 profile은 기본 AI 투영에 포함하지 않는다. selected_skills는 호출 경로 제안이며 실제 에이전트 실행 기록이 아니다. fact run은 narrative_status=not_generated로 봉인한다. AI 보고서는 모든 실질적인 문장을 주장에 연결하고 별도 reports namespace에 저장한다. 사실·제안·시연을 구별하고 자료의 모집단·단위·시점을 그대로 해석한다.

표준 결과: Run, Sources, RawFields, Postings, Requirements, Competition, FinancialHistory, WageBenchmarks, TaskExposure, CareerEvidence, OpportunityEvidence, Scenarios, ProposedPaths, PortfolioPlans, VentureHypotheses, GapsConflicts, Lineage. report_spec의 시트·열 투영은 봉인된 전체 facts와 raw archive를 삭제하지 않는다.
