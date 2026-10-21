"""Catalog-derived availability; registration is not live API acceptance."""

from __future__ import annotations
from typing import Any
from cil_domain.clusters.signature import ClusterSignature
from cil_contracts.providers import SourceCatalog
from cil_application.ports import load_source_catalog

DIMENSIONS = {
    "region": ["KR", "CZ", "SK", "US", "ALL"],
    "sector": ["PUBLIC_INSTITUTION", "STATE_OWNED", "GOVERNMENT", "PRIVATE", "ALL"],
    "tier": [
        "KOSPI",
        "KOSDAQ",
        "KONEX",
        "EXTERNAL_AUDIT",
        "MARKET_SOE",
        "QUASI_GOV",
        "OTHER_PUBLIC",
        "LOCAL_SOE",
        "LARGE_CONGLOMERATE",
        "MID_SIZED",
        "SME",
        "VENTURE",
        "PUBLIC_CORP",
        "FOREIGN_INVESTED",
        "CENTRAL_GOV",
        "LOCAL_GOV",
        "CZ_STATNI_PODNIK",
        "CZ_PRISPEVKOVA_ORG",
        "CZ_SRO",
        "CZ_AS",
        "CZ_OSVC",
        "CZ_ORGANIZACNI_SLOZKA",
        "CZ_DRUZSTVO",
        "CZ_FOREIGN_BRANCH",
        "SK_STATNY_PODNIK",
        "SK_SAV",
        "SK_PRISPEVKOVA",
        "SK_STATNY_ORGAN",
        "SK_AS",
        "FEDERAL_GS",
        "US_FOR_PROFIT",
        "US_NONPROFIT",
        "US_HIGHER_ED",
        "US_LOCAL_GOV",
        "ALL",
    ],
    "contract": ["REGULAR", "NON_REGULAR", "INTERN", "INDEFINITE", "DISPATCHED", "ALL"],
    "workplace": ["ONSITE", "HYBRID", "REMOTE", "ALL"],
}
BASELINE_API_CATALOG: dict[str, Any] = {}


def catalog_summary(catalog: SourceCatalog) -> dict[str, Any]:
    keyed = {o.provider for o in catalog.operations if o.access_mode != "keyless"}
    keyless = {o.provider for o in catalog.operations if o.access_mode == "keyless"}
    return {
        "schema_version": catalog.schema_version,
        "atomic_operations": len(catalog.operations),
        "total_providers": len({o.provider for o in catalog.operations}),
        "keyed_providers": len(keyed),
        "keyless_providers": len(keyless),
        "source_semantic_mappings": sum(
            len(o.field_contracts) for o in catalog.operations
        ),
        "distinct_internal_semantics": len(
            {f.internal_field for o in catalog.operations for f in o.field_contracts}
        ),
        "dimensions": DIMENSIONS,
        "live_status": "not_probed",
        "limitations": [
            "Operation, provider and field mappings have different counting units.",
            "Declared capabilities do not establish live response fields or record coverage.",
        ],
    }


def get_cluster_baseline_spec_text() -> str:
    BASELINE_API_CATALOG.clear()
    BASELINE_API_CATALOG.update(catalog_summary(load_source_catalog()))
    c = BASELINE_API_CATALOG
    return (
        f"등록된 원자 API operation {c['atomic_operations']}개 / provider {c['total_providers']}개\n"
        f"원천 필드 의미 매핑 {c['source_semantic_mappings']}개 / 내부 의미 {c['distinct_internal_semantics']}개\n"
        f"인증 분류 provider: 키 필요 {c['keyed_providers']}개, keyless {c['keyless_providers']}개 (혼합 provider 중복 가능)\n"
        "5축: Region:Sector:Tier:Contract:Workplace. 추가 조건은 ReportRequest 필터·조사 옵션.\n"
        "현재 응답의 전체 키 수·실시간 가용성·자료 건수는 선택한 snapshot에서 별도 확인."
    )


def resolve_active_providers(signature: ClusterSignature) -> dict[str, Any]:
    operations = load_source_catalog().operations
    selected = [
        o
        for o in operations
        if signature.region == "ALL"
        or signature.region in o.regions
        or "GLOBAL" in o.regions
        or "ALL" in o.regions
    ]
    free = [
        name
        for name in ("region", "sector", "tier", "contract", "workplace")
        if getattr(signature, name) == "ALL"
    ]
    return {
        "signature_key": signature.key,
        "active_providers": sorted({o.provider for o in selected}),
        "candidate_operations": [o.operation_id for o in selected],
        "availability": "registered_not_live_verified",
        "free_dimensions": free,
        "is_macro_rollup": len(free) >= 3,
        "is_micro_cohort": not free,
        "limitations": [
            "Registered capability is not selected-posting evidence or refresh authority."
        ],
    }
