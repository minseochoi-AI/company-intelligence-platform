"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from collections.abc import Iterable as Iterable
from cil_contracts.facts import RequirementEvidence as RequirementEvidence
from cil_domain.jobs.requirements import RequirementKind as RequirementKind
from cil_domain.jobs.requirements import RequirementNecessity as RequirementNecessity
from cil_contracts.facts import RequirementVerification as RequirementVerification
from enum import StrEnum as StrEnum
from cil_domain.jobs.requirements import (
    extract_job_requirements as extract_job_requirements,
)
from cil_domain.jobs.requirements import normalize_requirement as normalize_requirement
from cil_domain.jobs.requirements import (
    requirement_dedupe_key as requirement_dedupe_key,
)
from cil_domain.jobs.requirements import requirement_overlap as requirement_overlap
from cil_domain.jobs.requirements import requirement_rows as requirement_rows
from cil_domain.jobs.requirements import (
    resolve_country_baseline as resolve_country_baseline,
)
from cil_domain.jobs.requirements import verify_requirement as verify_requirement
