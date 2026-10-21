"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_domain.identity.links import IdentityLink as IdentityLink
from typing import Mapping as Mapping
from cil_domain.identity.links import _name as _name
from dataclasses import asdict as asdict
from cil_domain.identity.links import classify_link_status as classify_link_status
from dataclasses import dataclass as dataclass
from cil_domain.identity.links import link_mpm_alio as link_mpm_alio
from cil_domain.identity.links import link_mpsv_ares as link_mpsv_ares
