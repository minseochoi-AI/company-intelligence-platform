"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.facts import AtomicFieldContract as AtomicFieldContract
from cil_contracts.facts import FacetAvailability as FacetAvailability
from pathlib import Path as Path
from cil_contracts.facts import ProviderHealth as ProviderHealth
from cil_integrations.catalog.repository import (
    REQUIRED_OPERATION_KEYS as REQUIRED_OPERATION_KEYS,
)
from cil_contracts.providers import SourceCatalog as SourceCatalog
from cil_contracts.facts import SourcePolicy as SourcePolicy
from cil_contracts.providers import (
    _NATIVE_FIELD_CAPABILITIES as _NATIVE_FIELD_CAPABILITIES,
)
from cil_integrations.catalog.repository import _policy as _policy
from dataclasses import dataclass as dataclass
from cil_domain.providers.contracts import evaluate_activation as evaluate_activation
from cil_contracts.providers import field_capabilities as field_capabilities
from cil_integrations.catalog.repository import (
    load_source_catalog as load_source_catalog,
)
from cil_domain.providers.contracts import (
    validate_atomic_contract as validate_atomic_contract,
)
