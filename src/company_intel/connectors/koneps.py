"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_integrations.providers.koneps.procurements import (
    CURATED_KONEPS_FIXTURES as CURATED_KONEPS_FIXTURES,
)
from cil_integrations.providers.koneps.procurements import (
    CanonicalProcurementRecord as CanonicalProcurementRecord,
)
from cil_integrations.providers.koneps.procurements import (
    KONEPSProcurementConnector as KONEPSProcurementConnector,
)
from dataclasses import asdict as asdict
from dataclasses import dataclass as dataclass
