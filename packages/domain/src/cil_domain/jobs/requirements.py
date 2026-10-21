"""Canonical responsibility owner; migrated from src/company_intel/career_requirements.py."""

from __future__ import annotations
from cil_contracts.facts import RequirementEvidence
from cil_contracts.facts import RequirementVerification
from collections.abc import Iterable
from enum import StrEnum
from typing import Any


class RequirementKind(StrEnum):
    SKILL = "skill"
    LANGUAGE = "language"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    CERTIFICATION = "certification"
    LICENSE = "license"
    OTHER = "other"


class RequirementNecessity(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    UNKNOWN = "unknown"


def normalize_requirement(
    value: dict[str, Any], *, evidence_scope: str = "job_posting"
) -> RequirementEvidence:
    text = str(value.get("text") or value.get("requirement") or "").strip()
    if not text:
        raise ValueError("requirement text is required")
    status = str(value.get("kind") or value.get("status") or "required").casefold()
    if status not in {item.value for item in RequirementNecessity}:
        raise ValueError("requirement kind must be required, preferred, or unknown")
    source_url = value.get("source_url")
    return RequirementEvidence(
        text,
        status,
        evidence_scope,
        str(source_url) if source_url else None,
        "verified" if source_url else "unverified",
    )


def resolve_country_baseline(
    country_code: str, occupation_code: str | None = None
) -> RequirementVerification:
    return RequirementVerification(
        "requirement_unavailable",
        (),
        f"No verified public baseline is stored for {country_code.upper()}{('/' + occupation_code if occupation_code else '')}",
    )


def extract_job_requirements(job: dict[str, Any]) -> tuple[RequirementEvidence, ...]:
    rows = job.get("requirements")
    if not isinstance(rows, list):
        return ()
    results: list[RequirementEvidence] = []
    for row in rows:
        if isinstance(row, dict):
            results.append(normalize_requirement(row))
    return tuple(results)


def verify_requirement(
    job: dict[str, Any], *, country_code: str
) -> RequirementVerification:
    requirements = extract_job_requirements(job)
    if requirements:
        return RequirementVerification("available", requirements)
    return resolve_country_baseline(
        country_code,
        str(job.get("occupation_code")) if job.get("occupation_code") else None,
    )


def requirement_rows(
    requirements: Iterable[RequirementEvidence],
) -> list[dict[str, Any]]:
    return [
        {
            "text": item.text,
            "status": item.status,
            "evidence_scope": item.evidence_scope,
            "source_url": item.source_url,
            "verification_status": item.verification_status,
        }
        for item in requirements
    ]


def requirement_dedupe_key(
    *, kind: str, label: str, necessity: str, jurisdiction: str | None = None
) -> tuple[str, ...]:
    """Licences are jurisdiction-specific; a similar certificate is not a licence."""
    return (
        kind.casefold(),
        label.casefold().strip(),
        necessity.casefold(),
        (jurisdiction or "").casefold(),
    )


def requirement_overlap(
    rows: Iterable[dict[str, object]],
) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    for row in rows:
        key = requirement_dedupe_key(
            kind=str(row.get("requirement_kind", "other")),
            label=str(row.get("label", "")),
            necessity=str(row.get("necessity", "unknown")),
            jurisdiction=row.get("jurisdiction")
            if isinstance(row.get("jurisdiction"), str)
            else None,
        )
        counts[key] = counts.get(key, 0) + 1
    return counts
