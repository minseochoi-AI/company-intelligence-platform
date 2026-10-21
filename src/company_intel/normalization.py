"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_domain.observations.normalization import (
    AtomicObservationMapper as AtomicObservationMapper,
)
from cil_contracts.facts import ComparabilitySignature as ComparabilitySignature
from cil_domain.observations.normalization import (
    NormalizedObservation as NormalizedObservation,
)
from cil_contracts.facts import SourcePolicy as SourcePolicy
from cil_domain.observations.normalization import (
    calculate_quarterly_flow as calculate_quarterly_flow,
)
from cil_domain.observations.normalization import (
    comparability_signature as comparability_signature,
)
from dataclasses import dataclass as dataclass
from cil_domain.observations.normalization import deduplication_key as deduplication_key
from cil_domain.observations.normalization import (
    normalize_to_calendar_quarter as normalize_to_calendar_quarter,
)
from cil_domain.observations.normalization import normalize_unit as normalize_unit
from cil_domain.observations.normalization import (
    resolve_field_path as resolve_field_path,
)
