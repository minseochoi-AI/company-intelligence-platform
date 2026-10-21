"""Canonical responsibility owner; migrated from src/company_intel/normalization.py."""

from __future__ import annotations
from cil_contracts.facts import ComparabilitySignature
from cil_contracts.facts import SourcePolicy
from dataclasses import dataclass
from typing import Any
import hashlib
import json


@dataclass(frozen=True)
class NormalizedObservation:
    operation_id: str
    source_record_id: str | None
    subject_type: str
    country_code: str | None
    observation_date: str | None
    available_at: str | None
    values: dict[str, Any]
    source_locator: str | None
    deduplication_key: str


def normalize_unit(value: Any, unit: str | None) -> tuple[Any, str | None]:
    return (value, unit.strip() if isinstance(unit, str) and unit.strip() else None)


def resolve_field_path(record: Any, field_path: str) -> Any:
    """Return a provider field without flattening nested or multi-valued data.

    Catalog contracts may use a dotted path such as
    ``attributes.entity.legalForm.id``.  Numeric segments address an explicit
    array index; a non-numeric segment applied to a list maps over every list
    member and preserves the resulting list (including missing members).  This
    is deliberately lossless: callers decide whether a list can later be used
    as a facet instead of the mapper choosing one value on their behalf.
    """
    if not isinstance(field_path, str) or not field_path:
        return None
    if isinstance(record, dict) and field_path in record:
        return record[field_path]

    def descend(value: Any, segments: tuple[str, ...]) -> Any:
        if not segments:
            return value
        segment, *remaining = segments
        rest = tuple(remaining)
        if isinstance(value, dict):
            if segment not in value:
                return None
            return descend(value[segment], rest)
        if isinstance(value, list):
            if segment.isdigit():
                index = int(segment)
                return descend(value[index], rest) if 0 <= index < len(value) else None
            return [descend(item, segments) for item in value]
        return None

    return descend(record, tuple(field_path.split(".")))


def deduplication_key(
    operation_id: str,
    source_record_id: str | None,
    observation_date: str | None,
    values: dict[str, Any],
) -> str:
    stable = json.dumps(
        [operation_id, source_record_id, observation_date, values],
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


class AtomicObservationMapper:
    def map(
        self,
        policy: SourcePolicy,
        record: dict[str, Any],
        *,
        source_locator: str | None = None,
    ) -> NormalizedObservation:
        values = {
            contract.internal_field: resolve_field_path(record, contract.source_field)
            for contract in policy.field_contracts
        }
        source_record_id = next(
            (
                str(value)
                for key, value in record.items()
                if key in {"id", "idx", "publication-number", "Award ID"}
                and value is not None
            ),
            None,
        )
        observation_date = (
            record.get("observation_date")
            or record.get("date")
            or record.get("validFor")
        )
        available_at = (
            record.get("available_at")
            or record.get("updated_at")
            or record.get("filed_at")
        )
        return NormalizedObservation(
            operation_id=policy.operation_id,
            source_record_id=source_record_id,
            subject_type=policy.data_role,
            country_code=policy.regions[0] if len(policy.regions) == 1 else None,
            observation_date=str(observation_date) if observation_date else None,
            available_at=str(available_at) if available_at else None,
            values=values,
            source_locator=source_locator,
            deduplication_key=deduplication_key(
                policy.operation_id,
                source_record_id,
                str(observation_date) if observation_date else None,
                values,
            ),
        )


def comparability_signature(row: dict[str, Any]) -> ComparabilitySignature:
    """An explicit key for comparison; absent components remain absent."""
    return ComparabilitySignature(
        country_code=row.get("country_code") or row.get("country"),
        industry=row.get("industry") or row.get("industry_code"),
        size_bucket=row.get("size_bucket"),
        currency=row.get("currency") or row.get("salary_currency"),
        period=row.get("period") or row.get("salary_period"),
        unit=row.get("unit"),
        concept=row.get("concept") or row.get("metric_concept"),
        vintage=row.get("vintage") or row.get("available_at"),
        coverage=row.get("coverage"),
    )


def normalize_to_calendar_quarter(period_end_date: str | Any) -> str:
    """Convert any fiscal period end date (ISO or YYYYMMDD) into canonical Calendar Quarter CY-YYYY-Qk.

    Reconciles disparate fiscal year-end calendars across countries:
    - US Apple FY24Q1 (ends 2023-12-30) -> CY2023-Q4
    - US Microsoft FY24Q2 (ends 2023-12-31) -> CY2023-Q4
    - KR Kakao 23Q4 (ends 2023-12-31) -> CY2023-Q4
    """
    if not period_end_date:
        raise ValueError("period_end_date must not be empty")
    date_str = str(period_end_date).strip()[:10]
    cleaned = date_str.replace(".", "-").replace("/", "-")
    if len(cleaned) == 8 and cleaned.isdigit():
        year, month, _ = (int(cleaned[:4]), int(cleaned[4:6]), int(cleaned[6:8]))
    else:
        parts = cleaned.split("-")
        if len(parts) < 2:
            raise ValueError(f"Unrecognized date format: {period_end_date}")
        year, month = (int(parts[0]), int(parts[1]))
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid month {month} in date: {period_end_date}")
    quarter = (month - 1) // 3 + 1
    return f"CY{year}-Q{quarter}"


def calculate_quarterly_flow(
    ytd_records: list[dict[str, Any]],
    value_key: str = "cumulative_amount",
    period_key: str = "calendar_quarter",
) -> list[dict[str, Any]]:
    """Convert cumulative YTD financial statements into discrete quarterly flows.

    If Q1: flow = YTD_Q1
    If Q2: flow = YTD_Q2 - YTD_Q1
    If Q3: flow = YTD_Q3 - YTD_Q2
    If Q4: flow = YTD_Q4 - YTD_Q3
    """
    sorted_records = sorted(ytd_records, key=lambda r: str(r.get(period_key, "")))
    results: list[dict[str, Any]] = []
    current_year = None
    prev_cum = 0.0
    for rec in sorted_records:
        period = str(rec.get(period_key, ""))
        raw_val = rec.get(value_key)
        val = float(raw_val) if raw_val is not None else 0.0
        year_str = period[2:6] if period.startswith("CY") else period[:4]
        q_str = period[-1] if "Q" in period else "1"
        if year_str != current_year or q_str == "1":
            current_year = year_str
            flow = val
            prev_cum = val
        else:
            flow = val - prev_cum
            prev_cum = val
        out_rec = dict(rec)
        out_rec["quarterly_flow"] = flow
        out_rec["is_first_quarter"] = q_str == "1"
        results.append(out_rec)
    return results
