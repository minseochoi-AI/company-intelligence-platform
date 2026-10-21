"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.facts import Probe as Probe
from cil_domain.providers.selection import ProviderCluster as ProviderCluster
from cil_integrations.runtime.settings import Settings as Settings
from cil_integrations.providers.registry import build_probes as build_probes
from cil_domain.providers.selection import classify_operation as classify_operation
from cil_domain.providers.contracts import evaluate_activation as evaluate_activation
from cil_integrations.providers.registry import keyed_probes as keyed_probes
from cil_integrations.providers.registry import keyless_probes as keyless_probes
from cil_integrations.catalog.repository import (
    load_source_catalog as load_source_catalog,
)
from cil_integrations.providers.registry import (
    production_adapters as production_adapters,
)
from cil_domain.providers.selection import select_operations as select_operations
from cil_integrations.providers.registry import source_health as source_health
