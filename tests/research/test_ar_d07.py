def test_taxonomy_does_not_manufacture_crosswalks_salaries_or_promotions(proof):
    from cil_domain.taxonomy.lattice import (
        DeterministicLatticeSynthesizer,
        DeterministicTaxonomyItem,
    )

    item = DeterministicTaxonomyItem(
        "2512",
        "Software developers",
        "",
        "Write software",
        "",
        ["2511"],
        "2",
        "25",
        "251",
    )
    other = DeterministicTaxonomyItem(
        "2511", "Systems analysts", "", "Analyse systems", "", [], "2", "25", "251"
    )
    synthesizer = DeterministicLatticeSynthesizer(
        taxonomy={"2512": item, "2511": other}
    )
    graph = proof.invoke(
        "AR-D07-contract",
        synthesizer.build_deterministic_macro_graph,
        checks={
            "input": lambda b, a, r, e: set(b["state"]) == {"2512", "2511"},
            "return": lambda b, a, r, e: e is None and set(r.roles) == {"2512", "2511"},
            "relation": lambda b, a, r, e: (
                r.roles["2512"].us_onet is None
                and r.roles["2512"].salary_band == {}
                and all(
                    edge.transition_type == "taxonomy_related"
                    for edge in r.career_edges
                )
            ),
        },
        observe=lambda: synthesizer.taxonomy,
    )
    node = graph.roles["2512"]
    assert node.us_onet is None and node.kr_ncs is None
    assert node.salary_band == {} and node.automation_exposure is None
    assert all(
        edge.transition_type == "taxonomy_related" and edge.salary_increment_pct is None
        for edge in graph.career_edges
    )
    assert graph.workflow_connections == []
