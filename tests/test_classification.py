from cil_domain.companies.classification import classify_company, classify_taxonomy_axes, evaluate_analysis_eligibility, legacy_company_type
from cil_domain.identity.keys import CompanyIdentityResolver, IdentifierLink
from cil_contracts.facts import TaxonomyFact
from cil_integrations.storage.duckdb.repository import Warehouse


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


def test_taxonomy_axes_keep_legal_form_public_context_and_posting_unit_separate():
    facts = (
        TaxonomyFact("legal_form", "121", "ARES:pravniForma", "ares", "pravniForma", "121", "ICO:1"),
        TaxonomyFact("ownership_sector", "public_institution", "ALIO:source_scope", "alioplus", "provider_scope", "public_institution_context", "ALIO:2", evidence_status="provider_context", filterability="display_only"),
        TaxonomyFact("posting_organization_unit", "Engineering", "ATS:GREENHOUSE:department", "greenhouse", "departments", {"name": "Engineering"}, None, evidence_status="posting_scope"),
    )

    axes = classify_taxonomy_axes(facts)

    assert axes["legal_form"][0].namespace == "ARES:pravniForma"
    assert axes["ownership_sector"][0].value == "public_institution"
    assert axes["posting_organization_unit"][0].value == "Engineering"
    assert legacy_company_type(facts) == "public_institution"
    assert legacy_company_type(facts[:1]) == "unknown"
