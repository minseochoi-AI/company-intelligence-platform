"""Canonical responsibility owner; migrated from src/company_intel/current_jobs.py."""

from __future__ import annotations
from cil_application.jobs.search import search_job_dataframes
from cil_contracts.jobs import CurrentJobResult
from cil_contracts.jobs import JobSearchProfile
from cil_contracts.jobs import SearchDenominators
from cil_domain.jobs.denominators import _records
from cil_domain.jobs.denominators import summarize_coverage
from cil_application.ports import normalize_provider_payloads
from datetime import UTC, datetime
from typing import Any, Mapping


def execute_current_job_search(
    payloads: Mapping[str, Any],
    profile: JobSearchProfile,
    *,
    snapshot_id: str | None = None,
    active_as_of: str | None = None,
) -> CurrentJobResult:
    """Execute only against supplied immutable payloads; live refresh is separate."""
    jobs, _requirements, source_rows = normalize_provider_payloads(dict(payloads))
    frames = search_job_dataframes(dict(payloads), profile)
    cutoff = active_as_of or datetime.now(UTC).isoformat()
    active = sum((1 for row in jobs if bool(row.get("is_active"))))
    denominators = SearchDenominators(
        provider_returned=sum(
            (int(row.get("record_count") or 0) for row in source_rows)
        ),
        normalized=len(jobs),
        active=active,
        strict_match=len(frames.strict_matches),
        unverifiable=len(frames.unverifiable_candidates),
        no_match=len(frames.no_matches),
        conflict=len(frames.conflicts),
        active_as_of=cutoff,
    )
    tables = {
        "jobs": _records(frames.jobs),
        "strict_matches": _records(frames.strict_matches),
        "unverifiable_candidates": _records(frames.unverifiable_candidates),
        "no_matches": _records(frames.no_matches),
        "conflicts": _records(frames.conflicts),
        "requirements": _records(frames.requirements),
        "sources": _records(frames.sources),
    }
    return CurrentJobResult(
        snapshot_id, denominators, tables, summarize_coverage(tables["sources"])
    )
