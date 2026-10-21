"""Career architecture, role responsibility and moves are separate axes."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import math
import re

ARCHITECTURES = frozenset({"single_ladder", "dual_ladder", "career_lattice"})
ROLE_TRACKS = frozenset(
    {
        "IC_specialist",
        "technical_leadership",
        "people_management",
        "project_product_program",
    }
)
RELATIONS = frozenset(
    {
        "promotion",
        "lateral",
        "diagonal",
        "rotation",
        "secondment",
        "project_assignment",
        "track_switch",
        "taxonomy_parent",
        "skill_similarity",
        "framework_mapping",
        "proposed",
    }
)
EDGE_EVIDENCE = frozenset(
    {
        "employer_policy",
        "observed_move",
        "external_framework",
        "taxonomy",
        "ai_proposed",
        "user_assumption",
    }
)


@dataclass(frozen=True)
class CareerGraph:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    architecture: str
    employer_id: str | None = None
    framework_ref: dict[str, Any] | None = None


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

    def __post_init__(self):
        if (
            type(self.amount) not in (int, float)
            or not math.isfinite(self.amount)
            or self.amount < 0
            or not isinstance(self.currency, str)
            or not re.fullmatch("[A-Z]{3}", self.currency)
        ):
            raise ValueError("Money requires finite amount and explicit currency")


@dataclass(frozen=True)
class PortfolioExperimentPlan:
    proposal_id: str
    target_task: str
    gap_refs: list[str]
    baseline: str
    evaluation: dict[str, Any]
    deliverables: list[str]
    differentiation: str
    author_kind: str = "ai_proposed"
    dataset_rights: str = "unknown"
    budget: Money | None = None
    limitations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VentureHypothesis:
    proposal_id: str
    buyer: str
    user: str
    payer: str
    problem: str
    substitutes: list[str]
    pilot: dict[str, Any]
    kill_criteria: list[str]
    author_kind: str = "ai_proposed"
    jurisdictions: list[str] = field(default_factory=list)
    budget: Money | None = None
