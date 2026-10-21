"""Canonical responsibility owner; migrated from src/company_intel/job_trends.py."""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class TrendEligibility:
    eligible: bool
    reason: str | None
    series_signature: tuple[str, ...]
    snapshot_count: int


@dataclass(frozen=True)
class PostingLifecycle:
    provider: str
    job_id: str
    first_snapshot: str
    last_snapshot: str
    appearances: int
    lifecycle: str


def _signature(snapshot: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        (
            str(snapshot.get(key) or "unknown")
            for key in (
                "provider",
                "taxonomy_version",
                "normalizer_version",
                "coverage_cohort",
            )
        )
    )


def evaluate_trend_eligibility(
    snapshots: Iterable[Mapping[str, Any]],
) -> TrendEligibility:
    records = list(snapshots)
    signatures = {_signature(item) for item in records}
    if len(records) < 2:
        return TrendEligibility(False, "insufficient_history", (), len(records))
    if len(signatures) != 1:
        return TrendEligibility(False, "coverage_or_version_break", (), len(records))
    if any(
        (
            not item.get("snapshot_id") or not item.get("collected_at")
            for item in records
        )
    ):
        return TrendEligibility(
            False, "snapshot_lineage_missing", next(iter(signatures)), len(records)
        )
    return TrendEligibility(True, None, next(iter(signatures)), len(records))


def build_posting_lifecycle(
    snapshots: Iterable[Mapping[str, Any]],
) -> list[PostingLifecycle]:
    appearances: dict[tuple[str, str], list[str]] = {}
    ordered = sorted(snapshots, key=lambda item: str(item.get("collected_at", "")))
    final_ids: set[tuple[str, str]] = set()
    for snapshot in ordered:
        snapshot_id = str(snapshot.get("snapshot_id") or "")
        jobs = snapshot.get("jobs") or []
        current: set[tuple[str, str]] = set()
        for job in jobs if isinstance(jobs, list) else []:
            if not isinstance(job, Mapping):
                continue
            key = (
                str(job.get("provider") or snapshot.get("provider") or "unknown"),
                str(job.get("job_id") or ""),
            )
            if not key[1]:
                continue
            current.add(key)
            appearances.setdefault(key, []).append(snapshot_id)
        final_ids = current
    return [
        PostingLifecycle(
            provider,
            job_id,
            ids[0],
            ids[-1],
            len(ids),
            "active" if (provider, job_id) in final_ids else "closed",
        )
        for (provider, job_id), ids in sorted(appearances.items())
    ]


def aggregate_job_trends(snapshots: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    records = list(snapshots)
    eligibility = evaluate_trend_eligibility(records)
    if not eligibility.eligible:
        return {
            "status": "ineligible",
            "eligibility": asdict(eligibility),
            "series": [],
        }
    lifecycle = build_posting_lifecycle(records)
    series: list[dict[str, Any]] = []
    previous: set[tuple[str, str]] = set()
    for snapshot in sorted(records, key=lambda item: str(item.get("collected_at", ""))):
        jobs = snapshot.get("jobs") or []
        keys = {
            (
                str(job.get("provider") or snapshot.get("provider") or "unknown"),
                str(job.get("job_id") or ""),
            )
            for job in jobs
            if isinstance(job, Mapping) and job.get("job_id")
        }
        series.append(
            {
                "snapshot_id": snapshot.get("snapshot_id"),
                "collected_at": snapshot.get("collected_at"),
                "active_postings": len(keys),
                "new_postings": len(keys - previous),
                "closed_postings": len(previous - keys),
            }
        )
        previous = keys
    return {
        "status": "eligible",
        "eligibility": asdict(eligibility),
        "series": series,
        "lifecycle": [asdict(item) for item in lifecycle],
    }
