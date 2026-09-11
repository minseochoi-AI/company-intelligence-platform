from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .models import ComparabilitySignature, SourcePolicy


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
    return value, unit.strip() if isinstance(unit, str) and unit.strip() else None


def deduplication_key(operation_id: str, source_record_id: str | None, observation_date: str | None, values: dict[str, Any]) -> str:
    stable = json.dumps([operation_id, source_record_id, observation_date, values], ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


class AtomicObservationMapper:
    def map(self, policy: SourcePolicy, record: dict[str, Any], *, source_locator: str | None = None) -> NormalizedObservation:
        values = {
            contract.internal_field: record.get(contract.source_field)
            for contract in policy.field_contracts
        }
        source_record_id = next((str(value) for key, value in record.items() if key in {"id", "idx", "publication-number", "Award ID"} and value is not None), None)
        observation_date = record.get("observation_date") or record.get("date") or record.get("validFor")
        available_at = record.get("available_at") or record.get("updated_at") or record.get("filed_at")
        return NormalizedObservation(
            operation_id=policy.operation_id, source_record_id=source_record_id,
            subject_type=policy.data_role, country_code=(policy.regions[0] if len(policy.regions) == 1 else None),
            observation_date=str(observation_date) if observation_date else None,
            available_at=str(available_at) if available_at else None, values=values,
            source_locator=source_locator,
            deduplication_key=deduplication_key(policy.operation_id, source_record_id, str(observation_date) if observation_date else None, values),
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
