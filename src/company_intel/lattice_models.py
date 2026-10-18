"""Lattice models for multi-perspective cross-national occupational graphs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RoleNode:
    """A canonical occupational role node anchored to ISCO-08 with multi-perspective attributes."""
    role_id: str
    role_name: str
    isco_08: str
    kr_ncs: str | None = None
    kr_keco: str | None = None
    cz_isco: str | None = None
    us_onet: str | None = None
    domain_id: str = "ict_data_ai"
    career_level: int = 1  # 1: Entry/Junior, 2: Mid, 3: Senior, 4: Lead, 5: Director
    salary_band: dict[str, Any] = field(default_factory=dict)
    hiring_demand: str = "stable"  # increasing, very-high, scarce, stable
    skills: list[str] = field(default_factory=list)
    # Consultant view attributes
    value_chain_stage: str = "RND"  # RND, OPS, GTM, CORP
    headcount_share: float = 0.0  # % of total workforce
    peer_staffing_index: float = 1.0  # >1.0 over-indexed vs peer, <1.0 under-indexed
    # Market analyst view attributes
    wage_inflation_rate: float = 0.0  # annual wage growth %
    automation_exposure: float = 0.0  # 0.0 ~ 1.0 exposure to AI automation
    rev_per_hc_leverage: str = "standard"  # top-tier, high, medium, standard
    # Venture founder view attributes
    workflow_role_type: str = "user"  # user, payer, reviewer
    workflow_pain_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "isco_08": self.isco_08,
            "cross_national": {
                "kr_ncs": self.kr_ncs,
                "kr_keco": self.kr_keco,
                "cz_isco": self.cz_isco,
                "us_onet": self.us_onet,
            },
            "domain_id": self.domain_id,
            "career_level": self.career_level,
            "salary_band": self.salary_band,
            "hiring_demand": self.hiring_demand,
            "skills": self.skills,
            "consultant": {
                "value_chain_stage": self.value_chain_stage,
                "headcount_share": self.headcount_share,
                "peer_staffing_index": self.peer_staffing_index,
            },
            "market": {
                "wage_inflation_rate": self.wage_inflation_rate,
                "automation_exposure": self.automation_exposure,
                "rev_per_hc_leverage": self.rev_per_hc_leverage,
            },
            "venture": {
                "workflow_role_type": self.workflow_role_type,
                "workflow_pain_points": self.workflow_pain_points,
            },
        }


@dataclass
class CareerEdge:
    """Directed transition between two occupational roles with explicit skill deltas."""
    from_role_id: str
    to_role_id: str
    transition_type: str  # vertical_promotion, horizontal_transfer, specialization
    required_skills: list[str] = field(default_factory=list)  # ΔSkills: mandatory
    preferred_skills: list[str] = field(default_factory=list)  # ΔSkills: preferred
    qualification_diff: str = "none"  # education, certs, or tenure
    difficulty_stars: int = 1  # 1 to 5
    salary_increment_pct: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_role_id": self.from_role_id,
            "to_role_id": self.to_role_id,
            "transition_type": self.transition_type,
            "skill_delta": {
                "required": self.required_skills,
                "preferred": self.preferred_skills,
            },
            "qualification_diff": self.qualification_diff,
            "difficulty_stars": self.difficulty_stars,
            "salary_increment_pct": self.salary_increment_pct,
        }


@dataclass
class WorkflowConnection:
    """Workflow handoff and bottleneck edge between roles for venture opportunity discovery."""
    from_role_id: str
    to_role_id: str
    step_name: str
    handoff_overhead_hours: float
    pain_point_description: str
    b2b_opportunity: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_role_id": self.from_role_id,
            "to_role_id": self.to_role_id,
            "step_name": self.step_name,
            "handoff_overhead_hours": self.handoff_overhead_hours,
            "pain_point": self.pain_point_description,
            "b2b_opportunity": self.b2b_opportunity,
        }


@dataclass
class LatticeDomainGraph:
    """Multi-perspective domain lattice graph containing roles and all relational edges."""
    domain_id: str
    domain_name: str
    roles: dict[str, RoleNode] = field(default_factory=dict)
    career_edges: list[CareerEdge] = field(default_factory=list)
    workflow_connections: list[WorkflowConnection] = field(default_factory=list)

    def add_role(self, role: RoleNode) -> None:
        self.roles[role.role_id] = role

    def get_role(self, key: str) -> RoleNode | None:
        if key in self.roles:
            return self.roles[key]
        return next((r for r in self.roles.values() if r.isco_08 == key), None)

    def add_career_edge(self, edge: CareerEdge) -> None:
        self.career_edges.append(edge)

    def add_workflow_connection(self, conn: WorkflowConnection) -> None:
        self.workflow_connections.append(conn)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain_id": self.domain_id,
            "domain_name": self.domain_name,
            "roles": {k: v.to_dict() for k, v in self.roles.items()},
            "career_edges": [e.to_dict() for e in self.career_edges],
            "workflow_connections": [w.to_dict() for w in self.workflow_connections],
        }
