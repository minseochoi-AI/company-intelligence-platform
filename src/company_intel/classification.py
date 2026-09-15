from __future__ import annotations

from collections.abc import Iterable

from .models import AnalysisEligibility, CompanyClassification, TaxonomyFact

CAPABILITY_AXES = ("financial", "job_posting", "employment", "market", "macro", "public_context")
TAXONOMY_AXES = (
    "ownership_sector",
    "public_institution_type",
    "legal_form",
    "industry",
    "market_status",
    "posting_organization_unit",
)


def evaluate_analysis_eligibility(*, identity_resolved: bool, period_aligned: bool, unit_aligned: bool, available_at_present: bool) -> AnalysisEligibility:
    reasons: list[str] = []
    if not identity_resolved:
        reasons.append("identity_unresolved")
    if not period_aligned:
        reasons.append("missing-period-alignment")
    if not unit_aligned:
        reasons.append("missing-unit-alignment")
    if not available_at_present:
        reasons.append("missing-available-at")
    if not reasons:
        return AnalysisEligibility(True, False, ("causal-evidence-not-established",))
    return AnalysisEligibility(False, False, tuple(reasons))


def classify_taxonomy_axes(facts: Iterable[TaxonomyFact]) -> dict[str, tuple[TaxonomyFact, ...]]:
    """Group taxonomy facts without converting provider-native codes.

    The returned values are facts rather than a single string because a legal
    form, industry code, or public-institution type can be multi-valued.  In
    particular, this function intentionally does *not* infer an ownership
    sector from a legal-form code or a current market status from a listing
    venue.  Callers that need a cross-provider comparison must first select a
    common namespace and document their mapping.
    """

    grouped: dict[str, list[TaxonomyFact]] = {axis: [] for axis in TAXONOMY_AXES}
    for fact in facts:
        grouped.setdefault(fact.semantic_field, []).append(fact)
    return {
        axis: tuple(
            sorted(
                entries,
                key=lambda item: (item.namespace, item.value, item.raw_field),
            )
        )
        for axis, entries in grouped.items()
    }


def legacy_company_type(facts: Iterable[TaxonomyFact]) -> str:
    """Return the conservative legacy company-type value used by old callers.

    ``company_type`` was historically a catch-all field.  Only a source that
    explicitly declares an ownership sector may populate the legacy adapter;
    legal forms, ATS departments, and filing entity types remain ``unknown``.
    """

    ownership = [fact.value for fact in facts if fact.semantic_field == "ownership_sector"]
    if len(set(ownership)) == 1 and ownership:
        return ownership[0]
    return "unknown"


def classify_company(
    entity_id: str,
    capabilities: dict[str, str],
    *,
    evidence_complete: bool,
    identity_resolved: bool = True,
    period_aligned: bool = False,
    unit_aligned: bool = True,
    available_at_present: bool = True,
    taxonomy_facts: Iterable[TaxonomyFact] = (),
) -> CompanyClassification:
    allowed = {"available", "unavailable", "unknown", "context_only", "proxy_only"}
    normalized = {axis: capabilities.get(axis, "unknown") for axis in CAPABILITY_AXES}
    normalized = {axis: status if status in allowed else "unknown" for axis, status in normalized.items()}
    reasons = [f"{axis}_{status}" for axis, status in normalized.items() if status != "available"]
    if not evidence_complete:
        reasons.append("missing-aligned-series")
    eligibility = evaluate_analysis_eligibility(
        identity_resolved=identity_resolved,
        period_aligned=period_aligned and evidence_complete,
        unit_aligned=unit_aligned,
        available_at_present=available_at_present,
    )
    if not evidence_complete and "missing-aligned-series" not in eligibility.reasons:
        eligibility = AnalysisEligibility(
            eligibility.correlation_ready,
            eligibility.causal_ready,
            (*eligibility.reasons, "missing-aligned-series"),
        )
    facts = tuple(taxonomy_facts)
    return CompanyClassification(entity_id, normalized, eligibility, tuple(reasons), facts)


def identity_eligibility(status: str | None) -> dict[str, object]:
    """Describe which public-sector axes can be used as hard filters."""

    normalized = str(status or "unresolved")
    if normalized == "linked":
        return {"identity_status": normalized, "filterable": True, "reason": None}
    if normalized == "conflict":
        return {"identity_status": normalized, "filterable": False, "reason": "identity_conflict"}
    return {"identity_status": normalized if normalized == "candidate" else "unresolved", "filterable": False, "reason": "identity_unresolved"}


def public_sector_axes(
    *, public_context: str | None = None, public_institution_type: str | None = None,
    legal_form: str | None = None, ownership_sector: str | None = None, identity_status: str | None = None,
) -> dict[str, dict[str, object]]:
    """Keep source context, institution type, legal form, and ownership independent."""

    link = identity_eligibility(identity_status)
    return {
        "public_context": {"value": public_context, "filterable": public_context is not None, "source_scoped": True},
        "public_institution_type": {"value": public_institution_type, "filterable": bool(link["filterable"] and public_institution_type), "identity": link},
        "legal_form": {"value": legal_form, "filterable": bool(link["filterable"] and legal_form), "identity": link},
        "ownership_sector": {"value": ownership_sector, "filterable": bool(link["filterable"] and ownership_sector), "identity": link},
    }
