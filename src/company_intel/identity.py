"""Compatibility exports. Canonical implementations live in cil_* packages."""

from cil_domain.identity.keys import CompanyIdentityResolver as CompanyIdentityResolver
from cil_domain.identity.keys import IdentifierLink as IdentifierLink
from cil_domain.identity.keys import ResolutionResult as ResolutionResult
from cil_domain.identity.keys import (
    SUPPORTED_IDENTIFIER_TYPES as SUPPORTED_IDENTIFIER_TYPES,
)
from dataclasses import dataclass as dataclass
from cil_domain.identity.keys import explain_resolution as explain_resolution
from cil_domain.identity.keys import (
    resolve_candidate_company as resolve_candidate_company,
)
