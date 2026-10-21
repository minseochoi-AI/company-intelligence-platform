"""Canonical responsibility owner; migrated from src/company_intel/deterministic_lattice.py."""

from __future__ import annotations
from cil_contracts.taxonomy import CareerEdge
from cil_contracts.taxonomy import LatticeDomainGraph
from cil_contracts.taxonomy import RoleNode
from cil_contracts.taxonomy import WorkflowConnection
from cil_domain.taxonomy.facts import NCS_TO_ISCO_MAP
from dataclasses import dataclass, field
from typing import Any
import logging
import re

logger = logging.getLogger(__name__)

ISCO_MAJOR_DOMAIN_MAP: dict[str, str] = {
    "1": "경영/비즈니스 (Business & Strategy)",
    "2": "전문직 (IT/공학/자연과학/의료/금융)",
    "3": "준전문직/기술공 (Technical & Associate Professionals)",
    "4": "사무직 (Clerical Support & Operations)",
    "5": "서비스/영업 (Services & Sales)",
    "6": "농림어업 (Agriculture, Forestry & Fishery)",
    "7": "기능원 (Craft & Related Trades)",
    "8": "장치/기계조작 (Plant & Machine Operators)",
    "9": "단순노무 (Elementary Occupations)",
    "0": "국방/공공안보 (Armed Forces)",
}

SUBMAJOR_TO_DOMAIN_ID: dict[str, str] = {
    "11": "business_strategy",
    "12": "business_strategy",
    "13": "mobility_robotics",
    "14": "marketing_sales",
    "21": "semiconductor",
    "22": "bio_healthcare",
    "23": "business_strategy",
    "24": "finance_investment",
    "25": "ict_data_ai",
    "26": "legal_ip",
    "31": "semiconductor",
    "32": "bio_healthcare",
    "33": "finance_investment",
    "34": "legal_ip",
    "35": "ict_data_ai",
    "41": "business_strategy",
    "42": "marketing_sales",
    "43": "business_strategy",
    "44": "business_strategy",
    "51": "marketing_sales",
    "52": "marketing_sales",
    "53": "bio_healthcare",
    "54": "environment_safety",
    "61": "environment_safety",
    "62": "environment_safety",
    "63": "environment_safety",
    "71": "construction_architecture",
    "72": "mobility_robotics",
    "73": "culture_design",
    "74": "semiconductor",
    "75": "mobility_robotics",
    "81": "battery_energy",
    "82": "battery_energy",
    "83": "mobility_robotics",
    "91": "environment_safety",
    "92": "environment_safety",
    "93": "mobility_robotics",
    "94": "marketing_sales",
    "95": "marketing_sales",
    "96": "environment_safety",
    "01": "legal_ip",
    "02": "legal_ip",
    "03": "legal_ip",
}

DOMAIN_ID_TO_LABEL: dict[str, str] = {
    "ict_data_ai": "ICT / Software & Data / AI",
    "semiconductor": "반도체 / 전자회로 / 하드웨어",
    "mobility_robotics": "모빌리티 / 자율주행 / 로보틱스",
    "bio_healthcare": "바이오 / 제약 / 임상헬스케어",
    "battery_energy": "배터리 / 신소재 / 에너지",
    "business_strategy": "경영전략 / 인사 / 사업개발",
    "finance_investment": "금융투자 / 핀테크 / 리스크",
    "marketing_sales": "B2B영업 / 마케팅 / GTM",
    "legal_ip": "법률 / 지식재산권 / 변리",
    "construction_architecture": "스마트건축 / 토목 / 인프라",
    "culture_design": "디자인 / 디지털미디어 / 콘텐츠",
    "environment_safety": "탄소중립 / 산업안전 / ESG",
}

SUBMAJOR_TO_MANAGER: dict[str, str] = {
    "11": "1120",
    "12": "1120",
    "13": "1120",
    "14": "1120",
    "21": "1321",
    "22": "1342",
    "23": "1345",
    "24": "1211",
    "25": "1330",
    "26": "1219",
    "31": "1321",
    "32": "1342",
    "33": "1219",
    "34": "1219",
    "35": "1330",
    "41": "1219",
    "42": "1219",
    "43": "1219",
    "44": "1219",
    "51": "1411",
    "52": "1420",
    "53": "1342",
    "54": "1349",
    "61": "1311",
    "62": "1312",
    "63": "1311",
    "71": "1323",
    "72": "1321",
    "73": "1321",
    "74": "1324",
    "75": "1321",
    "81": "1321",
    "82": "1321",
    "83": "1324",
    "91": "1412",
    "92": "1311",
    "93": "1321",
    "94": "1412",
    "95": "1420",
    "96": "1349",
    "01": "0110",
    "02": "0110",
    "03": "0110",
}


@dataclass
class DeterministicTaxonomyItem:
    code: str
    title_en: str
    description: str
    tasks: str
    examples: str
    related_codes: list[str]
    major: str
    submajor: str
    minor: str


class DeterministicLatticeSynthesizer:
    """Industrial-grade deterministic occupational lattice synthesizer."""

    def __init__(
        self, *, taxonomy=None, crosswalks=None, role_evidence=None, workflows=None
    ) -> None:
        self.taxonomy = dict(taxonomy or {})
        self.crosswalks = dict(crosswalks or {})
        self.role_evidence = dict(role_evidence or {})
        self.workflows = list(workflows or [])

    def get_skill_level(self, major: str, submajor: str) -> int:
        """Official ILO Skill Level (1 to 4)."""
        if major == "1":
            return 3 if submajor == "14" else 4
        if major == "2":
            return 4
        if major == "3":
            return 3
        if major in ("4", "5", "7", "8"):
            return 2
        if major == "6":
            return 1 if submajor == "63" else 2
        if major == "9":
            return 1
        return 2

    def build_crosswalk(self, code: str) -> dict[str, Any]:
        supplied = self.crosswalks.get(code, {})
        return {
            field: supplied.get(field)
            for field in ("kr_ncs", "kr_ksco", "us_onet", "cz_isco")
        }

    def build_deterministic_roles(self) -> dict[str, RoleNode]:
        roles = {}
        for code, item in self.taxonomy.items():
            evidence = self.role_evidence.get(code, {})
            cross = self.build_crosswalk(code)
            roles[code] = RoleNode(
                role_id=code,
                role_name=item.title_en,
                isco_08=code,
                kr_ncs=cross["kr_ncs"],
                kr_keco=cross["kr_ksco"],
                us_onet=cross["us_onet"],
                cz_isco=cross["cz_isco"],
                domain_id=SUBMAJOR_TO_DOMAIN_ID.get(item.submajor, "unknown"),
                career_level=evidence.get("career_level"),
                salary_band=evidence.get("salary_band", {}),
                hiring_demand=evidence.get("hiring_demand", "unknown"),
                skills=evidence.get("skills", []),
                value_chain_stage=evidence.get("value_chain_stage", "unknown"),
                headcount_share=evidence.get("headcount_share"),
                peer_staffing_index=evidence.get("peer_staffing_index"),
                wage_inflation_rate=evidence.get("wage_inflation_rate"),
                automation_exposure=evidence.get("automation_exposure"),
                rev_per_hc_leverage=evidence.get("rev_per_hc_leverage", "unknown"),
                workflow_role_type=evidence.get("workflow_role_type", "unknown"),
                workflow_pain_points=evidence.get("workflow_pain_points", []),
                evidence_status=evidence.get("evidence_status", "taxonomy_only"),
                source_refs=evidence.get("source_refs", []),
            )
        return roles

    def build_deterministic_career_edges(
        self, roles: dict[str, RoleNode]
    ) -> list[CareerEdge]:
        # A taxonomy's related-occupation list is not a company movement policy.
        return [
            CareerEdge(
                code,
                related,
                "taxonomy_related",
                difficulty_stars=None,
                salary_increment_pct=None,
                evidence_status="taxonomy",
                source_refs=["selected-taxonomy"],
            )
            for code, item in sorted(self.taxonomy.items())
            for related in sorted(set(item.related_codes))
            if code in roles and related in roles and code != related
        ]

    def build_deterministic_workflows(
        self, roles: dict[str, RoleNode]
    ) -> list[WorkflowConnection]:
        result = []
        for row in self.workflows:
            if (
                row.get("from_role_id") not in roles
                or row.get("to_role_id") not in roles
            ):
                raise ValueError("workflow references unknown role")
            if row.get("evidence_status") not in {
                "observed",
                "ai_proposed",
                "user_assumption",
            } or not row.get("source_refs"):
                raise ValueError("workflow evidence/authorship required")
            result.append(WorkflowConnection(**row))
        return result

    def build_deterministic_macro_graph(self) -> LatticeDomainGraph:
        """Build the full 436-role deterministic grand unified macro graph."""
        graph = LatticeDomainGraph(
            "grand_unified",
            "Deterministic Grand Unified Occupational Macro Lattice",
            evidence_status="taxonomy_projection",
        )
        roles = self.build_deterministic_roles()
        edges = self.build_deterministic_career_edges(roles)
        workflows = self.build_deterministic_workflows(roles)
        for r in roles.values():
            graph.add_role(r)
        for e in edges:
            graph.add_career_edge(e)
        for w in workflows:
            graph.add_workflow_connection(w)
        logger.info(
            "Synthesized deterministic lattice: %d roles, %d edges, %d workflows (coverage is limited to supplied taxonomy)",
            len(graph.roles),
            len(graph.career_edges),
            len(graph.workflow_connections),
        )
        return graph
