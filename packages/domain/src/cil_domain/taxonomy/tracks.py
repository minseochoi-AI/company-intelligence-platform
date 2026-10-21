"""Canonical responsibility owner; migrated from src/company_intel/track_lattice.py."""

from __future__ import annotations
from cil_contracts.taxonomy import CareerEdge
from cil_contracts.taxonomy import LatticeDomainGraph
from cil_contracts.taxonomy import RoleNode
from cil_contracts.taxonomy import WorkflowConnection
from cil_domain.taxonomy.templates import DOMAIN_METADATA
from cil_domain.taxonomy.templates import DOMAIN_REGISTRY
from cil_domain.taxonomy.templates import build_ict_domain
from cil_domain.taxonomy.templates import get_domain_graph
from typing import Any


def get_default_ict_data_ai_graph() -> LatticeDomainGraph:
    """Build canonical full-depth ICT/SW & Data/AI occupational domain graph."""
    return build_ict_domain()


class TrackLatticeEngine:
    """Projection and rendering engine for the 4-audience occupational lattice."""

    def __init__(self, graph: LatticeDomainGraph | None = None) -> None:
        self.graph = graph or get_domain_graph("all")

    def project_career_view(self, target_role_id: str | None = None) -> dict[str, Any]:
        """Project the Job Seeker (Career) view with explicit skill deltas and wage bands."""
        roles = self.graph.roles
        edges = self.graph.career_edges
        if target_role_id and target_role_id in roles:
            connected = {target_role_id}
            for e in edges:
                if e.from_role_id == target_role_id or e.to_role_id == target_role_id:
                    connected.add(e.from_role_id)
                    connected.add(e.to_role_id)
            roles = {k: v for k, v in roles.items() if k in connected}
            edges = [
                e
                for e in edges
                if e.from_role_id in connected and e.to_role_id in connected
            ]
        mermaid_lines = ["flowchart LR", "  %% Styling"]
        mermaid_lines.append(
            "  classDef junior fill:#EBF5FB,stroke:#2980B9,stroke-width:2px;"
        )
        mermaid_lines.append(
            "  classDef senior fill:#E8F8F5,stroke:#27AE60,stroke-width:2px;"
        )
        mermaid_lines.append(
            "  classDef lead fill:#FEF9E7,stroke:#F39C12,stroke-width:2px;"
        )
        for role_id, role in roles.items():
            safe_id = role_id.replace("-", "_")
            cls = (
                "junior"
                if (role.career_level or 0) <= 1
                else "senior"
                if (role.career_level or 0) <= 3
                else "lead"
            )
            krw_min = f"{role.salary_band.get('krw_min', 0) // 10000:,}만"
            krw_max = f"{role.salary_band.get('krw_max', 0) // 10000:,}만"
            mermaid_lines.append(
                f'  {safe_id}["<b>{role.role_name}</b><br/>• ISCO-08: {role.isco_08} (KR: {role.kr_ncs or "N/A"} / CZ: {role.cz_isco or "N/A"})<br/>• 임금: {krw_min} ~ {krw_max} 원<br/>• 채용 수요: [{role.hiring_demand}]"]:::{cls}'
            )
        for e in edges:
            u = e.from_role_id.replace("-", "_")
            v = e.to_role_id.replace("-", "_")
            diff = (
                "unknown"
                if e.difficulty_stars is None
                else "★" * e.difficulty_stars + "☆" * (5 - e.difficulty_stars)
            )
            req = ", ".join(e.required_skills[:3])
            label = f'"[{e.transition_type}]<br/>Δ필수: {req}<br/>난이도: {diff}"'
            arrow = "-->" if e.transition_type == "vertical_promotion" else "-.->"
            mermaid_lines.append(f"  {u} {arrow}|{label}| {v}")
        return {
            "evidence_status": self.graph.evidence_status,
            "limitations": [
                "Curated diagrams are illustrative proposals, not observed salary, demand or employer promotion rules."
            ],
            "perspective": "career",
            "domain_id": self.graph.domain_id,
            "roles": [r.to_dict() for r in roles.values()],
            "edges": [e.to_dict() for e in edges],
            "mermaid": "\n".join(mermaid_lines),
        }

    def project_consultant_view(self) -> dict[str, Any]:
        """Project the Management Consultant view organized by enterprise value chain stages."""
        stages: dict[str, list[RoleNode]] = {
            "RND": [],
            "OPS": [],
            "GTM": [],
            "CORP": [],
        }
        for role in self.graph.roles.values():
            stage = (
                role.value_chain_stage if role.value_chain_stage in stages else "RND"
            )
            stages[stage].append(role)
        mermaid_lines = ["flowchart TD", "  %% Enterprise Value Chain Workforce Map"]
        stage_names = {
            "RND": "가치사슬 1단계: R&D 및 제품 혁신 (R&D & Innovation)",
            "OPS": "가치사슬 2단계: 운영 및 인프라 신뢰성 (Operations & Reliability)",
            "GTM": "가치사슬 3단계: 사업화 및 고객 접점 (GTM & Commercial)",
            "CORP": "가치사슬 4단계: 경영지원 및 거버넌스 (Governance & Support)",
        }
        for stage_key, stage_title in stage_names.items():
            mermaid_lines.append(f'  subgraph VC_{stage_key} ["{stage_title}"]')
            for role in stages[stage_key]:
                safe_id = role.role_id.replace("-", "_")
                p_diff = f"{('+' if role.peer_staffing_index >= 1.0 else '')}{(role.peer_staffing_index - 1.0) * 100:.0f}%p"
                mermaid_lines.append(
                    f'    {safe_id}["<b>{role.role_name}</b><br/>[인력 비중: {role.headcount_share:.1f}% | 피어 대비: {p_diff}]"]'
                )
            mermaid_lines.append("  end")
        mermaid_lines.append("  VC_RND ==>|기술 자산 이전| VC_OPS")
        mermaid_lines.append("  VC_OPS ==>|제품 SLA 보증| VC_GTM")
        mermaid_lines.append("  VC_CORP -.->|전사 거버넌스 지원| VC_RND")
        mermaid_lines.append("  VC_CORP -.->|전사 거버넌스 지원| VC_GTM")
        return {
            "evidence_status": self.graph.evidence_status,
            "limitations": [
                "Curated diagrams are illustrative proposals, not observed salary, demand or employer promotion rules."
            ],
            "perspective": "consultant",
            "domain_id": self.graph.domain_id,
            "stages": {k: [r.to_dict() for r in v] for k, v in stages.items()},
            "mermaid": "\n".join(mermaid_lines),
        }

    def project_market_view(self) -> dict[str, Any]:
        """Project the Equity Analyst view showing human capital ROI and wage inflation drivers."""
        mermaid_lines = [
            "flowchart TD",
            "  %% Equity Analyst Value Driver Tree",
            "  classDef target fill:#FDEDEC,stroke:#C0392B,stroke-width:2px;",
            "  classDef intermediate fill:#FEF5E7,stroke:#D35400,stroke-width:1.5px;",
            "  classDef driver fill:#EAFAF1,stroke:#27AE60,stroke-width:1.5px;",
            '  Top["<b>전사 영업이익률 및 인적자본 생산성</b><br/>(Rev per HC: 4.8억 원 / OPM: 22.4%)"]:::target',
            '  RevNode["<b>1인당 매출 레버리지 (Revenue Leverage)</b><br/>• R&D 및 GTM 직군 생산성에 비례"]:::intermediate',
            '  CostNode["<b>한계 인건비 압력 (Labor Cost Inflation)</b><br/>• 총 인건비 비중: 매출액의 42%"]:::intermediate',
            "  Top --> RevNode",
            "  Top --> CostNode",
        ]
        for role in self.graph.roles.values():
            if role.rev_per_hc_leverage in {"top-tier", "high"}:
                safe_id = f"Rev_{role.role_id.replace('-', '_')}"
                mermaid_lines.append(
                    f'  {safe_id}["<b>{role.role_name}</b><br/>• 레버리지: {role.rev_per_hc_leverage}<br/>• 자동화 노출도: {role.automation_exposure:.2f}"]:::driver'
                )
                mermaid_lines.append(f"  RevNode --> {safe_id}")
        for role in self.graph.roles.values():
            if role.wage_inflation_rate >= 8.0:
                safe_id = f"Cost_{role.role_id.replace('-', '_')}"
                mermaid_lines.append(
                    f'  {safe_id}["<b>{role.role_name}</b><br/>• 연간 임금 상승 압력: +{role.wage_inflation_rate:.1f}%<br/>• 비중: {role.headcount_share:.1f}%"]:::driver'
                )
                mermaid_lines.append(f"  CostNode --> {safe_id}")
        return {
            "evidence_status": self.graph.evidence_status,
            "limitations": [
                "Curated diagrams are illustrative proposals, not observed salary, demand or employer promotion rules."
            ],
            "perspective": "market",
            "domain_id": self.graph.domain_id,
            "mermaid": "\n".join(mermaid_lines),
        }

    def project_venture_view(self) -> dict[str, Any]:
        """Project the Venture Founder view showing workflow friction and B2B opportunities."""
        mermaid_lines = [
            "flowchart LR",
            "  %% Venture Opportunity & Bottleneck Map",
            "  classDef role fill:#EBF5FB,stroke:#2980B9,stroke-width:2px;",
            "  classDef pain fill:#FDEDEC,stroke:#E74C3C,stroke-width:2px;",
            "  classDef opp fill:#EAFAF1,stroke:#27AE60,stroke-width:2px;",
        ]
        connections = self.graph.workflow_connections
        for i, conn in enumerate(connections):
            step_id = f"Step_{i + 1}"
            u_role = self.graph.roles.get(conn.from_role_id)
            u_name = u_role.role_name if u_role else conn.from_role_id
            u_type = u_role.workflow_role_type if u_role else "user"
            mermaid_lines.append(f'  subgraph {step_id} ["{conn.step_name}"]')
            mermaid_lines.append(f'    R_{i}["<b>{u_name} ({u_type})</b>"]:::role')
            mermaid_lines.append(
                f'    P_{i}["<b>[Pain Point]</b><br/>• 지연: 주 {conn.handoff_overhead_hours:.1f}시간<br/>• {conn.pain_point_description}"]:::pain'
            )
            mermaid_lines.append(f"    R_{i} --- P_{i}")
            mermaid_lines.append("  end")
            b2b = conn.b2b_opportunity
            opp_id = f"Opp_{i + 1}"
            mermaid_lines.append(
                f'  {opp_id}["<b>[B2B Startup Opportunity]</b><br/>• 솔루션: {b2b.get("product_name", "B2B SaaS")}<br/>• 구매자: {b2b.get("target_buyer", "Payer")}<br/>• 예상 WTP: {b2b.get("estimated_wtp", "월 $1,000+")}"]:::opp'
            )
            mermaid_lines.append(f"  P_{i} -.->|솔루션 침투| {opp_id}")
        for i in range(len(connections) - 1):
            mermaid_lines.append(f"  Step_{i + 1} ==> Step_{i + 2}")
        return {
            "evidence_status": self.graph.evidence_status,
            "limitations": [
                "Curated diagrams are illustrative proposals, not observed salary, demand or employer promotion rules."
            ],
            "perspective": "venture",
            "domain_id": self.graph.domain_id,
            "connections": [c.to_dict() for c in connections],
            "mermaid": "\n".join(mermaid_lines),
        }

    def render_ascii_summary(self, role_id: str | None = None) -> str:
        """Render a concise ASCII summary suitable for terminal CLI inspection."""
        lines = [
            "=" * 78,
            " [CIL 4-Audience Multi-Perspective Occupational Track Lattice Summary]",
            f" Domain: {self.graph.domain_name} ({self.graph.domain_id})",
            "=" * 78,
        ]
        if self.graph.domain_id == "grand_unified":
            lines.append(
                "\n[12대 핵심 산업 분야 & 3국 텍사노미 전수 매핑 체계 (24개 NCS / CZ-ISCO / O*NET)]"
            )
            lines.append("-" * 78)
            for d_id, meta in DOMAIN_METADATA.items():
                if d_id == "grand_unified":
                    continue
                lines.append(f"• [{d_id}] {meta['name_ko']}")
                lines.append(
                    f"   KR NCS: {meta['kr_ncs_major']} | CZ-ISCO: {meta['cz_isco_major']}"
                )
                lines.append(f"   US O*NET: {meta['us_onet_major']}")
            lines.append("-" * 78)
            lines.append(
                f"총 직무 노드 수: {len(self.graph.roles)}개 | 경력 전이 엣지: {len(self.graph.career_edges)}개 (산업 간 전이 브릿지 포함) | B2B 워크플로우 결속: {len(self.graph.workflow_connections)}개"
            )
        target_roles = (
            [self.graph.roles[role_id]]
            if role_id and role_id in self.graph.roles
            else list(self.graph.roles.values())
        )
        for r in target_roles:
            lines.append(f"\n▶ [{r.role_id}] {r.role_name} (Level {r.career_level})")
            lines.append(
                f"  • Cross-National: ISCO-08 {r.isco_08} | KR NCS {r.kr_ncs or 'N/A'} | CZ-ISCO {r.cz_isco or 'N/A'} | US O*NET {r.us_onet or 'N/A'}"
            )
            krw_min = f"{r.salary_band.get('krw_min', 0) // 10000:,}만"
            krw_max = f"{r.salary_band.get('krw_max', 0) // 10000:,}만"
            lines.append(
                f"  [1. Career View] Salary: {krw_min} ~ {krw_max} KRW | Demand: {r.hiring_demand} | Skills: {', '.join(r.skills[:4])}"
            )
            lines.append(
                f"  [2. Consultant View] Stage: {r.value_chain_stage} | Headcount Share: {r.headcount_share:.1f}% | Peer Staffing Index: {r.peer_staffing_index:.2f}x"
            )
            lines.append(
                f"  [3. Market Analyst] Wage Inflation: +{r.wage_inflation_rate:.1f}%/yr | Automation Exposure: {r.automation_exposure:.2f} | Leverage: {r.rev_per_hc_leverage}"
            )
            lines.append(
                f"  [4. Venture Founder] Role Type: {r.workflow_role_type} | Pain Points: {'; '.join(r.workflow_pain_points[:2])}"
            )
        lines.append("\n" + "=" * 78)
        return "\n".join(lines)
