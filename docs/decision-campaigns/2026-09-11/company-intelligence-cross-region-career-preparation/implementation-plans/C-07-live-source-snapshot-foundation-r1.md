# Implementation plan: company-intelligence-cross-region-career-preparation--C-07-live-source-snapshot-foundation--r1

Status: `contract-ready`

## live-refresh-and-snapshot-foundation: MPM pagination과 MPSV 전체 파일 갱신을 provider operation으로 실행하고 한 검색 세션이 사용하는 불변 snapshot·분모·coverage·identity link history를 저장한다.

### Changes

| ID | Operation | Path | Decisions | Symbols | Source hash | Result hash | After state | Dependencies |
|---|---|---|---|---|---|---|---|---|
| file-change-e1e3c60c9a87 | MODIFY | `config/providers.json` | D-11-live-source-refresh-snapshot-contract | operations, mpm_public_employment, mpsv_job_vacancies | sha256:3d4196fab89a6438ddc6752fbd741e1d2321168bd2619af8eaa2728a1b8f82a2 | - | MPM 최신순 pagination과 MPSV snapshot download operation 및 freshness 정책을 선언한다. | - |
| file-change-927a21cab8b8 | MODIFY | `src/company_intel/connectors/keyed.py` | D-11-live-source-refresh-snapshot-contract | MPMPublicEmploymentConnector, iter_pages, collect_snapshot | sha256:f6f02fb66d1160091a8fbce8b0dcdf01131e43122944c06b43fdb7abe89af7e2 | - | 최신순·page size·종료 조건을 입력받아 중복 posting_id 없이 페이지를 수집한다. | file-change-e1e3c60c9a87 |
| file-change-8925cfef251f | MODIFY | `src/company_intel/connectors/keyless.py` | D-11-live-source-refresh-snapshot-contract | MPSVVacancyConnector, download_snapshot, stream_records | sha256:ee76965cb19b96ba7583338aa312c0ce74e3255801ca5afa19cf23b84831c57c | - | 공식 전체 파일을 bounded download하고 hash·수집시각·행 수와 함께 streaming parse한다. | file-change-e1e3c60c9a87 |
| file-change-42c469cea05e | MODIFY | `src/company_intel/warehouse.py` | D-11-live-source-refresh-snapshot-contract, D-13-public-sector-identity-linkage, D-16-job-trend-series-analysis-contract | snapshot_run, snapshot_source, store_snapshot, load_snapshot, entity_link, store_entity_link, posting_snapshot_membership, posting_lifecycle, load_snapshot_series | sha256:d36c1a2114ffc69987c2f109446639a5c1eba4911d6e807d67f7843eb9288545 | - | snapshot_id, collected_at, query parameters, raw hash, provider denominator, normalized/active counts와 partial failure를 저장한다. | provider entity와 canonical entity의 link status·method·evidence·validity를 snapshot별로 저장한다. | provider+posting_id membership와 taxonomy/normalizer/coverage version을 반복 snapshot별 보존한다. | file-change-927a21cab8b8, file-change-8925cfef251f |
| file-change-6094b4c9c865 | CREATE | `src/company_intel/live_snapshots.py` | D-11-live-source-refresh-snapshot-contract | SnapshotRequest, SnapshotManifest, refresh_sources, select_snapshot, snapshot_freshness | - | - | provider operation을 실행·격리하고 성공/부분실패를 하나의 redacted snapshot manifest로 결속한다. | file-change-42c469cea05e |
| file-change-edb669d59fb3 | CREATE | `tests/test_live_snapshots.py` | D-11-live-source-refresh-snapshot-contract | test_mpm_pagination_is_deduplicated, test_partial_failure_manifest, test_snapshot_replay | - | - | offline fixtures로 pagination, 중복 제거, partial failure, stale/reuse, manifest redaction을 검증한다. | file-change-6094b4c9c865 |
| file-change-f93b01f715ba | MODIFY | `tests/test_public_connectors.py` | D-11-live-source-refresh-snapshot-contract | test_mpm_paginated_query, test_mpsv_streaming_snapshot | sha256:be9a9fd6dd16c918e8e60a8beef666c96dea2fea71fd0109d558ba599a0ea1ee | - | MPM page 종료·중복과 MPSV bounded streaming을 offline transport fixture로 검증한다. | file-change-927a21cab8b8, file-change-8925cfef251f |

### Routed skills

- `c07-data-contract` → `company-intelligence-career-research` (IMPLEMENT, required): MPM·MPSV 수집 의미와 현재/누적 분모 경계를 유지한다.
- `c07-verification` → `verification-before-completion` (VALIDATE, required): snapshot·connector offline criteria를 독립 검증한다.

### Completion criteria

- `C-07-live-snapshot-tests` [planned] `verification-before-completion` phase=VALIDATE, depends=-: MPM/MPSV 수집이 중복 없는 불변 snapshot과 정확한 분모·partial failure를 생성한다.
