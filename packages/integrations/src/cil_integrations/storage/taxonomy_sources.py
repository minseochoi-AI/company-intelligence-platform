"""Load explicitly selected taxonomy inputs; never inspect sibling repositories."""

import json
from pathlib import Path
from cil_contracts.requests import content_hash
from cil_domain.taxonomy.lattice import (
    DeterministicTaxonomyItem,
    DeterministicLatticeSynthesizer,
)


def load_taxonomy_sources(path: str | Path) -> DeterministicLatticeSynthesizer:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "taxonomy-input-v1" or not payload.get(
        "source_id"
    ):
        raise ValueError("explicit taxonomy version/source required")
    items = payload.get("taxonomy", [])
    if not isinstance(items, list):
        raise ValueError("taxonomy array required")
    taxonomy = {}
    for row in items:
        item = DeterministicTaxonomyItem(**row)
        if item.code in taxonomy:
            raise ValueError("duplicate taxonomy code")
        taxonomy[item.code] = item
    crosswalks = payload.get("crosswalks", {})
    for source, mappings in crosswalks.items():
        if (
            source not in taxonomy
            or not mappings.get("source_id")
            or not mappings.get("version")
        ):
            raise ValueError("crosswalk requires source code, evidence and version")
    for code, evidence in payload.get("role_evidence", {}).items():
        if (
            code not in taxonomy
            or not evidence.get("source_refs")
            or evidence.get("evidence_status")
            not in {"observed", "source_modelled", "user_assumption", "ai_proposed"}
        ):
            raise ValueError("role measurements require explicit kind and source refs")
    result = DeterministicLatticeSynthesizer(
        taxonomy=taxonomy,
        crosswalks=crosswalks,
        role_evidence=payload.get("role_evidence"),
        workflows=payload.get("workflows"),
    )
    return result
