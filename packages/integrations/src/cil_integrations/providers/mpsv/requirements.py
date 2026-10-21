"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyless.py."""

from __future__ import annotations


def czech_public_requirement_source(source_name: str) -> dict[str, str]:
    return {"source": source_name, "status": "pending-official-field-verification"}
