def test_catalog_counts_have_explicit_units_and_follow_actual_operations(proof):
    from cil_application.providers.capabilities import catalog_summary
    from cil_integrations.catalog.repository import load_source_catalog

    catalog = load_source_catalog()
    result = proof.invoke(
        "AR-D03-contract",
        catalog_summary,
        catalog,
        checks={
            "input": lambda b, a, r, e: len(b["args"][0].operations) > 0,
            "return": lambda b, a, r, e: (
                e is None and isinstance(r, dict) and "physical_records" not in r
            ),
            "relation": lambda b, a, r, e: (
                r["atomic_operations"] == len(b["args"][0].operations)
                and r["total_providers"]
                == len({o.provider for o in b["args"][0].operations})
            ),
        },
    )
    assert result["atomic_operations"] == len(catalog.operations)
    assert result["total_providers"] == len({x.provider for x in catalog.operations})
    assert result["source_semantic_mappings"] == sum(
        len(x.field_contracts) for x in catalog.operations
    )
    assert "physical_records" not in result
