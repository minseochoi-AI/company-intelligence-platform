# Blogger 4관점 보고서: 통합 결정 행렬

2026-10-13. 이번 작업의 종료 경계는 PREPARE이며 설치·구현·외부 게시가 아니다.

| No | Status | Target file / current component | 5W1H | Parameters | After state | Dependencies (class.function) | Validation and change proposal |
|---|---|---|---|---|---|---|---|
| I01 | investigate | apps/company-report-blog/src/report_blog/blogger.py / 게시 adapter 없음 | 소유자가 수동 실행할 때 검토된 HTML을 자기 Blogger에 전달; CIL 계산은 복제하지 않음 | Blogger v3; OAuth blogger; 읽기 timeout 30s, 최대 3회; insert는 자동 retry 금지 | 초안 생성·기존 ID 갱신·실패 후 원격 대조; 중복 생성 방지 | googleapiclient.discovery.build; Resource.posts; HttpRequest.execute | insert timeout을 성공/실패로 추정하지 않고 장부 pending으로 보존; 재실행 중복 검사 |
| I02 | investigate | apps/company-report-blog/src/report_blog/render.py / HTML 구성기 없음 | 구성기가 한 보고서의 네 시선과 사실/AI/사람 영역을 로컬에서 결합; 작성자 평가를 생성기로 덮어쓰지 않음 | Jinja Environment autoescape=True; StrictUndefined; 신뢰된 템플릿만; 비신뢰 HTML safe 금지 | 동일 입력은 동일 HTML; 사용자 평가와 출처 유지 | jinja2.Environment; Template.render | HTML injection, 누락 필드, 네 관점·작성자 revision 보존 시험 |
| I03 | investigate | apps/company-report-blog/src/report_blog/taxonomy.py / Blogger 폴더 없음 | 산업별 부모·자식과 독자 네 관점을 로컬 정본에서 관리하고 Blogger 라벨·목차로 투영 | labels[]; 단일 canonical report_id; index-post는 장부에 별도 content_key | 실제 중첩 폴더라 주장하지 않는 가상 분류; 산업·기업·직종·보고서 간 링크 | Blogger posts resource; posts.list/get/patch | 라벨 생성·중복 보고서 방지·목차 갱신·끊긴 링크 검사 |
| I04 | investigate | apps/company-report-blog/src/report_blog/metrics.py / 성과 API 없음 | 작성자는 실행 후 소유 사이트의 유입·수익만 관측; 분석상의 평가와 트래픽 점수를 분리 | AdSense v2 readonly; Search Console v1 readonly; 계정·기간·통화 명시 | 클릭·노출과 확인 가능한 수익 집계; 없는 페이지별 매출 배분은 미확인 | discovery.build; accounts.reports.generate; searchanalytics.query | account 미연동은 unknown이지 매출 0이 아님; 페이지 매핑·측정 범위 시험 |

표를 먼저 작성하고 I01/I02의 lifecycle·실패 의미만 DeepWiki에 질의한다. SDK wiki의 오래된 버전·Python 지원 설명은 설치 버전 확정 근거로 사용하지 않는다.

## 행별 질의 후 최종 판정

| 행 | 최종 상태 | 확인한 경계 | 남은 실행 전제 |
|---|---|---|---|
| I01 | ready-for-implementation | build + 사용자 OAuth; posts.insert(isDraft=True), posts.patch, list_next; HttpMockSequence; insert blind retry는 중복 위험 | 소유 blog_id·OAuth·원격 쓰기 실행 승인; 실제 provider 검증 미수행 |
| I02 | ready-for-implementation | Environment(loader=PackageLoader(...), autoescape=True, undefined=StrictUndefined); URL scheme 검사는 자체 구현 | 정확한 lock 버전의 로컬 반례시험; 의견 입력 채널은 저장 소유권과 분리된 사용자 선택 |
| I03 | ready-for-implementation | 공식 Posts labels[] 및 HTML 목차로 가상 분류; hierarchy는 로컬 taxonomy 정본 | 라벨/목차의 실계정 렌더 확인; Blogger 테마 변경은 제외 |
| I04 | ready-for-implementation | 공식 AdSense v2/웹마스터 API의 typed read-only adapter; 페이지 매출 매핑은 관측 결과에 한정 | 계정/사이트 소유 권한·지원 dimensions 확인 전 성과값 unknown |

ready는 인터페이스·실패 처리·시험 계획이 준비되었다는 뜻이며 설치/실계정 연동/게시/성과 검증 완료를 의미하지 않는다.
I01: [DeepWiki 행별 응답](https://deepwiki.com/search/given-matrix-i01i04-producer-v_08d14238-51c6-4a4e-aa7c-43e3fc909fee).
I02: [DeepWiki 행별 응답](https://deepwiki.com/search/given-i02-trusted-packaged-tem_7e339e04-97e4-429b-947c-12440d09f0d4).
I03/I04: product-contract-ko.md의 공식 REST 자료와 대조했다. SDK wiki가 해당 서비스의 구체적 보장까지 답하지 못한 부분은 공식 REST 계약으로 보완했다.
인증된 transport는 AuthorizedHttp(credentials, http=httplib2.Http(timeout=30))를 만든 뒤 build에 http로 전달한다. http와 credentials를 동시에 build에 전달하지 않는다. 쓰기는 execute(num_retries=0); 읽기는 bounded retry로 분리한다. 원격 conditional write 지원을 확인하지 못했으므로 get→patch 경합은 잔존 한계다.
