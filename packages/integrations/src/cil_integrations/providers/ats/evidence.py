"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyless.py."""

from __future__ import annotations
from typing import Any, Iterable, Iterator, Mapping


def ats_detail_evidence(job: dict[str, Any]) -> dict[str, Any]:
    """Keep ATS detail text separate from a verified requirement assertion.

    Parsing and country-specific validation happen in career_requirements, so a
    job board description alone can never fabricate a certificate requirement.
    """
    detail = job.get("content") or job.get("description")
    return {
        "job_id": job.get("job_id") or job.get("id"),
        "source_url": job.get("absolute_url") or job.get("hosted_url"),
        "detail_present": bool(detail),
        "raw_detail": detail if isinstance(detail, str) else None,
        "availability": "unverified_detail" if detail else "requirement_unavailable",
    }
