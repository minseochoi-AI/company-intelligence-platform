"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_integrations.providers.bea.cubes import BEACubeLoader as BEACubeLoader
from cil_integrations.providers.eurostat.cubes import (
    EurostatCubeLoader as EurostatCubeLoader,
)
from cil_domain.finance.macro import MacroCubeManager as MacroCubeManager
from cil_contracts.macro import MacroObservation as MacroObservation
from pathlib import Path as Path
from dataclasses import dataclass as dataclass
