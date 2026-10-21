"""Explicit saved occupation mapping adapter; no fabricated code suffixes."""

import json
from pathlib import Path
from cil_domain.taxonomy.mapping import map_occupation


class SavedTaxonomyAdapter:
    def __init__(self, path: Path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != "occupation-mapping-v1" or not isinstance(
            payload.get("mappings"), list
        ):
            raise ValueError("versioned mapping array required")
        self.mappings = payload["mappings"]

    def resolve(self, code, system, target_system, *, version):
        return map_occupation(
            code, system, target_system, self.mappings, version=version
        )
