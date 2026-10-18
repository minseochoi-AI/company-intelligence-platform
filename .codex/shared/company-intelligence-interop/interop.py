#!/usr/bin/env python3
"""Validate shared artifacts and build a neutral career/venture comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

VERSION = "1.0.0"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
KINDS = {"career", "venture"}
AXES = ("time_hours_per_week", "budget_krw", "location", "risk_tolerance", "available_resources")


class ContractError(ValueError):
    pass


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be non-empty text")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be an array")
    return value


def _exact_keys(value: dict[str, Any], required: set[str], optional: set[str], label: str) -> None:
    missing = sorted(required - value.keys())
    extra = sorted(value.keys() - required - optional)
    if missing or extra:
        raise ContractError(f"{label} keys invalid; missing={missing}, extra={extra}")


def _version(value: dict[str, Any]) -> None:
    if value.get("schema_version") != VERSION:
        raise ContractError(f"schema_version must be {VERSION}")


def _timestamp(value: Any, label: str) -> None:
    text = _text(value, label)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ContractError(f"{label} must be an ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{label} must include a timezone")


def _string_list(value: Any, label: str) -> list[str]:
    rows = _list(value, label)
    if any(not isinstance(item, str) or not item.strip() for item in rows):
        raise ContractError(f"{label} entries must be non-empty text")
    if len(rows) != len(set(rows)):
        raise ContractError(f"{label} entries must be unique")
    return rows


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_target(reference_path: Path, relative: str) -> Path:
    raw = PurePosixPath(_text(relative, "path"))
    if raw.is_absolute() or ".." in raw.parts:
        raise ContractError("reference path must be relative and may not traverse parents")
    target = (reference_path.parent / Path(*raw.parts)).resolve()
    base = reference_path.parent.resolve()
    if target != base and base not in target.parents:
        raise ContractError("reference target escapes its artifact directory")
    if not target.is_file():
        raise ContractError(f"referenced artifact is missing: {target}")
    return target


def load(path: Path) -> dict[str, Any]:
    try:
        return _object(json.loads(path.read_text(encoding="utf-8")), str(path))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc


def validate_domain_plan(value: dict[str, Any]) -> None:
    _version(value)
    required = {"schema_version", "plan_kind", "plan_id", "revision", "generated_at", "subject", "constraints", "objectives", "actions", "evidence_bundle_refs", "unresolved"}
    _exact_keys(value, required, {"campaign_link"}, "DomainPlan")
    if value["plan_kind"] not in KINDS:
        raise ContractError("plan_kind must be career or venture")
    _text(value["plan_id"], "plan_id")
    if not isinstance(value["revision"], int) or value["revision"] < 1:
        raise ContractError("revision must be a positive integer")
    _timestamp(value["generated_at"], "generated_at")
    _text(value["subject"], "subject")
    constraints = _object(value["constraints"], "constraints")
    for key in AXES:
        if key not in constraints:
            raise ContractError(f"constraints.{key} is required")
    _string_list(constraints["available_resources"], "constraints.available_resources")
    objectives = _string_list(value["objectives"], "objectives")
    if not objectives:
        raise ContractError("objectives needs non-empty text entries")
    for index, action in enumerate(_list(value["actions"], "actions")):
        item = _object(action, f"actions[{index}]")
        _exact_keys(item, {"action_id", "description", "status", "evidence_refs"}, set(), f"actions[{index}]")
        _text(item["action_id"], f"actions[{index}].action_id")
        _text(item["description"], f"actions[{index}].description")
        if item["status"] not in {"proposed", "ready", "blocked", "complete"}:
            raise ContractError(f"actions[{index}].status is invalid")
        _string_list(item["evidence_refs"], f"actions[{index}].evidence_refs")
    _string_list(value["evidence_bundle_refs"], "evidence_bundle_refs")
    _string_list(value["unresolved"], "unresolved")


def validate_domain_plan_ref(value: dict[str, Any]) -> None:
    _version(value)
    required = {"schema_version", "plan_kind", "plan_id", "revision", "path", "sha256", "generated_at", "evidence_bundle_refs"}
    _exact_keys(value, required, {"campaign_link"}, "DomainPlanRef")
    if value["plan_kind"] not in KINDS:
        raise ContractError("plan_kind must be career or venture")
    _text(value["plan_id"], "plan_id")
    if not isinstance(value["revision"], int) or value["revision"] < 1:
        raise ContractError("revision must be a positive integer")
    if not SHA256.fullmatch(str(value["sha256"])):
        raise ContractError("sha256 must use sha256:<64 lowercase hex>")
    _timestamp(value["generated_at"], "generated_at")
    _string_list(value["evidence_bundle_refs"], "evidence_bundle_refs")


def validate_evidence_bundle(value: dict[str, Any]) -> None:
    _version(value)
    required = {"schema_version", "bundle_id", "generated_at", "producer", "subject", "sources", "claims", "redaction_status"}
    _exact_keys(value, required, set(), "EvidenceBundle")
    for key in ("bundle_id", "generated_at", "producer", "subject"):
        _timestamp(value[key], key) if key == "generated_at" else _text(value[key], key)
    sources = _list(value["sources"], "sources")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        item = _object(source, f"sources[{index}]")
        _exact_keys(item, {"source_id", "locator", "observed_at", "content_hash", "rights_status"}, set(), f"sources[{index}]")
        source_id = _text(item["source_id"], f"sources[{index}].source_id")
        if source_id in source_ids:
            raise ContractError(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)
        if not SHA256.fullmatch(str(item["content_hash"])):
            raise ContractError(f"sources[{index}].content_hash is invalid")
        if item["rights_status"] not in {"verified-reusable", "restricted", "unknown"}:
            raise ContractError(f"sources[{index}].rights_status is invalid")
    for index, claim in enumerate(_list(value["claims"], "claims")):
        item = _object(claim, f"claims[{index}]")
        refs = _list(item.get("source_ids"), f"claims[{index}].source_ids")
        if not refs or any(ref not in source_ids for ref in refs):
            raise ContractError(f"claims[{index}] must cite known source_ids")
        if item.get("status") not in {"observed", "inferred", "conflicted", "unknown"}:
            raise ContractError(f"claims[{index}].status is invalid")
    if value["redaction_status"] not in {"none", "redacted", "review-required"}:
        raise ContractError("redaction_status is invalid")


def validate_evidence_bundle_ref(value: dict[str, Any]) -> None:
    _version(value)
    _exact_keys(value, {"schema_version", "bundle_id", "path", "sha256", "generated_at"}, set(), "EvidenceBundleRef")
    _text(value["bundle_id"], "bundle_id")
    if not SHA256.fullmatch(str(value["sha256"])):
        raise ContractError("sha256 must use sha256:<64 lowercase hex>")
    _timestamp(value["generated_at"], "generated_at")


def validate_dual_path_comparison(value: dict[str, Any]) -> None:
    _version(value)
    required = {"schema_version", "comparison_id", "generated_at", "career_plan_ref", "venture_plan_ref", "status", "axes", "unresolved_axes", "decision"}
    _exact_keys(value, required, set(), "DualPathComparison")
    if value["status"] not in {"comparable", "partial", "blocked"}:
        raise ContractError("comparison status is invalid")
    if value["decision"] != "human-required":
        raise ContractError("comparison may not choose a path automatically")
    _timestamp(value["generated_at"], "generated_at")
    for name in ("career_plan_ref", "venture_plan_ref"):
        ref = _object(value[name], name)
        _exact_keys(ref, {"path", "sha256"}, set(), name)
        _text(ref["path"], f"{name}.path")
        if not SHA256.fullmatch(str(ref["sha256"])):
            raise ContractError(f"{name}.sha256 is invalid")
    statuses = {"comparable", "missing-career", "missing-venture", "missing-both"}
    rows = _list(value["axes"], "axes")
    seen: dict[str, str] = {}
    for index, row in enumerate(rows):
        item = _object(row, f"axes[{index}]")
        _exact_keys(item, {"axis", "career_value", "venture_value", "status"}, set(), f"axes[{index}]")
        axis = _text(item["axis"], f"axes[{index}].axis")
        if axis not in AXES or axis in seen or item["status"] not in statuses:
            raise ContractError(f"axes[{index}] has an invalid or duplicate axis/status")
        expected = "missing-both" if item["career_value"] is None and item["venture_value"] is None else "missing-career" if item["career_value"] is None else "missing-venture" if item["venture_value"] is None else "comparable"
        if item["status"] != expected:
            raise ContractError(f"axes[{index}].status contradicts its values")
        seen[axis] = expected
    if set(seen) != set(AXES):
        raise ContractError("axes must contain every comparison axis exactly once")
    unresolved = _string_list(value["unresolved_axes"], "unresolved_axes")
    expected_unresolved = sorted(axis for axis, status in seen.items() if status != "comparable")
    if sorted(unresolved) != expected_unresolved:
        raise ContractError("unresolved_axes does not match axis statuses")
    expected_status = "comparable" if not unresolved else "blocked" if len(unresolved) == len(AXES) else "partial"
    if value["status"] != expected_status:
        raise ContractError("comparison status does not match its axes")


def verify_dual_path_comparison_refs(value: dict[str, Any], artifact_path: Path) -> None:
    validate_dual_path_comparison(value)
    for name in ("career_plan_ref", "venture_plan_ref"):
        ref = value[name]
        target = _relative_target(artifact_path, ref["path"])
        if digest(target) != ref["sha256"]:
            raise ContractError(f"{name}.sha256 does not match its ref file")


def validate_campaign_link(value: dict[str, Any]) -> None:
    _version(value)
    _exact_keys(value, {"schema_version", "campaign_id", "relationship", "path", "sha256"}, set(), "CampaignLink")
    if value["relationship"] not in {"evidence-input", "decision-input", "implementation-output"}:
        raise ContractError("relationship is invalid")
    if not SHA256.fullmatch(str(value["sha256"])):
        raise ContractError("sha256 is invalid")


VALIDATORS: dict[str, Callable[[dict[str, Any]], None]] = {
    "domain-plan": validate_domain_plan,
    "domain-plan-ref": validate_domain_plan_ref,
    "evidence-bundle": validate_evidence_bundle,
    "evidence-bundle-ref": validate_evidence_bundle_ref,
    "dual-path-comparison": validate_dual_path_comparison,
    "campaign-link": validate_campaign_link,
}


def verify_domain_plan_ref(path: Path, expected_kind: str | None = None) -> dict[str, Any]:
    ref = load(path)
    validate_domain_plan_ref(ref)
    if expected_kind and ref["plan_kind"] != expected_kind:
        raise ContractError(f"expected {expected_kind} plan, found {ref['plan_kind']}")
    target = _relative_target(path, ref["path"])
    if digest(target) != ref["sha256"]:
        raise ContractError("DomainPlanRef sha256 does not match target")
    plan = load(target)
    validate_domain_plan(plan)
    for key in ("plan_kind", "plan_id", "revision"):
        if plan[key] != ref[key]:
            raise ContractError(f"DomainPlanRef {key} does not match target")
    return plan


def verify_evidence_bundle_ref(path: Path) -> dict[str, Any]:
    ref = load(path)
    validate_evidence_bundle_ref(ref)
    target = _relative_target(path, ref["path"])
    if digest(target) != ref["sha256"]:
        raise ContractError("EvidenceBundleRef sha256 does not match target")
    bundle = load(target)
    validate_evidence_bundle(bundle)
    if bundle["bundle_id"] != ref["bundle_id"]:
        raise ContractError("EvidenceBundleRef bundle_id does not match target")
    return bundle


def compare(career_ref: Path, venture_ref: Path, output_base: Path | None = None) -> dict[str, Any]:
    career = verify_domain_plan_ref(career_ref, "career")
    venture = verify_domain_plan_ref(venture_ref, "venture")
    rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for axis in AXES:
        left, right = career["constraints"].get(axis), venture["constraints"].get(axis)
        status = "missing-both" if left is None and right is None else "missing-career" if left is None else "missing-venture" if right is None else "comparable"
        if status != "comparable":
            unresolved.append(axis)
        rows.append({"axis": axis, "career_value": left, "venture_value": right, "status": status})
    comparable = len(rows) - len(unresolved)
    status = "comparable" if not unresolved else "blocked" if not comparable else "partial"
    base = (output_base or Path(os.path.commonpath([career_ref.resolve().parent, venture_ref.resolve().parent]))).resolve()
    career_locator = Path(os.path.relpath(career_ref.resolve(), base)).as_posix()
    venture_locator = Path(os.path.relpath(venture_ref.resolve(), base)).as_posix()
    for locator in (career_locator, venture_locator):
        if PurePosixPath(locator).is_absolute() or ".." in PurePosixPath(locator).parts:
            raise ContractError("comparison output must contain both input refs without parent traversal")
    career_digest, venture_digest = digest(career_ref), digest(venture_ref)
    basis = f"{career_digest}:{venture_digest}"
    return {"schema_version": VERSION, "comparison_id": "dual-" + hashlib.sha256(basis.encode()).hexdigest()[:16], "generated_at": datetime.now(UTC).isoformat(), "career_plan_ref": {"path": career_locator, "sha256": career_digest}, "venture_plan_ref": {"path": venture_locator, "sha256": venture_digest}, "status": status, "axes": rows, "unresolved_axes": unresolved, "decision": "human-required"}


def _plan(kind: str, plan_id: str) -> dict[str, Any]:
    return {"schema_version": VERSION, "plan_kind": kind, "plan_id": plan_id, "revision": 1, "generated_at": "2026-09-15T00:00:00+00:00", "subject": "self-test", "constraints": {"time_hours_per_week": 20, "budget_krw": 1000, "location": "KR", "risk_tolerance": "medium", "available_resources": ["server"]}, "objectives": ["verify"], "actions": [], "evidence_bundle_refs": [], "unresolved": []}


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        refs: list[Path] = []
        for kind in ("career", "venture"):
            plan = root / f"{kind}.json"
            plan.write_text(json.dumps(_plan(kind, kind + "-1")) + "\n", encoding="utf-8")
            ref = root / f"{kind}-ref.json"
            ref.write_text(json.dumps({"schema_version": VERSION, "plan_kind": kind, "plan_id": kind + "-1", "revision": 1, "path": plan.name, "sha256": digest(plan), "generated_at": "2026-09-15T00:00:00+00:00", "evidence_bundle_refs": []}) + "\n", encoding="utf-8")
            refs.append(ref)
        result = compare(refs[0], refs[1])
        validate_dual_path_comparison(result)
        if result["decision"] != "human-required" or result["status"] != "comparable":
            raise ContractError("self-test comparison invariant failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("kind", choices=sorted(VALIDATORS))
    validate_parser.add_argument("path", type=Path)
    verify_parser = sub.add_parser("verify-ref")
    verify_parser.add_argument("kind", choices=("domain-plan", "evidence-bundle"))
    verify_parser.add_argument("path", type=Path)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--career-ref", type=Path, required=True)
    compare_parser.add_argument("--venture-ref", type=Path, required=True)
    compare_parser.add_argument("--output", type=Path, required=True)
    sub.add_parser("self-test")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            value = load(args.path)
            VALIDATORS[args.kind](value)
            if args.kind == "dual-path-comparison":
                verify_dual_path_comparison_refs(value, args.path)
        elif args.command == "verify-ref":
            (verify_domain_plan_ref if args.kind == "domain-plan" else verify_evidence_bundle_ref)(args.path)
        elif args.command == "compare":
            result = compare(args.career_ref, args.venture_ref, args.output.parent)
            verify_dual_path_comparison_refs(result, args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            self_test()
        print(json.dumps({"status": "valid", "command": args.command}, ensure_ascii=False))
        return 0
    except ContractError as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
