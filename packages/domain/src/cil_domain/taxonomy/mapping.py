"""Versioned many-to-many occupation mappings; no code-shape guesses."""

from copy import deepcopy


def map_occupation(
    code: str, system: str, target_system: str, mappings: list[dict], *, version: str
) -> dict:
    selected = [
        deepcopy(row)
        for row in mappings
        if row.get("from_code") == code
        and row.get("from_system") == system
        and row.get("to_system") == target_system
        and row.get("version") == version
    ]
    if any(
        not row.get("source_id") or not row.get("relation") or not row.get("to_code")
        for row in selected
    ):
        raise ValueError("mapping identity, relation and source required")
    return {
        "status": "MAPPED" if selected else "UNKNOWN",
        "from_code": code,
        "from_system": system,
        "to_system": target_system,
        "version": version,
        "mappings": selected,
        "limitations": [
            "Taxonomy correspondence is not employer equivalence or promotion policy."
        ],
    }
