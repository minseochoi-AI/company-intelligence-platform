"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.taxonomy import CareerEdge as CareerEdge
from cil_domain.taxonomy.lattice import DOMAIN_ID_TO_LABEL as DOMAIN_ID_TO_LABEL
from cil_domain.taxonomy.lattice import (
    DeterministicLatticeSynthesizer as DeterministicLatticeSynthesizer,
)
from cil_domain.taxonomy.lattice import (
    DeterministicTaxonomyItem as DeterministicTaxonomyItem,
)
from cil_domain.taxonomy.lattice import ISCO_MAJOR_DOMAIN_MAP as ISCO_MAJOR_DOMAIN_MAP
from cil_contracts.taxonomy import LatticeDomainGraph as LatticeDomainGraph
from cil_domain.taxonomy.facts import NCS_TO_ISCO_MAP as NCS_TO_ISCO_MAP
from pathlib import Path as Path
from cil_contracts.taxonomy import RoleNode as RoleNode
from cil_domain.taxonomy.lattice import SUBMAJOR_TO_DOMAIN_ID as SUBMAJOR_TO_DOMAIN_ID
from cil_domain.taxonomy.lattice import SUBMAJOR_TO_MANAGER as SUBMAJOR_TO_MANAGER
from cil_contracts.taxonomy import WorkflowConnection as WorkflowConnection
from dataclasses import dataclass as dataclass
from collections import defaultdict as defaultdict
from dataclasses import field as field
from cil_domain.taxonomy.lattice import logger as logger
