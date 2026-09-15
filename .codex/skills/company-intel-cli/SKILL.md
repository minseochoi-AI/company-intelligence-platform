---
name: company-intel-cli
description: Use the Korean company-intel CLI to inspect saved provider evidence, search jobs or organizations, compare compatible companies, and export reproducible local results. Do not use for live provider refreshes unless explicitly requested.
---

# Company Intelligence CLI

Use the Korean command surface first. Existing English commands and options are compatibility aliases only.

Start with:

```bash
company-intel 사용-안내
company-intel 원천-상태
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

Keep JSON/CSV field names, provider IDs, and status enums unchanged. They are reproducibility contracts, not English presentation text. Do not infer salary, requirements, identity, or taxonomy values that an input snapshot does not structurally provide.

Examples:

```bash
company-intel 현재-채용 --프로필 profile.json --원천-응답 mpsv_cz=mpsv.json --출력 artifacts/current
company-intel 채용-동향 --스냅샷 artifacts/s1.json --스냅샷 artifacts/s2.json --지표 active_postings
company-intel 증거-내보내기 --표 tables.json --출력 artifacts/export --엑셀-생략
```
