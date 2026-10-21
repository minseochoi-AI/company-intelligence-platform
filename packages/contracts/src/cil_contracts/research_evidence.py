"""Evidence value kinds and missing reasons are independent of numeric confidence."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class ValueKind(str, Enum):
    OBSERVED = "observed"
    COMPUTED = "computed"
    SOURCE_MODELLED = "source_modelled"
    USER_ASSUMPTION = "user_assumption"
    AI_PROPOSED = "ai_proposed"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    method_version: str
    unit: str
    denominator_definition: str | None = None


@dataclass(frozen=True)
class EvidenceValue:
    value: Any
    kind: str
    source_refs: tuple[str, ...] = ()
    unit: str | None = None
    reason: str | None = None
    method_version: str | None = None
    limitations: tuple[str, ...] = ()

    def __post_init__(self):
        if self.kind not in {x.value for x in ValueKind}:
            raise ValueError("unknown evidence kind")
        if self.value is None and not self.reason:
            raise ValueError("missing values require a reason")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EligibilityAssessment:
    requirement_id: str
    kind: str
    verdict: str
    reason: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageCompetition:
    scope: dict[str, Any]
    numerator_kind: str
    denominator_kind: str
    result: EvidenceValue


@dataclass(frozen=True)
class OperationBinding:
    provider_id: str
    operation_id: str
    schema_version: str
    snapshot_hash: str
    auth_ref: str | None = None


@dataclass(frozen=True)
class Gap:
    field: str
    reason: str
    status: str = "NEEDS_EVIDENCE"
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
