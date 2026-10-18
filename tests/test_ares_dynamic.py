from company_intel.connectors.ares_dynamic import AresDynamicClient, lookup_czech_company


def test_ares_dynamic_lookup():
    client = AresDynamicClient()

    # Škoda Auto a.s.
    skoda = client.get_economic_subject("00177041")
    assert skoda is not None
    assert skoda["ico"] == "00177041"
    assert "Škoda" in skoda["company_name"]
    assert "29100" in skoda["cz_nace"]
    assert skoda["country_code"] == "CZ"
    assert skoda["city"] == "Mladá Boleslav"

    # Avast Software
    avast = client.get_economic_subject("02176475")
    assert avast is not None
    assert avast["ico"] == "02176475"
    assert "Avast" in avast["company_name"]
    assert any(c.startswith("62") or c.startswith("58") for c in avast["cz_nace"])
    assert avast["city"] == "Praha"


def test_ares_search_by_name():
    client = AresDynamicClient()
    results = client.search_by_name("Škoda")
    assert len(results) >= 1
    assert any(r["ico"] == "00177041" for r in results)


def test_ares_convenience_function():
    skoda = lookup_czech_company("00177041")
    assert skoda is not None
    assert skoda["ico"] == "00177041"
