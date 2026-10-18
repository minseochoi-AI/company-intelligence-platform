"""Unit tests for the 4-Audience Multi-Perspective Occupational Track Lattice."""
from __future__ import annotations

from company_intel.lattice_models import (
    CareerEdge,
    LatticeDomainGraph,
    RoleNode,
    WorkflowConnection,
)
from company_intel.track_lattice import (
    TrackLatticeEngine,
    get_default_ict_data_ai_graph,
)


def test_lattice_models_serialization():
    role = RoleNode(
        role_id="test-analyst",
        role_name="Test Analyst",
        isco_08="2511",
        kr_ncs="02010101",
        cz_isco="25110",
        us_onet="15-1211.00",
        career_level=2,
        salary_band={"krw_min": 40000000, "krw_max": 60000000},
        hiring_demand="increasing",
        skills=["SQL", "Python"],
        value_chain_stage="OPS",
        headcount_share=10.0,
        peer_staffing_index=1.1,
        wage_inflation_rate=5.5,
        automation_exposure=0.4,
        rev_per_hc_leverage="high",
        workflow_role_type="user",
        workflow_pain_points=["manual data entry"],
    )

    data = role.to_dict()
    assert data["role_id"] == "test-analyst"
    assert data["cross_national"]["kr_ncs"] == "02010101"
    assert data["cross_national"]["cz_isco"] == "25110"
    assert data["cross_national"]["us_onet"] == "15-1211.00"
    assert data["consultant"]["value_chain_stage"] == "OPS"
    assert data["market"]["wage_inflation_rate"] == 5.5
    assert data["venture"]["workflow_role_type"] == "user"

    edge = CareerEdge(
        from_role_id="test-analyst",
        to_role_id="test-engineer",
        transition_type="vertical_promotion",
        required_skills=["Spark", "Kafka"],
        difficulty_stars=3,
        salary_increment_pct=25.0,
    )
    edge_data = edge.to_dict()
    assert edge_data["transition_type"] == "vertical_promotion"
    assert edge_data["skill_delta"]["required"] == ["Spark", "Kafka"]
    assert edge_data["difficulty_stars"] == 3

    conn = WorkflowConnection(
        from_role_id="test-analyst",
        to_role_id="test-lead",
        step_name="Step 1",
        handoff_overhead_hours=10.0,
        pain_point_description="schema mismatch",
        b2b_opportunity={"product": "SchemaGuard", "wtp": "$2000"},
    )
    conn_data = conn.to_dict()
    assert conn_data["handoff_overhead_hours"] == 10.0
    assert conn_data["b2b_opportunity"]["product"] == "SchemaGuard"

    graph = LatticeDomainGraph("test_domain", "Test Domain")
    graph.add_role(role)
    graph.add_career_edge(edge)
    graph.add_workflow_connection(conn)
    g_data = graph.to_dict()
    assert "test-analyst" in g_data["roles"]
    assert len(g_data["career_edges"]) == 1
    assert len(g_data["workflow_connections"]) == 1


def test_track_lattice_engine_four_projections():
    graph = get_default_ict_data_ai_graph()
    engine = TrackLatticeEngine(graph)

    # 1. Career View Projection
    career_view = engine.project_career_view()
    assert career_view["perspective"] == "career"
    assert len(career_view["roles"]) == 8
    assert len(career_view["edges"]) >= 8
    assert "flowchart LR" in career_view["mermaid"]
    assert "2511_data_analyst" in career_view["mermaid"]
    assert "Δ필수" in career_view["mermaid"]

    # Filtered Career View Projection
    single_career = engine.project_career_view("2511-data-analyst")
    assert any(r["role_id"] == "2511-data-analyst" for r in single_career["roles"])

    # 2. Consultant View Projection
    consultant_view = engine.project_consultant_view()
    assert consultant_view["perspective"] == "consultant"
    assert "RND" in consultant_view["stages"]
    assert "OPS" in consultant_view["stages"]
    assert "GTM" in consultant_view["stages"]
    assert "CORP" in consultant_view["stages"]
    assert "flowchart TD" in consultant_view["mermaid"]
    assert "subgraph VC_RND" in consultant_view["mermaid"]
    assert "피어 대비" in consultant_view["mermaid"]

    # 3. Market View Projection
    market_view = engine.project_market_view()
    assert market_view["perspective"] == "market"
    assert "flowchart TD" in market_view["mermaid"]
    assert "Revenue Leverage" in market_view["mermaid"]
    assert "Labor Cost Inflation" in market_view["mermaid"]
    assert "임금 상승 압력" in market_view["mermaid"]

    # 4. Venture View Projection
    venture_view = engine.project_venture_view()
    assert venture_view["perspective"] == "venture"
    assert "flowchart LR" in venture_view["mermaid"]
    assert "Pain Point" in venture_view["mermaid"]
    assert "B2B Startup Opportunity" in venture_view["mermaid"]
    assert len(venture_view["connections"]) == 3

    # ASCII Summary
    summary = engine.render_ascii_summary("2511-data-analyst")
    assert "2511-data-analyst" in summary
    assert "ISCO-08 2511" in summary
    assert "KR NCS 02010101" in summary
    assert "CZ-ISCO 25110" in summary
    assert "US O*NET 15-1211.00" in summary
    assert "[1. Career View]" in summary
    assert "[2. Consultant View]" in summary
    assert "[3. Market Analyst]" in summary
    assert "[4. Venture Founder]" in summary


def test_multi_domain_registry_and_grand_unified_graph():
    from company_intel.lattice_domains import DOMAIN_METADATA, get_domain_graph

    # Verify 12 domains metadata
    assert len(DOMAIN_METADATA) >= 13
    assert "semiconductor_electronics" in DOMAIN_METADATA
    assert "mobility_robotics" in DOMAIN_METADATA
    assert "bio_pharma_healthcare" in DOMAIN_METADATA
    assert "chemical_battery_energy" in DOMAIN_METADATA
    assert "management_business_hr" in DOMAIN_METADATA
    assert "finance_investment_fintech" in DOMAIN_METADATA

    # Verify Semiconductor domain graph
    semi_graph = get_domain_graph("semiconductor")
    assert semi_graph.domain_id == "semiconductor_electronics"
    assert "2152-circuit-designer" in semi_graph.roles
    assert "1321-fab-director" in semi_graph.roles

    # Verify Grand Unified Macro graph
    macro_graph = get_domain_graph("all")
    assert macro_graph.domain_id == "grand_unified"
    assert len(macro_graph.roles) >= 40
    # Check cross-domain mobility bridges
    bridge_found = any(
        e.from_role_id == "2512-fullstack-dev" and e.to_role_id == "2144-autonomous-robotics-eng"
        for e in macro_graph.career_edges
    )
    assert bridge_found

    # Test engine with Grand Unified Macro Graph
    engine = TrackLatticeEngine(macro_graph)
    career_view = engine.project_career_view()
    assert len(career_view["roles"]) >= 40
    summary = engine.render_ascii_summary()
    assert "12대 핵심 산업 분야 & 3국 텍사노미 전수 매핑 체계" in summary
    assert "총 직무 노드 수:" in summary

