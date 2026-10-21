def test_competition_requires_same_round_and_nonzero_official_denominator(proof):
    from cil_domain.research.metrics import competition_ratio

    scope = {
        "round_id": "2026-A",
        "stage": "application",
        "role_id": "ICT",
        "location_id": "KR",
        "cutoff": "2026-10-20",
    }
    row = {
        **scope,
        "applicant_count": 100,
        "vacancy_count": 10,
        "numerator_kind": "unique_applicants",
        "denominator_kind": "openings",
        "source_type": "official",
        "source_id": "recruitment-result",
    }
    result = proof.invoke(
        "SK-D03-contract",
        competition_ratio,
        row,
        scope,
        checks={
            "input": lambda b, a, r, e: (
                b["args"][0]["vacancy_count"] == 10
                and b["args"][0]["applicant_count"] == 100
            ),
            "return": lambda b, a, r, e: (
                e is None and r["unit"] == "applicants_per_opening"
            ),
            "relation": lambda b, a, r, e: (
                r["value"]
                == b["args"][0]["applicant_count"] / b["args"][0]["vacancy_count"]
                and "success_probability" not in r
            ),
        },
    )
    assert result["value"] == 10
    assert result["unit"] == "applicants_per_opening"
    assert "success_probability" not in result
    assert (
        competition_ratio({**row, "vacancy_count": 0}, scope)["reason"]
        == "zero_denominator"
    )
    assert competition_ratio({**row, "round_id": "other"}, scope)["value"] is None
    assert (
        competition_ratio({**row, "numerator_kind": "clicks"}, scope)["value"] is None
    )


def test_eligibility_preserves_unknown_and_separates_disqualifiers():
    from cil_domain.research.metrics import eligibility_verdict

    req = {
        "requirement_id": "R1",
        "necessity": "required",
        "field": "credential",
        "operator": "eq",
        "value": "licence-A",
        "source_id": "posting",
    }
    assert eligibility_verdict(req, {})["verdict"] == "unknown"
    assert (
        eligibility_verdict(
            req, {"credential": {"value": "licence-A", "status": "verified"}}
        )["verdict"]
        == "match"
    )
    assert (
        eligibility_verdict(
            {**req, "kind": "ai_proposed"}, {"credential": "licence-A"}
        )["verdict"]
        == "unknown"
    )
    disqualifier = {
        **req,
        "necessity": "disqualifier",
        "field": "disqualified",
        "value": True,
    }
    assert (
        eligibility_verdict(
            disqualifier, {"disqualified": {"value": False, "status": "verified"}}
        )["verdict"]
        == "match"
    )
    assert (
        eligibility_verdict(
            disqualifier, {"disqualified": {"value": True, "status": "verified"}}
        )["verdict"]
        == "no_match"
    )


def test_financial_history_excludes_later_restatements_and_aligns_units():
    from cil_domain.research.metrics import comparable_financials

    common = {
        "entity_id": "E1",
        "concept": "revenue",
        "scope": "consolidated",
        "currency": "KRW",
        "unit": "KRW",
        "frequency": "annual",
        "period_basis": "duration",
    }
    rows = [
        {
            **common,
            "period_end": "2023-12-31",
            "available_at": "2024-03-01T00:00:00Z",
            "value": 80,
        },
        {
            **common,
            "period_end": "2024-12-31",
            "available_at": "2025-03-01T00:00:00Z",
            "value": 100,
        },
        {
            **common,
            "period_end": "2024-12-31",
            "available_at": "2026-03-01T00:00:00Z",
            "value": 130,
        },
    ]
    result = comparable_financials(rows, entity_id="E1", as_of="2025-06-01T00:00:00Z")
    assert [r["value"] for r in result["rows"]] == [80, 100]
    assert result["comparisons"][0]["value"] == 0.25
    assert result["excluded"][0]["reason"] == "not_available_as_of"


def test_wage_conversion_keeps_source_definition_and_requires_hours():
    from cil_domain.research.metrics import wage_conversion

    wage = {"value": 20, "period": "hour", "currency": "EUR", "basis": "gross_base"}
    assert wage_conversion(wage)["value"] is None
    annual = wage_conversion(
        wage, {"hours_per_year": 1800, "author_kind": "user_assumption"}
    )
    assert annual["value"] == 36000
    assert annual["currency"] == "EUR"
    assert annual["assumption_kind"] == "user_assumption"
    assert annual["basis"] == "gross_base"


def test_task_exposure_reports_unmapped_weight_without_replacement_probability():
    from cil_domain.research.metrics import task_exposure

    rows = [
        {"task_id": "T1", "weight": 0.6, "exposure": 0.7, "source_id": "study"},
        {"task_id": "T2", "weight": 0.4, "exposure": None},
    ]
    result = task_exposure(
        rows, {"method_id": "study", "version": "2025", "scale_min": 0, "scale_max": 1}
    )
    assert result["value"] is None
    assert result["coverage"] == 0.6
    assert result["covered_task_score"] == 0.7
    assert result["reason"] == "partial_task_coverage"
    assert "replacement_probability" not in result
