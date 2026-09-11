"""Route providers by the question they can answer, not their wire format."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from .models import SourcePolicy


class ProviderCluster(StrEnum):
    JOB_DISCOVERY = "job_discovery"
    IDENTITY = "identity"
    FUNDAMENTALS = "fundamentals"
    MARKET_MACRO = "market_macro"
    PUBLIC_CONTEXT = "public_context"
    PROXY_RESEARCH = "proxy_research"


class ProviderDisposition(StrEnum):
    PRODUCTION = "production"
    METADATA_ONLY = "metadata_only"
    CONTEXT_ONLY = "context_only"
    PROXY_ONLY = "proxy_only"
    CANDIDATE_PENDING_SEMANTIC_VALIDATION = "candidate_pending_semantic_validation"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OperationSelection:
    operation_id: str
    cluster: ProviderCluster
    disposition: ProviderDisposition
    reason: str


def _cluster_for_role(role: str) -> ProviderCluster:
    if role == "job_posting":
        return ProviderCluster.JOB_DISCOVERY
    if role == "identity":
        return ProviderCluster.IDENTITY
    if role == "financial":
        return ProviderCluster.FUNDAMENTALS
    if role in {"market", "macro"}:
        return ProviderCluster.MARKET_MACRO
    if role == "procurement":
        return ProviderCluster.PUBLIC_CONTEXT
    return ProviderCluster.PUBLIC_CONTEXT


def classify_operation(policy: SourcePolicy) -> OperationSelection:
    role = policy.data_role
    # The source catalog is the explicit, auditable authority for a source that
    # was rejected or deliberately confined after live schema validation.  Do
    # not let a broad role (for example, "macro") silently re-enable it.
    if policy.provider_disposition != ProviderDisposition.PRODUCTION:
        disposition = ProviderDisposition(policy.provider_disposition)
        return OperationSelection(
            policy.operation_id,
            _cluster_for_role(role),
            disposition,
            f"Catalog disposition is {disposition}; production routing is disabled or constrained accordingly.",
        )
    if policy.operation_id in {"greenhouse_airtable", "lever_spotify"}:
        return OperationSelection(policy.operation_id, ProviderCluster.JOB_DISCOVERY, ProviderDisposition.METADATA_ONLY, "Fixed board probe is a connector fixture, not market-wide company discovery.")
    if policy.provider in {"github", "openalex"}:
        return OperationSelection(policy.operation_id, ProviderCluster.PROXY_RESEARCH, ProviderDisposition.PROXY_ONLY, "Activity and research are not company financial or hiring facts.")
    if policy.provider == "alioplus":
        return OperationSelection(policy.operation_id, ProviderCluster.PUBLIC_CONTEXT, ProviderDisposition.CONTEXT_ONLY, "ALIO Plus describes public-institution context, not job requirements.")
    if policy.provider == "bea" and role == "dataset_catalog":
        return OperationSelection(policy.operation_id, ProviderCluster.MARKET_MACRO, ProviderDisposition.METADATA_ONLY, "Dataset catalog is discovery metadata, not an economic observation.")
    if policy.provider == "mpm_public_employment":
        return OperationSelection(policy.operation_id, ProviderCluster.JOB_DISCOVERY, ProviderDisposition.METADATA_ONLY, "List response lacks verified salary, location, and requirement detail.")
    if policy.provider == "mpsv_cz":
        return OperationSelection(policy.operation_id, ProviderCluster.JOB_DISCOVERY, ProviderDisposition.CANDIDATE_PENDING_SEMANTIC_VALIDATION, "Use only a schema-validated saved response until live endpoint validation is approved.")
    if role == "job_posting":
        return OperationSelection(policy.operation_id, ProviderCluster.JOB_DISCOVERY, ProviderDisposition.PRODUCTION, "Posting fields may be searched within their declared coverage.")
    if role == "identity":
        return OperationSelection(policy.operation_id, ProviderCluster.IDENTITY, ProviderDisposition.PRODUCTION, "Legal identifiers may resolve an entity, but never infer a match.")
    if role == "financial":
        return OperationSelection(policy.operation_id, ProviderCluster.FUNDAMENTALS, ProviderDisposition.PRODUCTION, "Reported financial facts remain period and unit scoped.")
    if role in {"market", "macro"}:
        return OperationSelection(policy.operation_id, ProviderCluster.MARKET_MACRO, ProviderDisposition.PRODUCTION, "Series require unit, frequency, and vintage matching.")
    if role in {"public_context", "procurement"}:
        return OperationSelection(policy.operation_id, ProviderCluster.PUBLIC_CONTEXT, ProviderDisposition.CONTEXT_ONLY, "Context must not be promoted to a job or financial fact.")
    return OperationSelection(policy.operation_id, ProviderCluster.PUBLIC_CONTEXT, ProviderDisposition.METADATA_ONLY, "No production search contract is declared.")


def select_operations(policies: Iterable[SourcePolicy], cluster: ProviderCluster, *, production_only: bool = True) -> tuple[OperationSelection, ...]:
    selections = tuple(classify_operation(policy) for policy in policies)
    return tuple(item for item in selections if item.cluster == cluster and (not production_only or item.disposition == ProviderDisposition.PRODUCTION))
