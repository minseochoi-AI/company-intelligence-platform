"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.query import COMPANY_SEMANTIC_FIELDS as COMPANY_SEMANTIC_FIELDS
from cil_contracts.facts import CandidateMatch as CandidateMatch
from cil_domain.companies.search import (
    CompanyCandidateEvaluation as CompanyCandidateEvaluation,
)
from cil_contracts.query import CompanySearchProfile as CompanySearchProfile
from cil_contracts.query import FieldFilter as FieldFilter
from cil_contracts.query import FieldVerdict as FieldVerdict
from cil_contracts.query import FilterMode as FilterMode
from cil_contracts.query import FilterVerdict as FilterVerdict
from collections.abc import Iterable as Iterable
from collections.abc import Mapping as Mapping
from cil_contracts.facts import SearchProfile as SearchProfile
from cil_contracts.query import SemanticValue as SemanticValue
from cil_contracts.query import UnknownPolicy as UnknownPolicy
from cil_domain.companies.search import (
    _KNOWN_CAPABILITY_STATUSES as _KNOWN_CAPABILITY_STATUSES,
)
from cil_domain.companies.search import (
    _SEMANTIC_FIELD_ALIASES as _SEMANTIC_FIELD_ALIASES,
)
from cil_domain.companies.search import (
    _apply_country_allocation as _apply_country_allocation,
)
from cil_domain.companies.search import _as_text as _as_text
from cil_domain.companies.search import (
    _capability_field_verdict as _capability_field_verdict,
)
from cil_domain.companies.search import _company_profile as _company_profile
from cil_domain.companies.search import _evaluation_reason as _evaluation_reason
from cil_domain.companies.search import (
    _identity_field_verdict as _identity_field_verdict,
)
from cil_domain.companies.search import _included as _included
from cil_domain.companies.search import _is_identity_conflict as _is_identity_conflict
from cil_domain.companies.search import _keyword_field_verdict as _keyword_field_verdict
from cil_domain.companies.search import _legacy_match as _legacy_match
from cil_domain.companies.search import _selector_matches as _selector_matches
from cil_domain.companies.search import (
    _semantic_field_verdict as _semantic_field_verdict,
)
from cil_domain.companies.search import _semantic_values as _semantic_values
from cil_domain.companies.search import (
    _semantic_values_from_value as _semantic_values_from_value,
)
from cil_domain.companies.search import _sort_evaluations as _sort_evaluations
from cil_domain.companies.search import (
    apply_country_allocation as apply_country_allocation,
)
from dataclasses import asdict as asdict
from cil_domain.companies.search import build_company_universe as build_company_universe
from cil_domain.companies.search import candidate_verdict as candidate_verdict
from cil_contracts.query import combine_verdicts as combine_verdicts
from cil_contracts.query import (
    company_search_profile_from_legacy as company_search_profile_from_legacy,
)
from dataclasses import dataclass as dataclass
from cil_domain.companies.search import (
    evaluate_company_candidate as evaluate_company_candidate,
)
from cil_domain.companies.search import explain_candidate as explain_candidate
from cil_domain.companies.search import (
    explain_company_evaluation as explain_company_evaluation,
)
from cil_domain.companies.search import identity_link_status as identity_link_status
from cil_domain.companies.search import public_sector_filter as public_sector_filter
from cil_domain.companies.search import (
    rank_candidate_evaluations as rank_candidate_evaluations,
)
from cil_domain.companies.search import rank_candidates as rank_candidates
from dataclasses import replace as replace
from cil_contracts.query import text_verdict as text_verdict
from cil_domain.companies.search import (
    validate_company_search_profile as validate_company_search_profile,
)
from cil_domain.companies.search import (
    validate_search_profile as validate_search_profile,
)
