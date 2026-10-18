---
name: company-intel-cli
description: Use the Korean company-intel CLI for saved company, institution, or job evidence, reproducible comparison, and export. Live refresh requires an explicit request.
---

# Company Intelligence CLI

Use the Korean command surface first. Existing English commands and options are compatibility aliases only.

From outside the CIL checkout, pass its root explicitly or set `COMPANY_INTEL_PROJECT_ROOT`. The CLI argument wins over the environment variable, then falls back to the current directory. Confirm `config/providers.json` exists before a provider-status command.

Start with:

```bash
company-intel 사용-안내
company-intel --프로젝트-경로 /path/to/company-intelligence-platform 원천-상태
```

For stored job snapshots, inspect the exact inputs before running a search:

```bash
company-intel 사용-안내 --명령 채용-검색
company-intel 채용-검색 --도움말
```

Use `대화형-선택` when a human needs to choose observed facets with arrow keys. It reads only local JSON snapshots; it does not refresh providers, install packages, or submit applications. In a non-TTY environment, use `--선택-스크립트` and `--미리보기`.

Choose the analysis path by purpose:

- Current vacancies from one saved collection: `현재-채용`.
- Change across compatible repeated snapshots: `채용-동향`.
- Entity ownership, legal form, or public-institution taxonomy: `기업-기관-검색`.
- Comparable metrics only: `기업-비교`.
- Evidence and CSV/XLSX delivery: `근거-설명`, `증거-내보내기`, then `선택-재현` when verification is needed.
- Pre-flight baseline cluster space disclosure: `클러스터-사양-안내` (`cluster-spec`).
- API attribute metadata audit: `api-속성-조회` (`list-api-attributes`).
- Dynamic 3-layer cluster jobs export: `클러스터-채용-추출` (`export-cluster-jobs`).

Keep JSON/CSV field names, provider IDs, and status enums unchanged. They are reproducibility contracts, not English presentation text. Do not infer salary, requirements, identity, or taxonomy values that an input snapshot does not structurally provide.

Examples:

```bash
# 1. 28대 API, 142개 원천 속성, 21,000개 클러스터 조합 사전 설명문 출력
company-intel 클러스터-사양-안내

# 2. 특정 API 반환 속성 메타데이터 감사
company-intel api-속성-조회 --원천 cz_mpsv

# 3. 5단계 시그니처 기반 채용공고 엑셀 추출 (24열 하이퍼링크 수식 포함)
company-intel 클러스터-채용-추출 --시그니처 KR:STATE_OWNED:ALL:REGULAR:ALL --출력-경로 kr_soe_jobs.xlsx

# 4. 사전 설명문 선행 브리핑 및 래티스 실시간 해석이 포함된 대화형 모드
company-intel 클러스터-채용-추출 --대화형 --국가 CZ --섹터 PUBLIC_INSTITUTION

# 5. 동적 3-계층 속성 확장 엑셀 추출 (Core 8열 + 동적 N열 + Provenance 7열)
company-intel 클러스터-채용-추출 --국가 CZ --동적-속성 legal_form,salary_min,award_amount --출력-경로 cz_dynamic.xlsx
```
