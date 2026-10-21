"""Compatibility exports. Canonical implementations live in cil_* packages."""

from cil_contracts.facts import AnalysisEligibility as AnalysisEligibility
from typing import Any as Any
from cil_contracts.facts import AtomicFact as AtomicFact
from cil_contracts.facts import AtomicFieldContract as AtomicFieldContract
from collections.abc import Callable as Callable
from cil_contracts.facts import CandidateMatch as CandidateMatch
from cil_contracts.facts import CompanyClassification as CompanyClassification
from cil_contracts.facts import ComparabilitySignature as ComparabilitySignature
from cil_contracts.facts import FacetAvailability as FacetAvailability
from cil_contracts.facts import HttpResult as HttpResult
from cil_contracts.facts import Normalizer as Normalizer
from cil_contracts.facts import Probe as Probe
from cil_contracts.facts import ProviderHealth as ProviderHealth
from cil_contracts.facts import RequirementEvidence as RequirementEvidence
from cil_contracts.facts import RequirementVerification as RequirementVerification
from cil_contracts.facts import SearchProfile as SearchProfile
from cil_contracts.facts import SourceDisposition as SourceDisposition
from cil_contracts.facts import SourcePolicy as SourcePolicy
from cil_contracts.facts import TaxonomyFact as TaxonomyFact
from dataclasses import dataclass as dataclass
from dataclasses import field as field
