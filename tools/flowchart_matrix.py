#!/usr/bin/env python3
"""Validate semantic flowchart sources and deterministically derive Mermaid assets.

Evidence SSoT and the approved design review are editable inputs. Mermaid/SVG
are derived artifacts; this tool never chooses product semantics by itself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

STEP_TYPES = {"start", "process", "decision", "end"}
STATUSES = {"implemented", "validated", "planned", "investigate"}
DIAGRAM_KINDS = {"flowchart", "sequence", "state", "architecture"}


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, int] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} top-level JSON must be an object")
    return value


def ids(items: Any, label: str, result: Result) -> set[str]:
    if not isinstance(items, list):
        result.error(f"{label}s must be an array")
        return set()
    values = [item.get("id") for item in items if isinstance(item, dict)]
    for value, count in Counter(values).items():
        if not isinstance(value, str) or not value:
            result.error(f"{label} has a missing or non-string id")
        elif count > 1:
            result.error(f"duplicate {label} id: {value}")
    return {value for value in values if isinstance(value, str) and value}


def next_ids(step: dict[str, Any]) -> list[str]:
    direct = step.get("next_step_ids") or []
    branches = step.get("branches") or []
    branch_ids = [branch.get("next_step_id") for branch in branches if isinstance(branch, dict)]
    return [item for item in [*direct, *branch_ids] if isinstance(item, str) and item]


def reachable(seeds: set[str], edges: dict[str, set[str]]) -> set[str]:
    seen, todo = set(seeds), deque(seeds)
    while todo:
        for target in edges[todo.popleft()]:
            if target not in seen:
                seen.add(target)
                todo.append(target)
    return seen


def has_cycle(nodes: set[str], edges: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        visiting.add(node)
        for target in edges[node]:
            if target in visiting or (target not in visited and visit(target)):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(node not in visited and visit(node) for node in nodes)


def components(nodes: set[str], edges: dict[str, set[str]]) -> int:
    graph = {node: set() for node in nodes}
    for source, targets in edges.items():
        for target in targets:
            graph[source].add(target)
            graph[target].add(source)
    count, unseen = 0, set(nodes)
    while unseen:
        count += 1
        todo = [unseen.pop()]
        while todo:
            for node in graph[todo.pop()] & unseen:
                unseen.remove(node)
                todo.append(node)
    return count


def evidence_refs(data: dict[str, Any], step: dict[str, Any]) -> list[str]:
    return step.get("evidence_refs") or data.get("default_evidence_refs") or []


def validate_evidence(data: dict[str, Any]) -> Result:
    result = Result()
    document_ids = ids(data.get("documents"), "document", result)
    claim_ids = ids(data.get("claims"), "claim", result)
    decision_ids = ids(data.get("decision_ledger"), "decision", result)
    if not document_ids or not claim_ids or not decision_ids:
        result.error("evidence source requires documents, claims, and decision_ledger")
    for document in data.get("documents", []):
        locator = document.get("source_locator") if isinstance(document, dict) else None
        if not isinstance(locator, dict) or locator.get("kind") not in {"google_doc", "conversation_attachment", "local_file"}:
            result.error(f"document {document.get('id')} needs a supported source_locator")
    for claim in data.get("claims", []):
        refs = claim.get("evidence_refs", []) if isinstance(claim, dict) else []
        if not isinstance(refs, list) or not refs:
            result.error(f"claim {claim.get('id')} needs evidence_refs")
    for decision in data.get("decision_ledger", []):
        if not decision.get("final_rule"):
            result.error(f"decision {decision.get('id')} needs accepted_rule")
    result.metrics = {"document_count": len(document_ids), "claim_count": len(claim_ids), "decision_count": len(decision_ids)}
    return result


def validate_design(design: dict[str, Any], evidence: dict[str, Any]) -> Result:
    result = Result()
    review = design.get("semantic_review")
    if not isinstance(review, dict) or review.get("status") != "approved":
        result.error("flowchart design semantic_review.status must be approved")
    flows = design.get("flow_units")
    flow_ids = ids(flows, "flow unit", result)
    if not flow_ids:
        result.error("design must define at least one semantic flow unit")
    claims = {item["id"] for item in evidence.get("claims", []) if isinstance(item, dict) and item.get("id")}
    decisions = {item["id"] for item in evidence.get("decision_ledger", []) if isinstance(item, dict) and item.get("id")}
    rr = {item["id"] for item in design.get("rr_rows", []) if isinstance(item, dict) and item.get("id")}
    boundaries = {item["id"] for item in design.get("architecture_boundaries", []) if isinstance(item, dict) and item.get("id")}
    for flow in flows if isinstance(flows, list) else []:
        if not all(isinstance(flow.get(key), str) and flow[key] for key in ("id", "matrix_path", "start_contract", "end_contract")):
            result.error(f"flow {flow.get('id')} is missing its matrix path or boundary contracts")
        for key, known in (("required_claim_refs", claims), ("required_decision_refs", decisions), ("required_rr_ids", rr), ("required_boundary_ids", boundaries)):
            values = flow.get(key)
            if not isinstance(values, list) or not values:
                result.error(f"flow {flow.get('id')} needs non-empty {key}")
            elif unknown := set(values) - known:
                result.error(f"flow {flow.get('id')} references unknown {key}: {sorted(unknown)}")
    views = design.get("diagram_views")
    view_ids = ids(views, "diagram view", result)
    if not isinstance(views, list) or not views:
        result.error("design must define explicit diagram_views; type may not be inferred from flow steps")
    for view in views if isinstance(views, list) else []:
        view_id, kind, source = view.get("id"), view.get("kind"), view.get("source_flow_id")
        if kind not in DIAGRAM_KINDS:
            result.error(f"view {view_id} has unsupported kind {kind!r}")
        if source not in flow_ids:
            result.error(f"view {view_id} references unknown source_flow_id {source!r}")
        if kind == "flowchart" and view.get("orientation") not in {"TD", "LR", "BT", "RL"}:
            result.error(f"flowchart view {view_id} needs orientation TD/LR/BT/RL")
        if kind == "sequence":
            participant_ids = ids(view.get("participants"), f"sequence participant in {view_id}", result)
            if not isinstance(view.get("events"), list) or not view["events"]:
                result.error(f"sequence view {view_id} needs ordered events")
            if not participant_ids:
                result.error(f"sequence view {view_id} needs participants")
        if kind == "state":
            state_ids = ids(view.get("states"), f"state in {view_id}", result)
            transitions = view.get("transitions")
            if not state_ids or not isinstance(transitions, list) or not transitions:
                result.error(f"state view {view_id} needs states and transitions")
        if kind == "architecture":
            group_ids = ids(view.get("groups"), f"architecture group in {view_id}", result)
            service_ids = ids(view.get("services"), f"architecture service in {view_id}", result)
            edges = view.get("edges")
            if not group_ids or not service_ids or not isinstance(edges, list) or not edges:
                result.error(f"architecture view {view_id} needs groups, services, and edges")
            for service in view.get("services", []):
                if service.get("group") not in group_ids:
                    result.error(f"architecture service {service.get('id')} references unknown group")
            for edge in edges if isinstance(edges, list) else []:
                if edge.get("from") not in service_ids or edge.get("to") not in service_ids:
                    result.error(f"architecture view {view_id} edge references unknown service")
    result.metrics = {"flow_count": len(flow_ids), "rr_count": len(rr), "boundary_count": len(boundaries), "diagram_view_count": len(view_ids)}
    return result


def validate(data: dict[str, Any], design: dict[str, Any] | None = None) -> Result:
    result = Result()
    swim, logic = data.get("swimlane_matrix"), data.get("logic_matrix")
    if not isinstance(swim, dict) or not isinstance(logic, dict):
        result.error("matrix requires swimlane_matrix and logic_matrix objects")
        return result
    lanes, phases, steps = swim.get("lanes"), swim.get("phases"), logic.get("steps")
    lane_ids, phase_ids, step_ids = ids(lanes, "lane", result), ids(phases, "phase", result), ids(steps, "step", result)
    placed: Counter[str] = Counter()
    for phase in phases if isinstance(phases, list) else []:
        cells = phase.get("steps_by_lane")
        if not isinstance(cells, dict):
            result.error(f"phase {phase.get('id')} steps_by_lane must be an object")
            continue
        for lane, members in cells.items():
            if lane not in lane_ids:
                result.error(f"phase {phase.get('id')} references unknown lane {lane}")
            if not isinstance(members, list):
                result.error(f"phase {phase.get('id')} lane {lane} must be an array")
                continue
            for sid in members:
                if sid not in step_ids:
                    result.error(f"phase {phase.get('id')} references unknown step {sid}")
                else:
                    placed[sid] += 1
    edges = {sid: set() for sid in step_ids}
    for step in steps if isinstance(steps, list) else []:
        sid = step.get("id")
        if step.get("phase_id") not in phase_ids or step.get("lane_id") not in lane_ids:
            result.error(f"step {sid} must reference an existing phase and lane")
        if step.get("type") not in STEP_TYPES:
            result.error(f"step {sid} has invalid type {step.get('type')!r}")
        if placed[sid] != 1:
            result.error(f"step {sid} must be placed exactly once in phases")
        status = step.get("implementation_status")
        if status not in STATUSES:
            result.error(f"step {sid} implementation_status must be one of {sorted(STATUSES)}")
        refs = evidence_refs(data, step)
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref.strip() for ref in refs):
            result.error(f"step {sid} needs evidence_refs or matrix default_evidence_refs")
        target = step.get("code_target")
        if target is not None:
            if not isinstance(target, dict) or target.get("state") not in {"planned", "implemented"}:
                result.error(f"step {sid} code_target must have state planned or implemented")
            elif target["state"] == "planned" and target.get("href"):
                result.error(f"step {sid} planned code_target may not contain href")
        if step.get("type") == "decision":
            branches = step.get("branches")
            if not isinstance(step.get("condition"), str) or not step["condition"].strip() or not isinstance(branches, list) or len(branches) < 2:
                result.error(f"decision {sid} needs a condition and two branches")
            elif len({branch.get("result") for branch in branches if isinstance(branch, dict)}) != len(branches):
                result.error(f"decision {sid} has duplicate branch labels")
        if step.get("type") == "end" and next_ids(step):
            result.error(f"end step {sid} cannot have next steps")
        for target_id in next_ids(step):
            if target_id not in step_ids:
                result.error(f"step {sid} references unknown next step {target_id}")
            else:
                edges[sid].add(target_id)
    starts = {step["id"] for step in steps if step.get("type") == "start" and step.get("id") in step_ids}
    ends = {step["id"] for step in steps if step.get("type") == "end" and step.get("id") in step_ids}
    if not starts or not ends:
        result.error("matrix requires start and end steps")
    if starts and (unseen := step_ids - reachable(starts, edges)):
        result.error(f"steps unreachable from start: {sorted(unseen)}")
    reverse = {sid: set() for sid in step_ids}
    for source, targets in edges.items():
        for target in targets:
            reverse[target].add(source)
    if ends and (dead := step_ids - reachable(ends, reverse)):
        result.error(f"steps without an end path: {sorted(dead)}")
    if has_cycle(step_ids, edges):
        result.error("directed cycle detected; loop policy is not approved")
    if design is not None:
        review = data.get("semantic_review")
        flow_id = review.get("flow_id") if isinstance(review, dict) else None
        unit = next((item for item in design.get("flow_units", []) if item.get("id") == flow_id), None)
        if not isinstance(review, dict) or review.get("status") != "approved" or unit is None:
            result.error("matrix needs approved semantic_review matching a design flow unit")
        else:
            for matrix_key, design_key in (("claim_refs", "required_claim_refs"), ("decision_refs", "required_decision_refs"), ("rr_ids", "required_rr_ids"), ("boundary_ids", "required_boundary_ids")):
                if set(review.get(matrix_key, [])) != set(unit.get(design_key, [])):
                    result.error(f"matrix {flow_id} {matrix_key} must exactly cover approved design")
    edge_count = sum(map(len, edges.values()))
    count = components(step_ids, edges) if step_ids else 0
    result.metrics = {"lane_count": len(lane_ids), "phase_count": len(phase_ids), "step_count": len(step_ids), "edge_count": edge_count, "decision_count": sum(step.get("type") == "decision" for step in steps), "component_count": count, "cyclomatic_complexity": edge_count - len(step_ids) + 2 * count}
    return result


def quote(text: Any) -> str:
    return str(text or "").replace("\\", "\\\\").replace('"', "\\\"").replace("\n", "<br/>")


def node(step: dict[str, Any], lane_names: dict[str, str]) -> str:
    label = quote(f"{step['id']} · {lane_names[step['lane_id']]}\n{step.get('output') or step.get('condition') or step.get('input') or ''}")
    if step["type"] in {"start", "end"}:
        return f'{step["id"]}(["{label}"])'
    if step["type"] == "decision":
        return f'{step["id"]}{{"{label}"}}'
    return f'{step["id"]}["{label}"]'


def compile_mermaid(data: dict[str, Any]) -> str:
    swim, logic = data["swimlane_matrix"], data["logic_matrix"]
    lane_names = {lane["id"]: lane.get("name", lane["id"]) for lane in swim["lanes"]}
    by_phase: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for step in logic["steps"]:
        by_phase[step["phase_id"]].append(step)
    lines = ["%% GENERATED FROM approved flowchart design; DO NOT EDIT", "flowchart TD", "  classDef implemented fill:#DCFCE7,stroke:#15803D,color:#14532D", "  classDef validated fill:#DBEAFE,stroke:#1D4ED8,color:#1E3A8A", "  classDef planned fill:#FEF3C7,stroke:#B45309,color:#78350F,stroke-dasharray: 5 3", "  classDef investigate fill:#FEE2E2,stroke:#B91C1C,color:#7F1D1D,stroke-dasharray: 5 3"]
    for phase in swim["phases"]:
        pid = phase["id"]
        lines.append(f'  subgraph phase_{pid}["{quote(phase.get("name", pid))}"]')
        for step in by_phase[pid]:
            lines.append(f"    {node(step, lane_names)}")
        lines.append("  end")
    for step in logic["steps"]:
        labels = {branch.get("next_step_id"): branch.get("result") for branch in step.get("branches") or [] if isinstance(branch, dict)}
        for target in next_ids(step):
            label = labels.get(target)
            lines.append(f"  {step['id']} -->{('| ' + quote(label) + ' |') if label else ''} {target}")
        lines.append(f"  class {step['id']} {step['implementation_status']}")
    return "\n".join(lines) + "\n"


def mermaid_text(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "<br/>")


def compile_sequence(view: dict[str, Any]) -> str:
    lines = ["%% GENERATED FROM approved diagram view; DO NOT EDIT", "sequenceDiagram"]
    type_map = {"actor": "actor", "boundary": "participant", "control": "participant", "database": "participant"}
    for participant in view["participants"]:
        prefix = type_map.get(participant.get("type"), "participant")
        lines.append(f"  {prefix} {participant['id']} as {mermaid_text(participant.get('label', participant['id']))}")

    def emit(events: list[dict[str, Any]], indent: str = "  ") -> None:
        for event in events:
            kind = event.get("kind")
            if kind == "message":
                lines.append(f"{indent}{event['from']}{event.get('arrow', '->>')}{event['to']}: {mermaid_text(event['label'])}")
            elif kind == "note":
                lines.append(f"{indent}Note over {event['over']}: {mermaid_text(event['label'])}")
            elif kind == "loop":
                lines.append(f"{indent}loop {mermaid_text(event['label'])}")
                emit(event.get("events", []), indent + "  ")
                lines.append(f"{indent}end")
            elif kind == "alt":
                lines.append(f"{indent}alt {mermaid_text(event['label'])}")
                emit(event.get("then", []), indent + "  ")
                lines.append(f"{indent}else {mermaid_text(event.get('else_label', 'otherwise'))}")
                emit(event.get("else", []), indent + "  ")
                lines.append(f"{indent}end")
            else:
                raise ValueError(f"unsupported sequence event kind: {kind!r}")
    emit(view["events"])
    return "\n".join(lines) + "\n"


def compile_state(view: dict[str, Any]) -> str:
    lines = ["%% GENERATED FROM approved diagram view; DO NOT EDIT", "stateDiagram-v2"]
    for state in view["states"]:
        lines.append(f"  state \"{mermaid_text(state['label'])}\" as {state['id']}")
    for transition in view["transitions"]:
        lines.append(f"  {transition['from']} --> {transition['to']}: {mermaid_text(transition.get('label', ''))}")
    return "\n".join(lines) + "\n"


def compile_architecture(view: dict[str, Any]) -> str:
    lines = ["%% GENERATED FROM approved diagram view; DO NOT EDIT", "architecture-beta"]
    for group in view["groups"]:
        lines.append(f"  group {group['id']}({group.get('icon', 'cloud')})[\"{mermaid_text(group['label'])}\"]")
    for service in view["services"]:
        lines.append(f"  service {service['id']}({service.get('icon', 'server')})[\"{mermaid_text(service['label'])}\"] in {service['group']}")
    parent = {service["id"]: service["group"] for service in view["services"]}
    for edge in view["edges"]:
        direction = edge.get("direction", "-->")
        crosses_group = parent[edge["from"]] != parent[edge["to"]]
        source_group = "{group}" if crosses_group else ""
        target_group = "{group}" if crosses_group else ""
        source = f"{edge['from']}{source_group}:{edge.get('from_side', 'R')}"
        target = f"{edge.get('to_side', 'L')}:{edge['to']}{target_group}"
        lines.append(f"  {source} {direction} {target}")
    return "\n".join(lines) + "\n"


def compile_view(view: dict[str, Any], matrix: dict[str, Any]) -> str:
    kind = view["kind"]
    if kind == "flowchart":
        rendered = compile_mermaid(matrix)
        return rendered.replace("flowchart TD", f"flowchart {view['orientation']}", 1)
    if kind == "sequence":
        return compile_sequence(view)
    if kind == "state":
        return compile_state(view)
    if kind == "architecture":
        return compile_architecture(view)
    raise ValueError(f"unsupported diagram kind {kind!r}")

def review_packet(evidence: dict[str, Any], design: dict[str, Any]) -> str:
    unresolved = [item for item in evidence.get("decision_ledger", []) if item.get("status") != "accepted"]
    lines = ["# Flowchart semantic review packet", "", "## Source status", f"- Claims: {len(evidence.get('claims', []))}", f"- Decisions: {len(evidence.get('decision_ledger', []))}", f"- Review: {design.get('semantic_review', {}).get('status', 'missing')}", "", "## Flow contracts", "", "| Flow | Start contract | End contract | Claims | Decisions |", "| --- | --- | --- | ---: | ---: |"]
    for unit in design.get("flow_units", []):
        lines.append(f"| {unit['id']} | {unit['start_contract']} | {unit['end_contract']} | {len(unit['required_claim_refs'])} | {len(unit['required_decision_refs'])} |")
    lines += ["", "## Post-chart DeepWiki handoff", "", "Only after the user accepts the chart semantics, validate actual GraphRAG/FastAPI/Tauri/LanceDB integration contracts with deepwiki-logic-integration.", "", "## Unresolved decisions", ""]
    lines += [f"- {item.get('id')}: {item.get('final_rule', 'missing rule')}" for item in unresolved] or ["- None."]
    return "\n".join(lines) + "\n"


def write(path: Path, content: str, check: bool) -> bool:
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def show(result: Result) -> int:
    print(json.dumps({"valid": result.valid, "errors": result.errors, "warnings": result.warnings, "metrics": result.metrics}, ensure_ascii=False, indent=2))
    return 0 if result.valid else 1


def render_artifact(mmdc: Path, mmd: Path, output: Path, mermaid_config: Path | None, puppeteer_config: Path | None) -> None:
    command = [str(mmdc), "-i", str(mmd), "-o", str(output), "-b", "transparent"]
    if mermaid_config:
        command.extend(["-c", str(mermaid_config)])
    if puppeteer_config:
        command.extend(["-p", str(puppeteer_config)])
    subprocess.run(command, check=True)


def render_or_check(mmdc: Path, mmd: Path, output: Path, signature: bytes, mermaid_config: Path | None, puppeteer_config: Path | None, check: bool) -> None:
    if not check:
        render_artifact(mmdc, mmd, output, mermaid_config, puppeteer_config)
    else:
        with tempfile.TemporaryDirectory(dir=output.parent) as directory:
            candidate = Path(directory) / output.name
            render_artifact(mmdc, mmd, candidate, mermaid_config, puppeteer_config)
            if not output.is_file() or output.read_bytes() != candidate.read_bytes():
                raise ValueError(f"stale rendered artifact: {output}")
    if not output.read_bytes().lstrip().startswith(signature):
        raise ValueError(f"invalid rendered artifact: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate-evidence"); p.add_argument("source", type=Path)
    p = sub.add_parser("validate-design"); p.add_argument("design", type=Path); p.add_argument("--evidence", type=Path, required=True)
    p = sub.add_parser("validate"); p.add_argument("matrix", type=Path); p.add_argument("--design", type=Path); p.add_argument("--evidence", type=Path)
    p = sub.add_parser("compile-mermaid"); p.add_argument("matrix", type=Path); p.add_argument("--output", type=Path, required=True); p.add_argument("--check", action="store_true")
    p = sub.add_parser("review-packet"); p.add_argument("--evidence", type=Path, required=True); p.add_argument("--design", type=Path, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--check", action="store_true")
    p = sub.add_parser("build"); p.add_argument("--evidence", type=Path, required=True); p.add_argument("--design", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--review-packet", type=Path, required=True); p.add_argument("--mmdc", type=Path, required=True); p.add_argument("--mermaid-config", type=Path); p.add_argument("--puppeteer-config", type=Path); p.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate-evidence":
            return show(validate_evidence(load(args.source)))
        if args.command == "validate-design":
            return show(validate_design(load(args.design), load(args.evidence)))
        if args.command == "validate":
            design = load(args.design) if args.design else None
            return show(validate(load(args.matrix), design))
        if args.command == "compile-mermaid":
            content = compile_mermaid(load(args.matrix))
            if not write(args.output, content, args.check):
                print(f"error: stale Mermaid artifact: {args.output}", file=sys.stderr); return 1
            return 0
        evidence, design = load(args.evidence), load(args.design)
        if not validate_evidence(evidence).valid or not validate_design(design, evidence).valid:
            print("error: evidence/design are not approved", file=sys.stderr); return 1
        if args.command == "review-packet":
            content = review_packet(evidence, design)
            if not write(args.output, content, args.check):
                print(f"error: stale review packet: {args.output}", file=sys.stderr); return 1
            return 0
        packet = review_packet(evidence, design)
        packet_path = args.review_packet
        if not write(packet_path, packet, args.check):
            print(f"error: stale review packet: {packet_path}", file=sys.stderr); return 1
        units = {unit["id"]: unit for unit in design["flow_units"]}
        for view in design["diagram_views"]:
            unit = units[view["source_flow_id"]]
            matrix_path = args.design.parent / unit["matrix_path"].removeprefix("docs/")
            matrix = load(matrix_path)
            result = validate(matrix, design)
            if not result.valid:
                print(json.dumps({"flow": unit["id"], "errors": result.errors}, ensure_ascii=False), file=sys.stderr); return 1
            mmd = args.output_dir / f"{view['id']}.mmd"
            svg = args.output_dir / f"{view['id']}.svg"
            png = args.output_dir / f"{view['id']}.png"
            content = compile_view(view, matrix)
            if not write(mmd, content, args.check):
                print(f"error: stale Mermaid artifact: {mmd}", file=sys.stderr); return 1
            render_or_check(args.mmdc, mmd, svg, b"<svg", args.mermaid_config, args.puppeteer_config, args.check)
            render_or_check(args.mmdc, mmd, png, b"\x89PNG\r\n\x1a\n", args.mermaid_config, args.puppeteer_config, args.check)
            svg_text = svg.read_text(encoding="utf-8")
            if 'aria-roledescription="error"' in svg_text:
                raise ValueError(f"Mermaid rendered an error SVG: {svg}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
