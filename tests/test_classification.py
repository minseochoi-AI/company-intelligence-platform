from company_intel.classification import classify_company, evaluate_analysis_eligibility
from company_intel.identity import CompanyIdentityResolver, IdentifierLink
from company_intel.warehouse import Warehouse


def test_finance_only_company_is_not_promoted_to_correlation_ready():
    classification = classify_company(
        "SEC:0000320193",
        {"financial": "available", "job_posting": "unavailable", "employment": "unavailable"},
        evidence_complete=False,
    )

    assert classification.capabilities["financial"] == "available"
    assert classification.analysis_eligibility.correlation_ready is False
    assert "missing-aligned-series" in classification.analysis_eligibility.reasons


def test_ambiguous_identity_is_retained_not_silently_merged():
    resolver = CompanyIdentityResolver()
    resolver.add(IdentifierLink("LEI", "A", "entity-a", "gleif", 0.9))
    resolver.add(IdentifierLink("LEI", "A", "entity-b", "gleif", 0.9))

    result = resolver.resolve("LEI", "A")

    assert result.status == "ambiguous"
    assert result.entity_id is None


def test_analysis_needs_identity_period_unit_and_availability():
    eligibility = evaluate_analysis_eligibility(
        identity_resolved=True,
        period_aligned=False,
        unit_aligned=True,
        available_at_present=True,
    )

    assert eligibility.correlation_ready is False
    assert "missing-period-alignment" in eligibility.reasons


def test_warehouse_identity_persistence_uses_the_identity_module_contract():
    assert callable(Warehouse.upsert_identity)


def test_context_and_proxy_capabilities_are_not_promoted():
    classification = classify_company("X", {"financial": "available", "public_context": "context_only", "market": "proxy_only"}, evidence_complete=True, period_aligned=True)
    assert classification.capabilities["public_context"] == "context_only"
    assert "market_proxy_only" in classification.classification_reasons
