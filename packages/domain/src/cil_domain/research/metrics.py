"""Pure research metrics with explicit population, unit, time and missingness."""

from __future__ import annotations
from typing import Any
from collections import defaultdict
from datetime import date
import math

from cil_contracts.requests import timestamp

SCOPE_FIELDS = ("round_id", "stage", "role_id", "location_id", "cutoff")


def _result(
    value: Any, unit: str, reason: str | None = None, **details: Any
) -> dict[str, Any]:
    return {
        "value": value,
        "unit": unit,
        "kind": "computed" if value is not None else "unknown",
        "reason": reason,
        "method_version": "1.0.0",
        **details,
    }


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def competition_ratio(
    row: dict[str, Any], expected_scope: dict[str, Any]
) -> dict[str, Any]:
    unit = "applicants_per_opening"
    if any(
        expected_scope.get(k) in (None, "") or row.get(k) in (None, "")
        for k in SCOPE_FIELDS
    ):
        return _result(None, unit, "scope_incomplete")
    if any(row[k] != expected_scope[k] for k in SCOPE_FIELDS):
        return _result(None, unit, "incomparable_recruitment_scope")
    if row.get("source_type") != "official" or not row.get("source_id"):
        return _result(None, unit, "official_stage_evidence_required")
    if (
        row.get("numerator_kind") not in {"unique_applicants", "submissions"}
        or row.get("denominator_kind") != "openings"
    ):
        return _result(None, unit, "incompatible_count_definition")
    numerator, denominator = row.get("applicant_count"), row.get("vacancy_count")
    if (
        not _number(numerator)
        or not _number(denominator)
        or numerator < 0
        or denominator < 0
    ):
        return _result(None, unit, "missing_or_invalid_counts")
    if denominator == 0:
        return _result(None, unit, "zero_denominator")
    return _result(
        numerator / denominator,
        unit,
        scope={k: row[k] for k in SCOPE_FIELDS},
        numerator=numerator,
        denominator=denominator,
        numerator_kind=row["numerator_kind"],
        denominator_kind="openings",
        source_refs=[row["source_id"]],
        limitations=["Population competition is not an individual hiring probability."],
    )


def stage_pass_rate(
    row: dict[str, Any], expected_scope: dict[str, Any]
) -> dict[str, Any]:
    unit = "stage_pass_fraction"
    if any(not row.get(k) or row.get(k) != expected_scope.get(k) for k in SCOPE_FIELDS):
        return _result(None, unit, "incomparable_recruitment_scope")
    a, b = row.get("passed_count"), row.get("attended_count")
    if row.get("source_type") != "official" or not row.get("source_id"):
        return _result(None, unit, "official_stage_evidence_required")
    if not _number(a) or not _number(b) or b <= 0 or not 0 <= a <= b:
        return _result(None, unit, "invalid_stage_counts")
    return _result(
        a / b, unit, numerator=a, denominator=b, source_refs=[row["source_id"]]
    )


def eligibility_verdict(
    requirement: dict[str, Any], profile: dict[str, Any], *, as_of: str | None = None
) -> dict[str, Any]:
    """Assess one documented rule. A missing profile is not a rejection."""
    result = {
        "requirement_id": requirement.get("requirement_id"),
        "necessity": requirement.get("necessity"),
        "verdict": "unknown",
        "source_refs": [requirement["source_id"]]
        if requirement.get("source_id")
        else [],
    }
    necessity = requirement.get("necessity")
    if necessity not in {"required", "preferred", "disqualifier"}:
        return {
            **result,
            "verdict": "not_applicable",
            "reason": "not_an_applicant_rule",
        }
    if (
        requirement.get("kind") == "ai_proposed"
        and requirement.get("review_status") != "approved"
    ):
        return {**result, "reason": "unreviewed_requirement_extraction"}
    if not requirement.get("source_id"):
        return {**result, "reason": "requirement_source_missing"}
    actual = profile.get(requirement.get("field"))
    if actual is None:
        return {**result, "reason": "profile_evidence_missing"}
    status = (
        actual.get("status", "unknown") if isinstance(actual, dict) else "self_reported"
    )
    value = actual.get("value") if isinstance(actual, dict) else actual
    if status == "conflict":
        return {
            **result,
            "verdict": "conflict",
            "reason": "conflicting_profile_evidence",
        }
    if status not in {"verified", "self_reported"} or value is None:
        return {**result, "reason": "profile_evidence_unverified"}
    if as_of and isinstance(actual, dict):
        available = actual.get("available_at")
        if status == "verified" and (not available or not actual.get("evidence_ref")):
            return {**result, "reason": "profile_evidence_reference_or_time_missing"}
        try:
            if available and timestamp(available) > timestamp(as_of):
                return {**result, "reason": "profile_evidence_not_available_as_of"}
        except ValueError:
            return {**result, "reason": "invalid_profile_evidence_time"}
    expected = requirement.get("value")
    operator = requirement.get("operator", "eq")
    if operator == "eq":
        hit = type(value) is type(expected) and value == expected
    elif operator == "in" and isinstance(expected, list):
        hit = any(type(value) is type(x) and value == x for x in expected)
    elif operator in {"gte", "lte"} and _number(value) and _number(expected):
        hit = value >= expected if operator == "gte" else value <= expected
    elif operator == "contains" and isinstance(value, list):
        hit = expected in value
    else:
        return {**result, "reason": "requirement_rule_not_comparable"}
    satisfied = not hit if necessity == "disqualifier" else hit
    return {
        **result,
        "verdict": "match" if satisfied else "no_match",
        "reason": "documented_rule_evaluated",
        "profile_evidence_status": status,
        "provisional": status == "self_reported",
        "condition_triggered": hit,
    }


def comparable_financials(
    rows: list[dict[str, Any]],
    *,
    entity_id: str,
    as_of: str,
    revision_mode: str = "known_at_time",
) -> dict[str, Any]:
    if revision_mode not in {"known_at_time", "current_restated"}:
        raise ValueError("invalid revision mode")
    cutoff = timestamp(as_of)
    fields = (
        "entity_id",
        "concept",
        "scope",
        "currency",
        "unit",
        "frequency",
        "period_basis",
    )
    versions: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    excluded = []
    for raw in rows:
        if raw.get("entity_id") != entity_id:
            continue
        row = dict(raw)
        if not row.get("available_at"):
            excluded.append({**row, "reason": "availability_time_unknown"})
            continue
        if timestamp(row["available_at"]) > cutoff:
            excluded.append({**row, "reason": "not_available_as_of"})
            continue
        if any(row.get(k) in (None, "") for k in fields) or not row.get("period_end"):
            excluded.append({**row, "reason": "comparison_signature_incomplete"})
            continue
        date.fromisoformat(row["period_end"])
        versions[tuple(row[k] for k in fields) + (row["period_end"],)].append(row)
    accepted, groups = [], defaultdict(list)
    for key, candidates in sorted(versions.items()):
        latest_time = max(timestamp(r["available_at"]) for r in candidates)
        latest = [r for r in candidates if timestamp(r["available_at"]) == latest_time]
        row = dict(sorted(latest, key=lambda r: str(r.get("revision", "")))[-1])
        if len({str(r.get("value")) for r in latest}) > 1:
            row["comparison_status"] = "conflict"
        row["revision_mode"] = revision_mode
        row["knowledge_cutoff"] = as_of
        accepted.append(row)
        groups[key[:-1]].append(row)
    comparisons = []
    for signature, group in sorted(groups.items()):
        group.sort(key=lambda r: r["period_end"])
        for before, after in zip(group, group[1:]):
            details = {
                "entity_id": entity_id,
                "concept": after["concept"],
                "previous_period": before["period_end"],
                "period_end": after["period_end"],
                "comparison_signature": dict(zip(fields, signature, strict=True)),
            }
            a, b = before.get("value"), after.get("value")
            days = (
                date.fromisoformat(after["period_end"])
                - date.fromisoformat(before["period_end"])
            ).days
            frequency = after["frequency"]
            aligned = (
                335 <= days <= 396
                if frequency in {"annual", "A", "Y"}
                else 80 <= days <= 100
                if frequency in {"quarterly", "Q"}
                else False
            )
            if (
                before.get("comparison_status") == "conflict"
                or after.get("comparison_status") == "conflict"
            ):
                result = _result(None, "fraction", "conflicting_financial_revisions")
            elif not aligned:
                result = _result(None, "fraction", "nonconsecutive_or_unknown_period")
            elif not _number(a) or not _number(b) or a <= 0:
                result = _result(None, "fraction", "nonpositive_or_missing_base")
            else:
                result = _result((b - a) / a, "fraction")
            comparisons.append({**details, **result})
    return {
        "rows": sorted(
            accepted, key=lambda r: (r["period_end"], r["concept"], r["available_at"])
        ),
        "comparisons": comparisons,
        "excluded": excluded,
        "revision_mode": revision_mode,
        "knowledge_cutoff": as_of,
    }


def wage_conversion(
    wage: dict[str, Any], assumptions: dict[str, Any] | None = None
) -> dict[str, Any]:
    assumptions = assumptions or {}
    details = {
        "currency": wage.get("currency"),
        "basis": wage.get("basis"),
        "source_period": wage.get("period"),
        "source_value": wage.get("value"),
        "source_refs": [wage["source_id"]] if wage.get("source_id") else [],
    }
    value, period = wage.get("value"), wage.get("period")
    if (
        not _number(value)
        or value < 0
        or not wage.get("currency")
        or not wage.get("basis")
    ):
        return {
            **_result(None, "currency_per_year", "wage_definition_incomplete"),
            **details,
        }
    if period in {"year", "annual"}:
        return {
            **_result(value, "currency_per_year"),
            **details,
            "assumption_kind": None,
        }
    multiplier_name = {
        "hour": "hours_per_year",
        "month": "payments_per_year",
        "week": "paid_weeks_per_year",
    }.get(period)
    factor = assumptions.get(multiplier_name) if multiplier_name else None
    kind = assumptions.get("author_kind")
    if (
        multiplier_name is None
        or not _number(factor)
        or factor <= 0
        or kind not in {"user_assumption", "ai_proposed", "source_derived"}
    ):
        return {
            **_result(None, "currency_per_year", "explicit_work_schedule_required"),
            **details,
        }
    return {
        **_result(value * factor, "currency_per_year"),
        **details,
        "assumption_kind": kind,
        "conversion": {multiplier_name: factor},
        "limitations": [
            "Annualization does not estimate an offer, net salary, benefits or total compensation."
        ],
    }


def task_exposure(
    tasks: list[dict[str, Any]], method: dict[str, Any], *, total_weight: float = 1.0
) -> dict[str, Any]:
    unit = "normalized_task_exposure"
    if not method.get("method_id") or not method.get("version"):
        return _result(None, unit, "exposure_method_required")
    low, high = method.get("scale_min"), method.get("scale_max")
    if (
        not _number(low)
        or not _number(high)
        or high <= low
        or not _number(total_weight)
        or total_weight <= 0
    ):
        return _result(None, unit, "invalid_exposure_scale_or_weight")
    if not tasks:
        return _result(None, unit, "task_evidence_missing", coverage=0.0)
    if any(not _number(t.get("weight")) or t["weight"] < 0 for t in tasks):
        return _result(None, unit, "task_weights_unknown", coverage=None)
    if len({t.get("task_id") for t in tasks}) != len(tasks):
        return _result(None, unit, "duplicate_task_mapping")
    weight = sum(t["weight"] for t in tasks)
    if weight > total_weight + 1e-9:
        return _result(None, unit, "task_weights_exceed_population")
    covered = weighted = 0.0
    for task in tasks:
        score = task.get("exposure")
        if score is None or not task.get("source_id"):
            continue
        if not _number(score) or not low <= score <= high:
            return _result(None, unit, "task_exposure_outside_scale")
        covered += task["weight"]
        weighted += task["weight"] * (score - low) / (high - low)
    coverage = covered / total_weight
    mean = weighted / covered if covered else None
    details = {
        "coverage": coverage,
        "covered_task_score": mean,
        "unmapped_weight": total_weight - covered,
        "method_id": method["method_id"],
        "study_version": method["version"],
        "bounds": [
            weighted / total_weight,
            (weighted + total_weight - covered) / total_weight,
        ],
        "limitations": [
            "Task exposure is not an individual replacement or unemployment probability.",
            "Bounds assume the stated score scale and supplied time weights.",
        ],
    }
    if coverage < 1 - 1e-9:
        return _result(None, unit, "partial_task_coverage", **details)
    return {**_result(mean, unit, **details), "kind": "source_modelled"}
