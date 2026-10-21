def test_ai_effect_requires_panel_and_does_not_invent_event_returns(proof):
    from cil_application.analysis.service import evaluate_ai_adoption_impact

    empty = proof.invoke(
        "AR-D09-contract",
        evaluate_ai_adoption_impact,
        checks={
            "input": lambda b, a, r, e: b["args"] == () and b["kwargs"] == {},
            "return": lambda b, a, r, e: e is None and r["status"] == "NEEDS_EVIDENCE",
            "relation": lambda b, a, r, e: (
                "executive_summary" not in r and "labor_productivity_did" not in r
            ),
        },
    )
    assert empty["status"] == "NEEDS_EVIDENCE"
    assert "executive_summary" not in empty
    panel = []
    for group, treated in (("T", True), ("C", False)):
        for entity in range(3):
            for post in (False, True):
                panel.append(
                    {
                        "entity_id": group + str(entity),
                        "is_treated": treated,
                        "is_post": post,
                        "ebit_per_employee": 10 + entity + int(post),
                        "sw_job_ratio": 0.2,
                        "admin_job_ratio": 0.3,
                    }
                )
    result = evaluate_ai_adoption_impact(panel)
    assert result["event_study_car"]["status"] == "NEEDS_EVIDENCE"
    assert "p<0.01" not in result["executive_summary"]
