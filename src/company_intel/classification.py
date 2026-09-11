from __future__ import annotations

from .models import AnalysisEligibility, CompanyClassification

CAPABILITY_AXES = ("financial", "job_posting", "employment", "market", "macro", "public_context")


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


def classify_company(entity_id: str, capabilities: dict[str, str], *, evidence_complete: bool, identity_resolved: bool = True, period_aligned: bool = False, unit_aligned: bool = True, available_at_present: bool = True) -> CompanyClassification:
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
    return CompanyClassification(entity_id, normalized, eligibility, tuple(reasons))
