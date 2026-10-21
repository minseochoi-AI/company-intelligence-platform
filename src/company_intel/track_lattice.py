"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.taxonomy import CareerEdge as CareerEdge
from cil_domain.taxonomy.templates import DOMAIN_METADATA as DOMAIN_METADATA
from cil_domain.taxonomy.templates import DOMAIN_REGISTRY as DOMAIN_REGISTRY
from cil_contracts.taxonomy import LatticeDomainGraph as LatticeDomainGraph
from cil_contracts.taxonomy import RoleNode as RoleNode
from cil_domain.taxonomy.tracks import TrackLatticeEngine as TrackLatticeEngine
from cil_contracts.taxonomy import WorkflowConnection as WorkflowConnection
from cil_domain.taxonomy.templates import build_ict_domain as build_ict_domain
from cil_domain.taxonomy.tracks import (
    get_default_ict_data_ai_graph as get_default_ict_data_ai_graph,
)
from cil_domain.taxonomy.templates import get_domain_graph as get_domain_graph
