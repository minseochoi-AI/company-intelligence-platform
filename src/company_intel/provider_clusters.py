"""Compatibility exports. Canonical implementations live in cil_* packages."""

from collections.abc import Iterable as Iterable
from cil_domain.providers.selection import OperationSelection as OperationSelection
from cil_domain.providers.selection import ProviderCluster as ProviderCluster
from cil_domain.providers.selection import ProviderDisposition as ProviderDisposition
from cil_contracts.facts import SourcePolicy as SourcePolicy
from enum import StrEnum as StrEnum
from cil_domain.providers.selection import _cluster_for_role as _cluster_for_role
from cil_domain.providers.selection import classify_operation as classify_operation
from dataclasses import dataclass as dataclass
from cil_domain.providers.selection import select_operations as select_operations
