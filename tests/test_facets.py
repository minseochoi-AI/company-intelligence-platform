from pathlib import Path

from cil_domain.queries.facets import build_job_facets, build_taxonomy_facets, facet_options_for_selection, field_availability, identity_link_status
from cil_contracts.providers import field_capabilities
from cil_integrations.catalog.repository import load_source_catalog
from cil_domain.taxonomy.facts import taxonomy_facts_from_record


def _facet(options, field, value=None):
    matching = [item for item in options if item["semantic_field"] == field]
    if value is not None:
        matching = [item for item in matching if item["normalized_value"] == value]
    assert matching
    return matching[0]


def test_dynamic_job_facet_availability_disables_unknown_company_type_and_unstructured_salary():
    jobs = [
        {
            "provider": "greenhouse",
            "country_code": "US",
            "occupation_label": "Data Engineer",
            "location_raw": "New York, NY",
            "workplace_type": "remote",
            "employment_type": "unknown",
            "employment_type_raw": None,
            "posting_language": "en",
            "company_type": "unknown",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": None,
            "salary_period": None,
            "salary_basis": "unspecified",
        },
        {
            "provider": "lever",
            "country_code": "CZ",
            "occupation_label": "Data Engineer",
            "location_raw": "Prague",
            "workplace_type": "hybrid",
            "employment_type": "unknown",
            "employment_type_raw": "Permanent",
            "posting_language": None,
            "company_type": "unknown",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": None,
            "salary_period": None,
            "salary_basis": "unspecified",
        },
    ]

    options = build_job_facets(jobs)

    assert _facet(options, "country_code", "US")["selectable"] is True
    assert _facet(options, "employment_commitment_raw", "Permanent")["selectable"] is False
    company_type = _facet(options, "company_type", "__unavailable__")
    salary = _facet(options, "salary_signature", "__unavailable__")
    assert company_type["filterability"] == "forbidden"
    assert company_type["disabled_reason"]
    assert salary["filterability"] == "display-only"
    assert "structured" in salary["disabled_reason"].casefold()
    assert field_availability("company_type", jobs).selectable is False


def test_salary_and_taxonomy_facets_keep_their_required_semantics():
    jobs = [
        {
            "provider": "lever",
            "country_code": "US",
            "salary_min": 100000,
            "salary_max": 130000,
            "salary_currency": "USD",
            "salary_period": "year",
            "salary_basis": "base",
        }
    ]
    taxonomy = taxonomy_facts_from_record(
        "ares",
        {"ico": "123", "pravniForma": "121", "czNace": ["62.01"]},
    ) + taxonomy_facts_from_record(
        "alioplus",
        {"apbaId": "AL-1", "apbaTypeNa": "준정부기관"},
    )

    job_options = build_job_facets(jobs)
    taxonomy_options = build_taxonomy_facets(taxonomy)

    salary = _facet(job_options, "salary_signature", "USD/year/base")
    legal_form = _facet(taxonomy_options, "legal_form", "121")
    ownership = _facet(taxonomy_options, "ownership_sector", "public_institution")
    assert salary["selectable"] is True
    assert salary["comparability_requirements"] == ["currency", "period", "basis"]
    assert legal_form["vocabulary_namespace"] == "ARES:pravniForma"
    assert legal_form["selectable"] is True
    assert ownership["selectable"] is False
    assert ownership["evidence_status"] == "provider_scoped"


def test_source_catalog_declares_provider_native_field_boundaries():
    root = Path(__file__).resolve().parents[1]
    catalog = load_source_catalog(root / "config/providers.json")

    lever = {item.semantic_field: item for item in field_capabilities(catalog.by_id("lever_spotify"))}
    ares = {item.semantic_field: item for item in field_capabilities(catalog.by_id("ares_czech_company"))}

    assert lever["company_type"].filterability == "forbidden"
    assert lever["salary"].filterability == "filterable"
    assert ares["legal_form"].selectable is True
    assert ares["ownership_sector"].filterability == "forbidden"


def test_progressive_identity_facet_marks_unresolved_as_display_only():
    rows = [{"country_code": "KR", "identity_link_status": "unresolved"}, {"country_code": "CZ", "identity_link_status": "linked"}]
    statuses = {item["normalized_value"]: item for item in identity_link_status(rows)}
    assert statuses["unresolved"]["filterability"] == "display_only"
    assert facet_options_for_selection(rows, {"country_code": "KR"}, "country_code")[0]["record_count"] == 1
