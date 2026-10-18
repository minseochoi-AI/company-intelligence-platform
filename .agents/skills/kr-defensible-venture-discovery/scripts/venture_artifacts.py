#!/usr/bin/env python3
"""Validate venture research artifacts and report decision-critical gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
MODES = {"CONFIGURE", "BASELINE", "GAP", "AUGMENT", "RECLASSIFY", "DECIDE"}
ARCHETYPES = {"competitive", "niche", "unverified-white-space"}
CONSTRAINTS = {
    "time_hours_per_week", "budget_krw", "location", "risk_tolerance",
    "available_resources", "field_access", "hardware_tolerance",
    "regulatory_tolerance", "sales_horizon_months",
    "desired_barriers", "runway_months", "hardware_prototype_budget_krw",
    "certifications", "forbidden_paths",
}


class ArtifactError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArtifactError("artifact must be an object")
    return value


def _text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ArtifactError(f"{field} must be non-empty text")


def _array(value: Any, field: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ArtifactError(f"{field} must be {'a non-empty ' if nonempty else 'an '}array")
    return value


def _base(value: dict[str, Any]) -> None:
    if value.get("schema_version") != VERSION:
        raise ArtifactError(f"schema_version must be {VERSION}")
    if not isinstance(value.get("revision"), int) or value["revision"] < 1:
        raise ArtifactError("revision must be a positive integer")


def session_gaps(value: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    constraints = value.get("founder_constraints")
    if not isinstance(constraints, dict):
        return ["founder_constraints"]
    for field in sorted(CONSTRAINTS):
        if field not in constraints or constraints[field] is None or constraints[field] == "":
            gaps.append(f"founder_constraints.{field}")
    if not constraints.get("available_resources"):
        gaps.append("founder_constraints.available_resources")
    if not constraints.get("desired_barriers"):
        gaps.append("founder_constraints.desired_barriers")
    if not value.get("target_sectors"):
        gaps.append("target_sectors")
    return sorted(set(gaps))


def validate_session(value: dict[str, Any]) -> None:
    _base(value)
    required = {"schema_version", "session_id", "revision", "mode", "generated_at", "founder_constraints", "target_sectors", "non_goals", "hypothesis_refs", "evidence_bundle_refs", "research_gaps"}
    missing, extra = required - value.keys(), value.keys() - required
    if missing or extra:
        raise ArtifactError(f"VentureSession keys invalid; missing={sorted(missing)}, extra={sorted(extra)}")
    _text(value["session_id"], "session_id")
    _text(value["generated_at"], "generated_at")
    if value["mode"] not in MODES:
        raise ArtifactError("mode is invalid")
    constraints = value["founder_constraints"]
    if not isinstance(constraints, dict) or not CONSTRAINTS.issubset(constraints):
        raise ArtifactError("founder_constraints is incomplete")
    _array(value["target_sectors"], "target_sectors", nonempty=True)
    for field in ("non_goals", "hypothesis_refs", "evidence_bundle_refs", "research_gaps"):
        _array(value[field], field)
    for field in ("available_resources", "desired_barriers", "certifications", "forbidden_paths"):
        _array(constraints[field], f"founder_constraints.{field}")
    allowed_barriers = {"physical", "algorithmic", "workflow", "data", "distribution"}
    if any(item not in allowed_barriers for item in constraints["desired_barriers"]):
        raise ArtifactError("founder_constraints.desired_barriers contains an invalid barrier")
    calculated, reported = set(session_gaps(value)), set(value["research_gaps"])
    if calculated != reported:
        raise ArtifactError(
            "research_gaps must equal calculated gaps; "
            f"missing={sorted(calculated - reported)}, extra={sorted(reported - calculated)}"
        )
    if value["mode"] != "CONFIGURE" and session_gaps(value):
        raise ArtifactError("non-CONFIGURE session has unresolved founder constraints")


def opportunity_gaps(value: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    for field in ("problem", "buyer", "user", "payer", "solution"):
        if not value.get(field):
            gaps.append(field)
    sizing = value.get("market_sizing")
    if not isinstance(sizing, dict):
        gaps.append("market_sizing")
    else:
        for field in ("tam", "sam", "som", "unit", "formula", "assumptions"):
            if field not in sizing or sizing[field] in (None, "", []):
                gaps.append(f"market_sizing.{field}")
    if not value.get("evidence_refs"):
        gaps.append("evidence_refs")
    if not value.get("experiments"):
        gaps.append("experiments")
    if not value.get("kill_criteria"):
        gaps.append("kill_criteria")
    rights_rows = value.get("data_rights", [])
    for index, item in enumerate(rights_rows if isinstance(rights_rows, list) else []):
        if isinstance(item, dict) and item.get("product_use") in {None, "", "unknown"}:
            gaps.append(f"data_rights[{index}].product_use")
    return sorted(set(gaps))


def validate_opportunity(value: dict[str, Any]) -> None:
    _base(value)
    required = {"schema_version", "hypothesis_id", "revision", "sector", "problem", "buyer", "user", "payer", "solution", "market_archetype", "market_sizing", "competitors", "substitutes", "barriers", "data_rights", "evidence_refs", "unresolved", "experiments", "kill_criteria"}
    missing, extra = required - value.keys(), value.keys() - required
    if missing or extra:
        raise ArtifactError(f"OpportunityHypothesis keys invalid; missing={sorted(missing)}, extra={sorted(extra)}")
    for field in ("hypothesis_id", "sector", "problem", "buyer", "user", "payer", "solution"):
        _text(value[field], field)
    archetype = value["market_archetype"]
    if archetype not in ARCHETYPES:
        raise ArtifactError("market_archetype must be competitive, niche, or unverified-white-space")
    competitors = _array(value["competitors"], "competitors")
    substitutes = _array(value["substitutes"], "substitutes")
    for field in ("barriers", "data_rights", "evidence_refs", "unresolved", "experiments"):
        _array(value[field], field)
    _array(value["kill_criteria"], "kill_criteria", nonempty=True)
    sizing = value["market_sizing"]
    if not isinstance(sizing, dict) or not {"tam", "sam", "som", "unit", "formula", "assumptions"}.issubset(sizing):
        raise ArtifactError("market_sizing is incomplete")
    if archetype in {"competitive", "niche"} and not competitors:
        raise ArtifactError(f"{archetype} requires at least one named competitor")
    if archetype == "unverified-white-space" and not substitutes:
        raise ArtifactError("unverified-white-space requires substitutes or workarounds")
    if archetype == "unverified-white-space" and not value["evidence_refs"]:
        raise ArtifactError("unverified-white-space requires competitor-search evidence")
    for index, competitor in enumerate(competitors):
        if not isinstance(competitor, dict):
            raise ArtifactError(f"competitors[{index}] must be an object")
        _text(competitor.get("name"), f"competitors[{index}].name")
        _array(competitor.get("evidence_refs"), f"competitors[{index}].evidence_refs", nonempty=True)
    allowed_barriers = {"physical", "algorithmic", "workflow", "data", "distribution"}
    for index, barrier in enumerate(value["barriers"]):
        if not isinstance(barrier, dict) or barrier.get("kind") not in allowed_barriers:
            raise ArtifactError(f"barriers[{index}].kind is invalid")
        for field in ("claim", "acquisition_path", "cost_time", "verification", "copyability_risk"):
            _text(barrier.get(field), f"barriers[{index}].{field}")
    for index, rights in enumerate(value["data_rights"]):
        if not isinstance(rights, dict):
            raise ArtifactError(f"data_rights[{index}] must be an object")
        for field in ("source_ref", "acquisition", "analysis", "product_use", "personal_data", "refresh_cost"):
            _text(rights.get(field), f"data_rights[{index}].{field}")


def _sample() -> dict[str, Any]:
    return {
        "schema_version": VERSION, "hypothesis_id": "h-1", "revision": 1, "sector": "agriculture",
        "problem": "manual inspection", "buyer": "cooperative", "user": "operator", "payer": "cooperative",
        "solution": "retrofit inspection aid", "market_archetype": "unverified-white-space",
        "market_sizing": {"tam": 100, "sam": 30, "som": 3, "unit": "accounts", "formula": "accounts", "assumptions": ["pilot"]},
        "competitors": [], "substitutes": ["manual inspection"], "barriers": [], "data_rights": [],
        "evidence_refs": ["search-1"], "unresolved": [], "experiments": ["five interviews"], "kill_criteria": ["no paid pilot intent"],
    }


def self_test() -> None:
    validate_opportunity(_sample())
    invalid = _sample()
    invalid["market_archetype"] = "niche"
    try:
        validate_opportunity(invalid)
    except ArtifactError:
        return
    raise ArtifactError("self-test expected niche-without-competitor rejection")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate-session", "validate-opportunity", "gaps"):
        child = sub.add_parser(command)
        child.add_argument("path", type=Path)
        if command == "gaps":
            child.add_argument("--kind", choices=("session", "opportunity"), required=True)
    sub.add_parser("self-test")
    args = parser.parse_args(argv)
    try:
        if args.command == "self-test":
            self_test()
            result: dict[str, Any] = {"status": "valid"}
        else:
            value = load(args.path)
            if args.command == "validate-session":
                validate_session(value)
                result = {"status": "valid", "kind": "session"}
            elif args.command == "validate-opportunity":
                validate_opportunity(value)
                result = {"status": "valid", "kind": "opportunity"}
            else:
                gaps = session_gaps(value) if args.kind == "session" else opportunity_gaps(value)
                result = {"status": "complete" if not gaps else "gaps", "gaps": gaps}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ArtifactError as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
