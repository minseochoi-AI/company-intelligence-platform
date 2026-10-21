"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.query import AtomicSearchProfile as AtomicSearchProfile
from cil_contracts.query import COMPANY_SEMANTIC_FIELDS as COMPANY_SEMANTIC_FIELDS
from cil_contracts.query import CompanySearchProfile as CompanySearchProfile
from cil_contracts.query import ComparabilityPolicy as ComparabilityPolicy
from cil_contracts.query import CurrentJobQuery as CurrentJobQuery
from cil_contracts.query import CurrentResultContract as CurrentResultContract
from cil_contracts.query import DenominatorContract as DenominatorContract
from cil_contracts.query import FieldFilter as FieldFilter
from cil_contracts.query import FieldVerdict as FieldVerdict
from cil_contracts.query import FilterMode as FilterMode
from cil_contracts.query import FilterVerdict as FilterVerdict
from collections.abc import Iterable as Iterable
from cil_contracts.query import JobTrendQuery as JobTrendQuery
from collections.abc import Mapping as Mapping
from cil_contracts.query import QueryMode as QueryMode
from cil_contracts.query import SelectionProfile as SelectionProfile
from cil_contracts.query import SemanticValue as SemanticValue
from enum import StrEnum as StrEnum
from cil_contracts.query import TrendComparison as TrendComparison
from cil_contracts.query import TrendMetric as TrendMetric
from cil_contracts.query import UnknownPolicy as UnknownPolicy
from cil_contracts.query import _JOB_ONLY_COMPANY_INPUTS as _JOB_ONLY_COMPANY_INPUTS
from cil_contracts.query import _PROFILE_LIST_FIELDS as _PROFILE_LIST_FIELDS
from cil_contracts.query import _field_filter_from_mapping as _field_filter_from_mapping
from cil_contracts.query import (
    _job_only_filters_from_mapping as _job_only_filters_from_mapping,
)
from cil_contracts.query import _merge_filter_values as _merge_filter_values
from cil_contracts.query import _parse_field_filters as _parse_field_filters
from cil_contracts.query import _string_tuple as _string_tuple
from cil_contracts.query import combine_verdicts as combine_verdicts
from cil_contracts.query import (
    company_search_profile_from_legacy as company_search_profile_from_legacy,
)
from cil_contracts.query import (
    company_search_profile_from_mapping as company_search_profile_from_mapping,
)
from dataclasses import dataclass as dataclass
from cil_contracts.query import normalize_tree_selection as normalize_tree_selection
from cil_contracts.query import parse_query_profile as parse_query_profile
from cil_contracts.query import text_verdict as text_verdict
from cil_contracts.query import validate_facet_selection as validate_facet_selection
