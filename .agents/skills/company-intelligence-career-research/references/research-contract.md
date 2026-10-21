# S02 조사 실행 계약

책임: 공고 요건과 사용자 증빙을 대조한다. 필수·우대·결격을 분리한다. 검토 전 AI 추출문은 미확인이다. 공식 지원자/모집인원 또는 합격자/응시인원은 동일 회차·직무·지역·단계·마감시각으로만 나눈다. 클릭 수는 지원자 수가 아니다. 개인 합격확률을 산출하지 않는다.

요청은 `cil_contracts.requests.ReportRequest` v2.0.0 한 parser를 사용한다. `subject_refs, profile_ref, requirement_policy, competition_spec, history, as_of`를 [구현된 요청 계약](../../../../packages/contracts/src/cil_contracts/requests.py)의 허용 이름으로 입력한다. 지원하지 않는 root·nested 옵션은 거부한다. 5축 시그니처는 선택 공고·상세 필터·계산·표현 옵션을 대신하지 않는다.

```bash
company-intel research validate --request request.json --snapshot snapshot.json
company-intel research run --request request.json --snapshot snapshot.json --output artifacts/research
company-intel research verify --bundle artifacts/research/RUN_ID --manifest-sha256 HASH
company-intel research report --bundle artifacts/research/RUN_ID --manifest-sha256 HASH --narrative report.md --claims claims.json
```

validate/run은 saved snapshot만 소비한다. AI 호출·provider refresh 없이 원천 보존→정규화·계산→17개 논리 dataset→결정론적 XLSX→해시 manifest를 생성한다. 출력의 source_kind와 unknown/conflict·GapsConflicts·Lineage를 함께 읽는다. PARTIAL은 근거 공백이 있는 조사 결과다. NEEDS_INPUT/NEEDS_EVIDENCE는 성공한 결과가 아니다.

보고서 작성자는 `ai-input.json`과 `cell-refs.json`을 읽는다. 원천 전체와 개인 profile은 기본 AI 투영에 포함하지 않는다. selected_skills는 호출 경로 제안이며 실제 에이전트 실행 기록이 아니다. fact run은 narrative_status=not_generated로 봉인한다. AI 보고서는 모든 실질적인 문장을 주장에 연결하고 별도 reports namespace에 저장한다. 사실·제안·시연을 구별하고 자료의 모집단·단위·시점을 그대로 해석한다.

표준 결과: Run, Sources, RawFields, Postings, Requirements, Competition, FinancialHistory, WageBenchmarks, TaskExposure, CareerEvidence, OpportunityEvidence, Scenarios, ProposedPaths, PortfolioPlans, VentureHypotheses, GapsConflicts, Lineage. report_spec의 시트·열 투영은 봉인된 전체 facts와 raw archive를 삭제하지 않는다.
