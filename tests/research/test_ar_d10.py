def test_missing_macro_is_unknown_and_latest_is_order_independent(proof):
    from cil_domain.finance.macro import MacroCubeManager
    from cil_contracts.macro import MacroObservation

    assert MacroCubeManager().get_latest_base_rate("KR") is None
    assert MacroCubeManager().get_real_gdp_growth("KR") is None
    old = MacroObservation(
        "KR", "base_rate", "rate", "2024-01-01", "2024-Q1", 3.5, "percent"
    )
    new = MacroObservation(
        "KR", "base_rate", "rate", "2025-01-01", "2025-Q1", 3.0, "percent"
    )
    manager = MacroCubeManager([new, old])
    assert (
        proof.invoke(
            "AR-D10-contract",
            manager.get_latest_base_rate,
            "KR",
            checks={
                "input": lambda b, a, r, e: (
                    b["args"] == ("KR",)
                    and b["state"][0].observation_date > b["state"][1].observation_date
                ),
                "return": lambda b, a, r, e: e is None and r == 0.03,
                "relation": lambda b, a, r, e: (
                    r == max(b["state"], key=lambda o: o.observation_date).value / 100
                    and b["state"] == a["state"]
                ),
            },
            observe=lambda: manager._observations,
        )
        == 0.03
    )
