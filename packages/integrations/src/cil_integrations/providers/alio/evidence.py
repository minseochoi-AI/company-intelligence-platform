"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from typing import Any, Callable, Mapping


def alio_context_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Return ALIO+ organisation context without inventing a legal identity.

    The live organisation response can leave ``apbaId`` blank and ``apbaNa``
    null while supplying its displayed institution name in ``title``.  A
    missing provider identifier must remain missing; ``title`` is useful for
    contextual grouping only and is not an entity-resolution key.
    """
    return {
        "institution_id": record.get("apbaId") or None,
        "institution_name": record.get("apbaNa") or record.get("title"),
        "institution_type": record.get("apbaTypeNa"),
        "identity_status": "source_identifier_present"
        if record.get("apbaId")
        else "context_only_no_source_identifier",
        "evidence_scope": "public_institution_context",
        "is_job_requirement": False,
    }
