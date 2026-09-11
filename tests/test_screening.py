from company_intel.screening import ScreenerProfile, screen_companies


def test_peer_boundaries_and_coverage() -> None:
    rows = [
        {"entity_id": "A", "country": "US", "industry": "software", "size_bucket": "L", "growth": 0.2, "margin": 0.1, "available_at": "2026-01-01", "source_url": "https://a"},
        {"entity_id": "B", "country": "US", "industry": "software", "size_bucket": "L", "growth": 0.1, "margin": None, "available_at": "2026-01-01", "source_url": "https://b"},
        {"entity_id": "C", "country": "KR", "industry": "software", "size_bucket": "L", "growth": 0.9, "margin": 0.9, "available_at": "2026-01-01", "source_url": "https://c"},
        {"entity_id": "D", "country": "US", "industry": "software", "size_bucket": "L", "growth": 0.8, "margin": 0.8, "available_at": "2027-01-01", "source_url": "https://d"},
    ]
    result = screen_companies(rows, ScreenerProfile(("US",), ("software",), ("L",), {"growth": 1, "margin": 1}, as_of="2026-12-31"))
    assert set(result.rankings["entity_id"]) == {"A", "B"}
    assert set(result.rankings["peer_group"]) == {"US|software|L"}
    assert result.rankings.set_index("entity_id").loc["B", "data_coverage"] == 0.5
    assert set(result.exclusions["reason"]) == {"country_out_of_scope", "not_available_as_of"}


def test_incompatible_units_and_proxy_metrics_are_not_ranked() -> None:
    rows = [
        {"entity_id": "A", "country": "US", "industry": "software", "size_bucket": "L", "growth": 10, "unit": "percent", "currency": "USD", "period": "year", "concept": "revenue_growth", "coverage": "full"},
        {"entity_id": "B", "country": "US", "industry": "software", "size_bucket": "L", "growth": 5, "unit": "count", "currency": "USD", "period": "year", "concept": "revenue_growth", "coverage": "full"},
        {"entity_id": "C", "country": "US", "industry": "software", "size_bucket": "L", "growth": 99, "metric_role": "proxy"},
    ]
    result = screen_companies(rows, ScreenerProfile(("US",), ("software",), ("L",), {"growth": 1}, minimum_peer_size=1))
    assert "proxy_metric_not_rankable" in set(result.exclusions["reason"])
    assert "incompatible_comparability_signature" in set(result.exclusions["reason"])
