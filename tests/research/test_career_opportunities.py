import pytest


def test_portfolio_requires_gap_deliverables_and_differentiation():
    from cil_domain.research.career_graph import validate_experiment_spec

    proposal = {
        "proposal_id": "one",
        "target_task": "task",
        "baseline": "manual",
        "evaluation": {
            "metric": "error",
            "test_data": "held-out",
            "failure_criteria": "worse than baseline",
        },
        "author_kind": "ai_proposed",
    }
    result = validate_experiment_spec(proposal, "portfolio")
    assert result["status"] == "NEEDS_INPUT"
    assert {"gap_refs", "deliverables", "differentiation"} <= set(result["missing"])


def test_all_six_purposes_reach_separate_evidence_and_proposal_tables(tmp_path):
    import json
    from cil_contracts.requests import ReportRequest
    from cil_application.research.report_service import run_research
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    available = "2026-10-19T00:00:00Z"
    scope = {
        "round_id": "round",
        "stage": "application",
        "role_id": "R",
        "location_id": "CZ",
        "cutoff": "2026-10-20",
    }
    posting = {
        "provider_id": "saved",
        "posting_id": "P",
        "revision": "r1",
        "entity_id": "E",
        "role_id": "R",
        "location_id": "CZ",
        "vacancy_batch_id": "round",
        "cluster_signature": "CZ:PRIVATE:ALL:REGULAR:ONSITE",
        "available_at": available,
        "requirements": [
            {
                "requirement_id": "credential",
                "necessity": "required",
                "field": "credential",
                "value": "A",
                "source_id": "posting",
            }
        ],
    }
    financial = {
        "entity_id": "E",
        "concept": "revenue",
        "scope": "consolidated",
        "currency": "EUR",
        "unit": "EUR",
        "frequency": "annual",
        "period_basis": "duration",
    }
    snapshot = {
        "source_kind": "fixture",
        "postings": [posting],
        "profiles": {"me": {"credential": {"value": "B", "status": "self_reported"}}},
        "competition": [
            {
                "posting_id": "P",
                **scope,
                "applicant_count": 20,
                "vacancy_count": 2,
                "numerator_kind": "unique_applicants",
                "denominator_kind": "openings",
                "source_type": "official",
                "source_id": "recruitment",
                "available_at": available,
            }
        ],
        "financials": [
            {
                **financial,
                "period_start": "2023-01-01",
                "period_end": "2023-12-31",
                "available_at": "2024-03-01T00:00:00Z",
                "value": 80,
                "source_id": "rev-2023",
            },
            {
                **financial,
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "available_at": "2025-03-01T00:00:00Z",
                "value": 100,
                "source_id": "rev-2024",
            },
        ],
        "wages": [
            {
                "role_id": "R",
                "country": "CZ",
                "value": 50000,
                "period": "year",
                "currency": "EUR",
                "basis": "gross",
                "source_id": "wage",
                "available_at": available,
            }
        ],
        "tasks": [
            {
                "task_id": "T1",
                "role_id": "R",
                "weight": 0.5,
                "exposure": 0.2,
                "source_id": "study",
            },
            {
                "task_id": "T2",
                "role_id": "R",
                "weight": 0.5,
                "exposure": 0.6,
                "source_id": "study",
            },
        ],
        "career_graph": {
            "architecture": "dual_ladder",
            "employer_id": "E",
            "nodes": [
                {"node_id": "engineer", "role_track": "IC_specialist"},
                {"node_id": "manager", "role_track": "people_management"},
            ],
            "edges": [
                {
                    "from": "engineer",
                    "to": "manager",
                    "relation": "track_switch",
                    "evidence_kind": "employer_policy",
                    "employer_id": "E",
                    "source_id": "career-policy",
                    "available_at": available,
                },
                {
                    "from": "manager",
                    "to": "engineer",
                    "relation": "proposed",
                    "evidence_kind": "ai_proposed",
                },
            ],
        },
        "opportunities": [
            {
                "opportunity_id": "issue",
                "source_type": "oss_issue",
                "source_id": "issue-source",
                "title": "schema mismatch",
            }
        ],
        "portfolio_plans": [
            {
                "proposal_id": "portfolio",
                "target_task": "T1",
                "gap_refs": ["credential"],
                "baseline": "manual",
                "evaluation": {
                    "metric": "error rate",
                    "test_data": "fixture-held-out",
                    "failure_criteria": "worse than baseline",
                },
                "deliverables": ["agent code", "evaluation.json"],
                "differentiation": "source-field preservation measured against baseline",
                "dataset_rights": "fixture-reusable",
                "author_kind": "ai_proposed",
            }
        ],
        "venture_hypotheses": [
            {
                "proposal_id": "venture",
                "buyer": "department",
                "user": "analyst",
                "payer": "department owner",
                "problem": "schema mismatch",
                "substitutes": ["manual"],
                "pilot": {
                    "offer": "sandbox pilot",
                    "price": {"amount": 5, "currency": "EUR"},
                    "success_criteria": "paid pilot and fewer errors",
                    "failure_criteria": "no paid pilot",
                    "sample_definition": "fixture users",
                },
                "kill_criteria": ["no buyer"],
                "jurisdictions": ["CZ"],
                "author_kind": "ai_proposed",
            }
        ],
        "scenarios": [
            {
                "scenario_id": "growth",
                "method_id": "compound_growth/v1",
                "base_source_id": "rev-2024",
                "growth_rate": 0.1,
                "years": 2,
                "author_kind": "user_assumption",
            }
        ],
    }
    for collection in ("tasks", "opportunities"):
        for row in snapshot[collection]:
            row["available_at"] = available
    request = ReportRequest.from_dict(
        {
            "purpose": [
                "selected-posting",
                "financial",
                "work-future",
                "path",
                "portfolio",
                "venture",
            ],
            "question": "시연의 모든 조사 목적",
            "as_of": "2026-10-20T00:00:00Z",
            "profile_ref": "me",
            "subject_refs": [
                {"provider_id": "saved", "posting_id": "P", "revision": "r1"}
            ],
            "exposure_method": {
                "method_id": "fixture-study",
                "version": "1",
                "scale_min": 0,
                "scale_max": 1,
            },
            "argument_origins": [{"json_pointer": "/", "origin": "user_explicit"}],
        }
    )
    store = ResearchArtifactStore(tmp_path)
    snapshot["portfolio_plans"][0]["budget"] = {"amount": 100, "currency": "EUR"}
    result = run_research(
        request,
        snapshot,
        CapabilityRegistry(),
        store,
        renderer=render_research_workbook,
    )
    tables = json.loads(store.read("tables.json"))
    assert result["selected_skills"] == [f"S{i:02}" for i in range(1, 9)]
    assert tables["Competition"][0]["value"] == 10
    assert tables["Requirements"][0]["verdict"] == "no_match"
    assert tables["TaskExposure"][0]["value"] == pytest.approx(0.4)
    assert tables["WageBenchmarks"][0]["value"] == 50000
    assert tables["Scenarios"][0]["computed_value"] == pytest.approx(121)
    assert tables["PortfolioPlans"][0]["validation_status"] == "PROPOSED"
    assert tables["VentureHypotheses"][0]["validation_status"] == "PROPOSED"
    assert tables["OpportunityEvidence"][0]["payment_evidence_status"] == "not_observed"
    assert len(tables["ProposedPaths"]) == 1
    from cil_application.research.report_service import seal_report

    sentence = "시연 포트폴리오 예산은 100 EUR다."
    claims = {
        "contract_version": "research-claims-v1",
        "manifest_sha256": result["manifest_sha256"],
        "claims": [
            {
                "claim_id": "budget",
                "text": sentence,
                "kind": "ai_proposed",
                "value": 100,
                "unit": "EUR",
                "assumptions": ["실험 예산 제안"],
                "refs": [
                    {
                        "table_id": "PortfolioPlans",
                        "row_id": tables["PortfolioPlans"][0]["_row_id"],
                        "column_id": "budget",
                        "value_pointer": "/amount",
                    }
                ],
            }
        ],
    }
    assert (
        seal_report(store, result["manifest_sha256"], sentence, claims)["status"]
        == "REFERENCES_VALIDATED"
    )
    assert all(
        e["evidence_kind"] != "ai_proposed"
        for e in json.loads(store.read("facts/raw.json"))["career_graph"]["edges"]
    )


def test_career_relationships_do_not_turn_similarity_into_official_promotion(proof):
    from cil_contracts.career_proposals import CareerGraph
    from cil_domain.research.career_graph import validate_career_edges

    nodes = [
        {"node_id": "backend", "role_track": "IC_specialist"},
        {"node_id": "data", "role_track": "IC_specialist"},
    ]
    edge = {
        "from": "backend",
        "to": "data",
        "relation": "skill_similarity",
        "evidence_kind": "ai_proposed",
    }
    graph = CareerGraph(nodes=nodes, edges=[edge], architecture="career_lattice")
    result = proof.invoke(
        "SK-D04-contract",
        validate_career_edges,
        graph,
        checks={
            "input": lambda b, a, r, e: (
                b["args"][0].edges[0]["relation"] == "skill_similarity"
            ),
            "return": lambda b, a, r, e: (
                e is None and r["architecture"] == "career_lattice"
            ),
            "relation": lambda b, a, r, e: (
                r["edges"][0]["relation"] == b["args"][0].edges[0]["relation"]
                and b["args"][0] == a["args"][0]
            ),
        },
    )
    assert result["edges"][0]["relation"] == "skill_similarity"
    assert result["edges"][0]["evidence_kind"] == "ai_proposed"
    with pytest.raises(ValueError, match="official"):
        validate_career_edges(
            CareerGraph(
                nodes=nodes,
                edges=[
                    {
                        **edge,
                        "relation": "promotion",
                        "evidence_kind": "employer_policy",
                    }
                ],
                architecture="dual_ladder",
            )
        )


def test_unpriced_venture_remains_unconfirmed():
    from cil_domain.research.career_graph import validate_experiment_spec

    proposal = {
        "proposal_id": "one",
        "buyer": "buyer",
        "user": "user",
        "payer": "payer",
        "problem": "problem",
        "substitutes": ["manual"],
        "pilot": {"offer": "trial"},
        "kill_criteria": ["no buyer"],
        "author_kind": "ai_proposed",
    }
    result = validate_experiment_spec(proposal, "venture")
    assert result["status"] == "NEEDS_INPUT" and "pilot.price" in result["missing"]


def test_future_and_undated_task_evidence_is_excluded_from_as_of_analysis():
    from cil_application.research.report_service import _available_records

    snapshot = {
        "tasks": [
            {"task_id": "future", "available_at": "2027-01-01T00:00:00Z"},
            {"task_id": "unknown"},
            {"task_id": "past", "source_id": "s"},
        ],
        "sources": [{"source_id": "s", "available_at": "2026-01-01T00:00:00Z"}],
    }
    gaps = []
    rows = list(_available_records(snapshot, "tasks", "2026-10-20T00:00:00Z", gaps))
    assert [r["task_id"] for r in rows] == ["past"]
    assert {g["reason"] for g in gaps} == {
        "not_available_as_of",
        "evidence_availability_unknown",
    }
