"""Current-job execution with a denominator chain and four evidence outcomes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

from .job_search import JobSearchProfile, normalize_provider_payloads, search_job_dataframes


@dataclass(frozen=True)
class SearchDenominators:
    provider_returned: int
    normalized: int
    active: int
    strict_match: int
    unverifiable: int
    no_match: int
    conflict: int
    active_as_of: str


@dataclass(frozen=True)
class CurrentJobResult:
    snapshot_id: str | None
    denominators: SearchDenominators
    tables: dict[str, list[dict[str, Any]]]
    coverage: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"snapshot_id": self.snapshot_id, "denominators": asdict(self.denominators), "tables": self.tables, "coverage": self.coverage}


def _records(frame: Any) -> list[dict[str, Any]]:
    return frame.astype(object).where(frame.notna(), None).to_dict("records")


def summarize_coverage(sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "providers": sorted({str(row.get("provider")) for row in sources if row.get("provider")} ),
        "source_count": len(sources),
        "limitations": [row.get("limitations") for row in sources if row.get("limitations")],
    }


def execute_current_job_search(
    payloads: Mapping[str, Any], profile: JobSearchProfile, *, snapshot_id: str | None = None, active_as_of: str | None = None
) -> CurrentJobResult:
    """Execute only against supplied immutable payloads; live refresh is separate."""

    jobs, _requirements, source_rows = normalize_provider_payloads(dict(payloads))
    frames = search_job_dataframes(dict(payloads), profile)
    cutoff = active_as_of or datetime.now(UTC).isoformat()
    active = sum(1 for row in jobs if bool(row.get("is_active")))
    denominators = SearchDenominators(
        provider_returned=sum(int(row.get("record_count") or 0) for row in source_rows),
        normalized=len(jobs),
        active=active,
        strict_match=len(frames.strict_matches),
        unverifiable=len(frames.unverifiable_candidates),
        no_match=len(frames.no_matches),
        conflict=len(frames.conflicts),
        active_as_of=cutoff,
    )
    tables = {
        "jobs": _records(frames.jobs), "strict_matches": _records(frames.strict_matches),
        "unverifiable_candidates": _records(frames.unverifiable_candidates),
        "no_matches": _records(frames.no_matches), "conflicts": _records(frames.conflicts),
        "requirements": _records(frames.requirements), "sources": _records(frames.sources),
    }
    return CurrentJobResult(snapshot_id, denominators, tables, summarize_coverage(tables["sources"]))
