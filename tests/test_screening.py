from cil_domain.companies.screening import ScreenerProfile, screen_companies


def _comparable_row(entity_id: str, *, unit: str = "percent", growth: float = 0.0, **extra: object) -> dict:
    return {
        "entity_id": entity_id,
        "country": "US",
        "industry": "software",
        "size_bucket": "L",
        "growth": growth,
        "unit": unit,
        "period": "year",
        "concept": "revenue_growth",
        "coverage": "full",
        "available_at": "2026-01-01",
        **extra,
    }


def test_peer_boundaries_and_coverage() -> None:
    rows = [
        _comparable_row("A", growth=0.2, margin=0.1, source_url="https://a"),
        _comparable_row("B", growth=0.1, margin=None, source_url="https://b"),
        _comparable_row("C", growth=0.9, margin=0.9, country="KR", source_url="https://c"),
        _comparable_row("D", growth=0.8, margin=0.8, available_at="2027-01-01", source_url="https://d"),
    ]
    result = screen_companies(
        rows,
        ScreenerProfile(
            ("US",), ("software",), ("L",), {"growth": 1, "margin": 1}, as_of="2026-12-31"
        ),
    )
    assert set(result.rankings["entity_id"]) == {"A", "B"}
    assert set(result.rankings["peer_group"]) == {"US|software|L"}
    assert result.rankings.set_index("entity_id").loc["B", "data_coverage"] == 0.5
    assert set(result.exclusions["reason"]) == {"country_out_of_scope", "not_available_as_of"}


def test_multiple_comparability_groups_are_exposed_with_a_legacy_default_group() -> None:
    rows = [
        _comparable_row("A", growth=10),
        _comparable_row("B", unit="count", growth=5),
        _comparable_row("C", growth=99, metric_role="proxy"),
    ]
    result = screen_companies(
        rows,
        ScreenerProfile(("US",), ("software",), ("L",), {"growth": 1}, minimum_peer_size=1),
    )
    assert "proxy_metric_not_rankable" in set(result.exclusions["reason"])
    assert "incompatible_comparability_signature" in set(result.exclusions["reason"])
    assert len(result.rankings) == 1
    assert len(result.metadata["comparability_groups"]) == 2
    assert all(item["choice_required"] for item in result.metadata["comparability_groups"])
    assert result.metadata["default_comparability_selection"] == "legacy_largest_group"


def test_explicit_comparability_group_ranks_only_selected_signature() -> None:
    rows = [
        _comparable_row("A", growth=10),
        _comparable_row("B", unit="count", growth=5),
    ]
    initial = screen_companies(
        rows,
        ScreenerProfile(("US",), ("software",), ("L",), {"growth": 1}, minimum_peer_size=1),
    )
    percent_group = next(
        item["group_id"]
        for item in initial.metadata["comparability_groups"]
        if item["signature"]["unit"] == "percent"
    )

    result = screen_companies(
        rows,
        ScreenerProfile(
            ("US",),
            ("software",),
            ("L",),
            {"growth": 1},
            minimum_peer_size=1,
            comparability_group=percent_group,
        ),
    )

    assert list(result.rankings["entity_id"]) == ["A"]
    assert "comparability_group_not_selected" in set(result.exclusions["reason"])
    assert result.rankings.iloc[0]["comparability_group_id"] == percent_group


def test_missing_semantic_signature_is_unverifiable_not_ranked() -> None:
    result = screen_companies(
        [{"entity_id": "A", "country": "US", "industry": "software", "size_bucket": "L", "growth": 1}],
        ScreenerProfile(("US",), ("software",), ("L",), {"growth": 1}, minimum_peer_size=1),
    )

    assert result.rankings.empty
    assert list(result.exclusions["reason"]) == ["unverifiable_comparability_signature"]
