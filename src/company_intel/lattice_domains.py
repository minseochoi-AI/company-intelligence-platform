"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Callable as Callable
from cil_contracts.taxonomy import CareerEdge as CareerEdge
from cil_domain.taxonomy.templates import DOMAIN_METADATA as DOMAIN_METADATA
from cil_domain.taxonomy.templates import DOMAIN_REGISTRY as DOMAIN_REGISTRY
from cil_contracts.taxonomy import LatticeDomainGraph as LatticeDomainGraph
from cil_contracts.taxonomy import RoleNode as RoleNode
from cil_contracts.taxonomy import WorkflowConnection as WorkflowConnection
from cil_domain.taxonomy.templates import (
    build_battery_energy_domain as build_battery_energy_domain,
)
from cil_domain.taxonomy.templates import (
    build_bio_healthcare_domain as build_bio_healthcare_domain,
)
from cil_domain.taxonomy.templates import (
    build_business_strategy_domain as build_business_strategy_domain,
)
from cil_domain.taxonomy.templates import (
    build_construction_architecture_domain as build_construction_architecture_domain,
)
from cil_domain.taxonomy.templates import (
    build_culture_design_domain as build_culture_design_domain,
)
from cil_domain.taxonomy.templates import (
    build_environment_safety_domain as build_environment_safety_domain,
)
from cil_domain.taxonomy.templates import (
    build_finance_investment_domain as build_finance_investment_domain,
)
from cil_domain.taxonomy.templates import (
    build_grand_unified_macro_graph as build_grand_unified_macro_graph,
)
from cil_domain.taxonomy.templates import build_ict_domain as build_ict_domain
from cil_domain.taxonomy.templates import build_legal_ip_domain as build_legal_ip_domain
from cil_domain.taxonomy.templates import (
    build_marketing_sales_domain as build_marketing_sales_domain,
)
from cil_domain.taxonomy.templates import (
    build_mobility_robotics_domain as build_mobility_robotics_domain,
)
from cil_domain.taxonomy.templates import (
    build_semiconductor_domain as build_semiconductor_domain,
)
from cil_domain.taxonomy.templates import get_domain_graph as get_domain_graph
