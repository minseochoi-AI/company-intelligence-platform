"""Canonical responsibility owner; migrated from src/company_intel/excel_lattice_export.py."""

from __future__ import annotations
from cil_domain.taxonomy.lattice import DeterministicLatticeSynthesizer
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import Any
import logging
import openpyxl

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

SUBMAJOR_DOMAIN_DETAILED: dict[str, str] = {
    "11": "경영/비즈니스 (Business & Strategy)",
    "12": "경영/비즈니스 (Business & Strategy)",
    "13": "제조/생산/운영 (Operations & Production)",
    "14": "서비스/환대 (Hospitality & Retail)",
    "21": "이공계/엔지니어링 (Engineering & Technology)",
    "22": "바이오/의료 (Bio, Pharma & Healthcare)",
    "23": "교육/연구 (Education & Research)",
    "24": "금융/비즈니스 (Finance, Strategy & HR)",
    "25": "정보통신/데이터 (ICT, Software & AI)",
    "26": "법률/문화/디자인 (Legal, Media & Design)",
    "31": "이공계/기술공 (Science & Engineering Technicians)",
    "32": "의료/보건기술 (Health Associate Professionals)",
    "33": "금융/사무행정 (Business & Admin Associates)",
    "34": "법률/문화기술 (Legal, Social & Cultural Associates)",
    "35": "정보통신기술 (ICT Technicians & Operations)",
}

DOMAIN_LABEL_MAP: dict[str, str] = {
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


def load_raw_isco_unit_groups(rows=None) -> list[dict[str, str]]:
    """Project explicitly supplied taxonomy rows; no sibling-repository fallback."""
    if rows is None:
        raise ValueError("explicit taxonomy input required")
    return [
        {
            "isco_code": row.code,
            "title_en": row.title_en,
            "description": row.description,
        }
        for row in rows
    ]


def build_occupational_lattice_workbook(
    output_path="company-intelligence-occupational-lattice-master.xlsx", *, graph=None
) -> Path:
    """Render supplied graph with missing measurements explicitly null."""
    from cil_reporting.research_workbook import render_research_workbook
    from dataclasses import asdict

    if graph is None or not graph.roles:
        raise ValueError("explicit nonempty taxonomy graph required")
    tables = {
        "00_Navigator": [
            {
                "_row_id": "scope",
                "domain_id": graph.domain_id,
                "domain_name": graph.domain_name,
                "roles": len(graph.roles),
                "meaning": "Coverage is limited to supplied evidence. Taxonomy relatedness is not employer promotion policy.",
            }
        ],
        "01_Master_Taxonomy": [
            {"_row_id": key, **asdict(role)}
            for key, role in sorted(graph.roles.items())
        ],
        "02_Career_Lattice_DAG": [
            {"_row_id": str(i), **asdict(edge)}
            for i, edge in enumerate(graph.career_edges)
        ],
        "03_Consultant_ValueChain": [
            {
                "_row_id": key,
                "value_chain_stage": r.value_chain_stage,
                "headcount_share": r.headcount_share,
                "peer_staffing_index": r.peer_staffing_index,
                "source_refs": r.source_refs,
            }
            for key, r in sorted(graph.roles.items())
        ],
        "04_Market_Dynamics_ROI": [
            {
                "_row_id": key,
                "salary_band": r.salary_band,
                "automation_exposure": r.automation_exposure,
                "wage_inflation_rate": r.wage_inflation_rate,
                "evidence_status": r.evidence_status,
                "source_refs": r.source_refs,
            }
            for key, r in sorted(graph.roles.items())
        ],
        "05_Venture_B2BSaaS": [
            {"_row_id": str(i), **asdict(edge)}
            for i, edge in enumerate(graph.workflow_connections)
        ],
        "06_Data_Dictionary": [
            {
                "_row_id": "missing",
                "null": "not observed",
                "taxonomy_related": "related occupations, not promotion",
                "source_refs": "selected source identifiers",
            }
        ],
        "07_Time_Series_Warehouse": [],
        "08_Temporal_Comparative_Table": [],
        "09_Cross_Elasticity_Trends": [],
    }
    build = render_research_workbook(tables)
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.read_bytes() != build.data:
        raise FileExistsError("existing workbook differs; choose a new output path")
    output.write_bytes(build.data)
    return output
