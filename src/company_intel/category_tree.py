"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_domain.taxonomy.tree import FacetBranch as FacetBranch
from typing import Iterable as Iterable
from typing import Mapping as Mapping
from cil_domain.taxonomy.tree import PURPOSE_ROOTS as PURPOSE_ROOTS
from cil_domain.taxonomy.tree import PurposeNode as PurposeNode
from cil_domain.taxonomy.tree import SelectionSession as SelectionSession
from cil_domain.taxonomy.tree import _matches as _matches
from cil_domain.taxonomy.tree import advance_selection as advance_selection
from cil_domain.taxonomy.tree import backtrack_selection as backtrack_selection
from cil_domain.taxonomy.tree import branches_for_selection as branches_for_selection
from dataclasses import dataclass as dataclass
from cil_domain.taxonomy.tree import preview_selection as preview_selection
from dataclasses import replace as replace
from cil_domain.taxonomy.tree import roots as roots
