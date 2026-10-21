"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_contracts.facts import FacetAvailability as FacetAvailability
from cil_domain.queries.facets import FacetDefinition as FacetDefinition
from cil_domain.queries.facets import FacetOption as FacetOption
from collections.abc import Iterable as Iterable
from cil_contracts.facts import TaxonomyFact as TaxonomyFact
from cil_domain.queries.facets import _JOB_DEFINITIONS as _JOB_DEFINITIONS
from cil_domain.queries.facets import _TAXONOMY_DEFINITIONS as _TAXONOMY_DEFINITIONS
from cil_domain.queries.facets import _evidence_status as _evidence_status
from cil_domain.queries.facets import _fact_token as _fact_token
from cil_domain.queries.facets import _job_options as _job_options
from cil_domain.queries.facets import _present as _present
from cil_domain.queries.facets import _records as _records
from cil_domain.queries.facets import _taxonomy_facts as _taxonomy_facts
from cil_domain.queries.facets import _text_value as _text_value
from cil_domain.queries.facets import build_job_facets as build_job_facets
from cil_domain.queries.facets import build_taxonomy_facets as build_taxonomy_facets
from dataclasses import dataclass as dataclass
from collections import defaultdict as defaultdict
from cil_domain.queries.facets import facet_count as facet_count
from cil_domain.queries.facets import facet_coverage as facet_coverage
from cil_domain.queries.facets import facet_definitions as facet_definitions
from cil_domain.queries.facets import (
    facet_options_for_selection as facet_options_for_selection,
)
from cil_domain.queries.facets import field_availability as field_availability
from cil_domain.queries.facets import identity_link_status as identity_link_status
from cil_domain.queries.facets import invalid_selection as invalid_selection
from cil_domain.queries.facets import public_context as public_context
from cil_domain.taxonomy.facts import (
    taxonomy_facts_from_record as taxonomy_facts_from_record,
)
