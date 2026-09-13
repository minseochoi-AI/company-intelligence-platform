from company_intel.taxonomy import TAXONOMY_AXES, taxonomy_facts_from_record


def _by_axis(facts, axis):
    return [fact for fact in facts if fact.semantic_field == axis]


def test_provider_native_taxonomy_preserves_codes_and_namespaces_without_identity_merge():
    ares = taxonomy_facts_from_record(
        "ares",
        {"ico": "123", "obchodniJmeno": "Example", "pravniForma": "121", "czNace": ["62.01", "63.11"]},
    )
    gleif = taxonomy_facts_from_record(
        "gleif",
        {"data": [{"id": "LEI-123", "attributes": {"entity": {"legalForm": {"id": "H1UM"}, "status": "ACTIVE", "category": "GENERAL"}}}]},
    )

    assert {fact.value for fact in _by_axis(ares, "industry")} == {"62.01", "63.11"}
    assert _by_axis(ares, "legal_form")[0].namespace == "ARES:pravniForma"
    assert _by_axis(gleif, "legal_form")[0].namespace == "GLEIF:ELF"
    assert _by_axis(gleif, "legal_entity_status")[0].value == "ACTIVE"
    assert not _by_axis(gleif, "market_status")
    assert ares[0].entity_id == "ICO:123"
    assert gleif[0].entity_id == "LEI:LEI-123"


def test_sec_alio_mpm_and_ats_stay_on_their_own_axes():
    sec = taxonomy_facts_from_record(
        "sec",
        {"cik": "320193", "sic": "3571", "sicDescription": "Electronic Computers", "entityType": "operating", "exchanges": ["Nasdaq"]},
    )
    alio = taxonomy_facts_from_record(
        "alioplus",
        {"apbaId": "A-1", "apbaTypeNa": "준정부기관", "apbaGb": "APBA", "bsnNa": "청년지원"},
    )
    mpm = taxonomy_facts_from_record(
        "mpm_public_employment",
        {"posting_id": "M-1", "institution_name": "정부기관", "type01": "e01", "type02": "g01"},
    )
    greenhouse = taxonomy_facts_from_record(
        "greenhouse",
        {"id": "G-1", "departments": [{"name": "Data"}], "offices": [{"location": "Prague"}]},
    )
    lever = taxonomy_facts_from_record(
        "lever",
        {"id": "L-1", "categories": {"team": "Platform", "department": "Engineering"}},
    )

    assert _by_axis(sec, "industry")[0].namespace == "SEC:SIC"
    assert _by_axis(sec, "listing_venue")[0].value == "Nasdaq"
    assert not _by_axis(sec, "market_status")
    assert _by_axis(alio, "ownership_sector")[0].value == "public_institution"
    assert _by_axis(alio, "public_institution_type")[0].value == "준정부기관"
    assert all(fact.semantic_field != "industry" for fact in alio)
    assert _by_axis(mpm, "posting_organization_unit")[0].evidence_status == "unresolved_identity"
    assert {fact.namespace for fact in _by_axis(mpm, "public_employment_type_code")} == {"MPM:type01", "MPM:type02"}
    assert _by_axis(greenhouse, "posting_organization_unit")[0].namespace == "ATS:GREENHOUSE:department"
    assert {fact.value for fact in _by_axis(lever, "posting_organization_unit")} == {"Platform", "Engineering"}
    assert "market_status" in TAXONOMY_AXES
