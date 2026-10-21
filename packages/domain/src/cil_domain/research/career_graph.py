"""Validate typed career relations and evidence-backed experiments."""

from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict
from typing import Any

from cil_contracts.career_proposals import (
    CareerGraph,
    ARCHITECTURES,
    ROLE_TRACKS,
    RELATIONS,
    EDGE_EVIDENCE,
    Money,
)
from cil_contracts.requests import timestamp


def validate_career_edges(
    graph: CareerGraph, *, as_of: str | None = None
) -> dict[str, Any]:
    if graph.architecture not in ARCHITECTURES:
        raise ValueError("unknown career architecture")
    nodes = deepcopy(graph.nodes)
    ids = [n.get("node_id") for n in nodes]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("career nodes require unique identities")
    for node in nodes:
        if node.get("role_track") not in ROLE_TRACKS:
            raise ValueError("unknown career role track")
    by_id = {n["node_id"]: n for n in nodes}
    edges = deepcopy(graph.edges)
    for edge in edges:
        if edge.get("from") not in by_id or edge.get("to") not in by_id:
            raise ValueError("career edge references an unknown node")
        if (
            edge.get("relation") not in RELATIONS
            or edge.get("evidence_kind") not in EDGE_EVIDENCE
        ):
            raise ValueError("career relation and evidence kind must be explicit")
        if edge["evidence_kind"] == "employer_policy":
            if (
                not edge.get("source_id")
                or not graph.employer_id
                or edge.get("employer_id") != graph.employer_id
            ):
                raise ValueError(
                    "official employer path requires matching employer and policy source"
                )
        if edge["evidence_kind"] in {
            "observed_move",
            "external_framework",
            "taxonomy",
        } and not edge.get("source_id"):
            raise ValueError("observed career relation requires its source")
        if edge["relation"] in {"promotion", "track_switch"} and edge[
            "evidence_kind"
        ] in {"external_framework", "taxonomy"}:
            raise ValueError("framework/taxonomy is not an employer promotion policy")
        if (
            as_of
            and edge["evidence_kind"] not in {"ai_proposed", "user_assumption"}
            and not edge.get("available_at")
        ):
            raise ValueError("career evidence availability time required")
        if (
            as_of
            and edge.get("available_at")
            and timestamp(edge["available_at"]) > timestamp(as_of)
        ):
            raise ValueError("career evidence is not available as_of")
        if edge["relation"] == "promotion":
            first, last = by_id[edge["from"]], by_id[edge["to"]]
            if first.get("grade_system") and first.get("grade_system") == last.get(
                "grade_system"
            ):
                if (
                    isinstance(first.get("grade_rank"), int)
                    and isinstance(last.get("grade_rank"), int)
                    and last["grade_rank"] <= first["grade_rank"]
                ):
                    raise ValueError(
                        "promotion must increase the declared employer grade rank"
                    )
    # Promotion edges must be acyclic. Lateral moves/rotations/return paths may cycle.
    promotion = {n: [] for n in ids}
    for edge in edges:
        if edge["relation"] == "promotion":
            promotion[edge["from"]].append(edge["to"])
    active, done = set(), set()

    def visit(node):
        if node in active:
            raise ValueError("cyclic promotion relation")
        if node in done:
            return
        active.add(node)
        for target in promotion[node]:
            visit(target)
        active.remove(node)
        done.add(node)

    for node in ids:
        visit(node)
    return {
        "architecture": graph.architecture,
        "employer_id": graph.employer_id,
        "nodes": nodes,
        "edges": edges,
        "limitations": [
            "A proposed route is not a promised promotion, timeline or salary progression."
        ],
    }


def validate_experiment_spec(proposal: dict[str, Any], kind: str) -> dict[str, Any]:
    if kind not in {"portfolio", "venture"}:
        raise ValueError("unknown experiment kind")
    required = (
        (
            "proposal_id",
            "target_task",
            "gap_refs",
            "baseline",
            "evaluation",
            "deliverables",
            "differentiation",
        )
        if kind == "portfolio"
        else (
            "proposal_id",
            "buyer",
            "user",
            "payer",
            "problem",
            "substitutes",
            "pilot",
            "kill_criteria",
        )
    )
    missing = [k for k in required if proposal.get(k) in (None, "", [], {})]
    if proposal.get("author_kind") not in {"ai_proposed", "user_assumption"}:
        missing.append("author_kind")
    if kind == "portfolio" and isinstance(proposal.get("evaluation"), dict):
        for name in ("metric", "test_data", "failure_criteria"):
            if not proposal["evaluation"].get(name):
                missing.append("evaluation." + name)
    budget = proposal.get("budget")
    if budget is not None:
        try:
            Money(**budget)
        except (TypeError, ValueError) as error:
            raise ValueError("invalid proposal budget Money") from error
    if kind == "venture" and isinstance(proposal.get("pilot"), dict):
        pilot = proposal["pilot"]
        for name in (
            "offer",
            "price",
            "success_criteria",
            "failure_criteria",
            "sample_definition",
        ):
            if pilot.get(name) in (None, "", [], {}):
                missing.append("pilot." + name)
        if "price" in pilot:
            try:
                Money(**pilot["price"])
            except (TypeError, ValueError) as error:
                raise ValueError("invalid pilot price Money") from error
    if budget is not None and (
        not isinstance(budget, dict)
        or type(budget.get("amount")) not in (float, int)
        or budget["amount"] < 0
        or not budget.get("currency")
    ):
        raise ValueError("budget requires a nonnegative amount and explicit currency")
    if (
        kind == "venture"
        and proposal.get("revenue_status") == "observed"
        and not proposal.get("payment_evidence_refs")
    ):
        raise ValueError("observed revenue requires payment evidence")
    return {
        "status": "NEEDS_INPUT" if missing else "PROPOSED",
        "proposal_kind": kind,
        "proposal": deepcopy(proposal),
        "missing": missing,
        "meaning": "Research/experiment proposal; not implementation, sales or hiring success.",
    }
