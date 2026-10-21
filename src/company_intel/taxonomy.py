"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from collections.abc import Iterable as Iterable
from collections.abc import Mapping as Mapping
from cil_domain.taxonomy.facts import NCS_TO_ISCO_MAP as NCS_TO_ISCO_MAP
from cil_domain.taxonomy.facts import TAXONOMY_AXES as TAXONOMY_AXES
from cil_domain.taxonomy.facts import TITLE_TO_ISCO_PATTERNS as TITLE_TO_ISCO_PATTERNS
from cil_contracts.facts import TaxonomyFact as TaxonomyFact
from cil_domain.taxonomy.facts import _add as _add
from cil_domain.taxonomy.facts import _add_many as _add_many
from cil_domain.taxonomy.facts import _alio_facts as _alio_facts
from cil_domain.taxonomy.facts import _ares_facts as _ares_facts
from cil_domain.taxonomy.facts import _ats_facts as _ats_facts
from cil_domain.taxonomy.facts import _entity_id as _entity_id
from cil_domain.taxonomy.facts import _first as _first
from cil_domain.taxonomy.facts import _gleif_facts as _gleif_facts
from cil_domain.taxonomy.facts import _hrdkorea_facts as _hrdkorea_facts
from cil_domain.taxonomy.facts import _mpm_facts as _mpm_facts
from cil_domain.taxonomy.facts import _mpsv_facts as _mpsv_facts
from cil_domain.taxonomy.facts import _native_value as _native_value
from cil_domain.taxonomy.facts import _sec_facts as _sec_facts
from cil_domain.taxonomy.facts import _values as _values
from cil_domain.taxonomy.facts import _worknet_facts as _worknet_facts
from cil_domain.taxonomy.facts import link_status as link_status
from cil_domain.taxonomy.facts import normalize_alio_taxonomy as normalize_alio_taxonomy
from cil_domain.taxonomy.facts import normalize_ares_taxonomy as normalize_ares_taxonomy
from cil_domain.observations.normalization import (
    resolve_field_path as resolve_field_path,
)
from cil_domain.taxonomy.facts import resolve_title_to_isco as resolve_title_to_isco
from cil_domain.taxonomy.facts import (
    taxonomy_facts_from_record as taxonomy_facts_from_record,
)
from cil_domain.taxonomy.facts import (
    taxonomy_facts_from_records as taxonomy_facts_from_records,
)
