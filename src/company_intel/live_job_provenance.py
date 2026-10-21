"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.jobs import CanonicalJobRecord as CanonicalJobRecord
from cil_application.jobs.provenance import (
    JobProvenanceVerifier as JobProvenanceVerifier,
)
