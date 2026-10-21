"""Research orchestration with injected storage and workbook projection.

The fact path never imports a model client or performs provider refreshes. AI
proposal inputs and narrative reports retain independent namespaces and hashes.
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict
from typing import Any, Callable, Protocol
import hashlib
import json

from cil_contracts.requests import (
    ReportRequest,
    canonical_bytes,
    content_hash,
    timestamp,
)
from cil_contracts.career_proposals import CareerGraph
from cil_contracts.sealed_research_bundle import WorkbookBuild
from cil_application.research.request_compiler import compile_request, CapabilityPort
from cil_domain.research.metrics import (
    competition_ratio,
    stage_pass_rate,
    eligibility_verdict,
    comparable_financials,
    wage_conversion,
    task_exposure,
)
from cil_domain.research.career_graph import (
    validate_career_edges,
    validate_experiment_spec,
)

DATASETS = (
    "Run",
    "Sources",
    "RawFields",
    "Postings",
    "Requirements",
    "Competition",
    "FinancialHistory",
    "WageBenchmarks",
    "TaskExposure",
    "CareerEvidence",
    "OpportunityEvidence",
    "Scenarios",
    "ProposedPaths",
    "PortfolioPlans",
    "VentureHypotheses",
    "GapsConflicts",
    "Lineage",
)
PROPOSAL_TABLES = {"Scenarios", "ProposedPaths", "PortfolioPlans", "VentureHypotheses"}
PROPOSAL_INPUTS = {
    "scenarios",
    "proposed_paths",
    "portfolio_plans",
    "venture_hypotheses",
}


class ArtifactStore(Protocol):
    def write(self, relative: str, data: bytes) -> None: ...
    def read(self, relative: str) -> bytes: ...
    def exists(self, relative: str) -> bool: ...


def run_identity(request: ReportRequest, snapshot: dict[str, Any]) -> str:
    return (
        "run-"
        + content_hash(
            [request.request_hash, content_hash(snapshot), "research-engine-v1"]
        )[:24]
    )


def _raw_fields(value: Any, pointer: str = ""):
    if isinstance(value, dict) and value:
        for key in sorted(value):
            item = value[key]
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from _raw_fields(item, pointer + "/" + escaped)
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from _raw_fields(item, pointer + "/" + str(index))
    else:
        yield {
            "raw_pointer": pointer or "/",
            "value": value,
            "value_type": type(value).__name__,
        }


def _profile(snapshot: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    ref = value.get("profile_ref")
    if ref is None:
        return {}
    if isinstance(ref, str):
        return snapshot.get("profiles", {}).get(ref, {})
    if isinstance(ref, dict) and isinstance(ref.get("profile_id"), str):
        return snapshot.get("profiles", {}).get(ref["profile_id"], {})
    raise ValueError("profile_ref must identify a profile in the selected snapshot")


def _selected(
    row: dict[str, Any], options: dict[str, Any], mapping: dict[str, str]
) -> bool:
    for key, field in mapping.items():
        if key in options:
            expected = options[key]
            if (
                (row.get(field) not in expected)
                if isinstance(expected, list)
                else (row.get(field) != expected)
            ):
                return False
    return True


def _proposal_selected(row: dict[str, Any], spec: dict[str, Any]) -> bool:
    if not _selected(
        row,
        spec,
        {
            "proposal_ids": "proposal_id",
            "task_ids": "target_task",
            "dataset_rights": "dataset_rights",
        },
    ):
        return False
    if spec.get("jurisdictions") and not set(row.get("jurisdictions", [])) & set(
        spec["jurisdictions"]
    ):
        return False
    maximum = spec.get("max_budget")
    if maximum:
        if (
            not isinstance(maximum, dict)
            or set(maximum) != {"amount", "currency"}
            or type(maximum["amount"]) not in (int, float)
            or maximum["amount"] < 0
        ):
            raise ValueError("max_budget requires amount and currency")
        budget = row.get("budget", {})
        if (
            budget.get("currency") != maximum["currency"]
            or type(budget.get("amount")) not in (int, float)
            or budget["amount"] > maximum["amount"]
        ):
            return False
    return True


def _available_records(snapshot, collection, as_of, gaps):
    sources = {
        source.get("source_id"): source for source in snapshot.get("sources", [])
    }
    for original in snapshot.get(collection, []):
        record = deepcopy(original)
        available = record.get("available_at") or sources.get(
            record.get("source_id"), {}
        ).get("available_at")
        try:
            if not available:
                reason = "evidence_availability_unknown"
            elif timestamp(available) > timestamp(as_of):
                reason = "not_available_as_of"
            else:
                record["available_at"] = available
                yield record
                continue
        except ValueError:
            reason = "invalid_evidence_availability"
        gaps.append(
            {
                "field": collection,
                "source_id": record.get("source_id"),
                "reason": reason,
            }
        )


def run_research(
    request: ReportRequest,
    snapshot: dict[str, Any],
    registry: CapabilityPort,
    store: ArtifactStore,
    *,
    renderer: Callable[[dict[str, list[dict[str, Any]]]], WorkbookBuild],
) -> dict[str, Any]:
    compiled = compile_request(request, snapshot, registry)
    if compiled["status"] in {"NEEDS_INPUT", "NEEDS_EVIDENCE"}:
        return compiled
    value = request.as_dict()
    metrics = {m["metric_id"] for m in value.get("metric_specs", [])}

    def wants(metric):
        return not metrics or metric in metrics

    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in DATASETS}
    run_id = run_identity(request, snapshot)
    source_kind = compiled["source_kind"]
    tables["Run"].append(
        {
            "run_id": run_id,
            "question": request.question,
            "as_of": request.as_of,
            "request_hash": request.request_hash,
            "snapshot_hash": compiled["snapshot_hash"],
            "selected_skills": compiled["selected_skills"],
            "source_kind": source_kind,
            "layout_version": "research-xlsx-v1",
            "method_version": "1.0.0",
        }
    )
    tables["Sources"] = deepcopy(snapshot.get("sources", []))
    tables["Sources"].append(
        {
            "source_id": "saved-bundle",
            "snapshot_hash": compiled["snapshot_hash"],
            "source_kind": source_kind,
            "rights": "user_supplied_local_analysis",
            "coverage": snapshot.get("coverage", "not_declared"),
            "limitations": "Source metadata is a declaration, not proof of live API acceptance or real-world accuracy.",
        }
    )
    raw_facts = {
        key: deepcopy(item)
        for key, item in snapshot.items()
        if key not in PROPOSAL_INPUTS
    }
    if isinstance(raw_facts.get("career_graph"), dict):
        for component in ("nodes", "edges"):
            raw_facts["career_graph"][component] = [
                row
                for row in raw_facts["career_graph"].get(component, [])
                if row.get("evidence_kind", row.get("author_kind"))
                not in {"ai_proposed", "user_assumption"}
            ]
    tables["RawFields"] = list(_raw_fields(raw_facts))
    tables["Postings"] = deepcopy(compiled["selected_postings"])
    tables["GapsConflicts"] = deepcopy(compiled["gaps"])
    profile = _profile(snapshot, value)
    ids = {p["posting_id"] for p in compiled["selected_postings"]}
    entities = {
        p.get("entity_id") for p in compiled["selected_postings"] if p.get("entity_id")
    }
    roles = {
        p.get("role_id") for p in compiled["selected_postings"] if p.get("role_id")
    }
    mapping = snapshot.get("role_mappings", {}).get(value.get("role_mapping_ref"), [])
    if mapping:
        if not isinstance(mapping, list):
            raise ValueError(
                "role mapping must contain explicit versioned crosswalk rows"
            )
        for row in mapping:
            if (
                not row.get("source_id")
                or not row.get("version")
                or not row.get("from_role_id")
                or not row.get("to_role_id")
            ):
                raise ValueError(
                    "role mapping requires source, version and both role identifiers"
                )
        roles |= {r["to_role_id"] for r in mapping if r["from_role_id"] in roles}
    entities.update(value.get("financial_spec", {}).get("entity_ids", []))
    if value.get("financial_spec", {}).get("entity_id"):
        entities.add(value["financial_spec"]["entity_id"])
    for posting in compiled["selected_postings"]:
        for requirement in posting.get("requirements", []):
            if not wants("eligibility"):
                break
            policy = value.get("requirement_policy", {})
            if requirement.get("necessity") not in {
                "required",
                "preferred",
                "disqualifier",
            }:
                tables["GapsConflicts"].append(
                    {
                        "field": "requirements",
                        "posting_id": posting["posting_id"],
                        "reason": "requirement_necessity_unclassified",
                    }
                )
            if requirement.get("necessity") not in policy.get(
                "kinds", ["required", "preferred", "disqualifier"]
            ):
                continue
            assessment = eligibility_verdict(requirement, profile, as_of=request.as_of)
            if assessment.get("verdict") in {"unknown", "conflict"}:
                tables["GapsConflicts"].append(
                    {
                        "field": "requirements",
                        "requirement_id": requirement.get("requirement_id"),
                        "reason": assessment["reason"],
                    }
                )
            if (
                not policy.get("include_unknown", True)
                and assessment.get("verdict") == "unknown"
            ):
                continue
            tables["Requirements"].append(
                {
                    **deepcopy(requirement),
                    **assessment,
                    "posting_id": posting["posting_id"],
                }
            )
        competitions = [
            r
            for r in snapshot.get("competition", [])
            if r.get("posting_id") == posting["posting_id"]
        ]
        if (
            not competitions
            and "selected-posting" in request.purpose
            and (wants("competition_ratio") or wants("stage_pass_rate"))
        ):
            tables["Competition"].append(
                {
                    "posting_id": posting["posting_id"],
                    "value": None,
                    "kind": "unknown",
                    "reason": "official_recruitment_counts_unavailable",
                    "unit": "applicants_per_opening",
                }
            )
        for row in competitions:
            if not wants(
                "stage_pass_rate"
                if row.get("numerator_kind") == "passed"
                else "competition_ratio"
            ):
                continue
            expected = {
                "round_id": posting.get("vacancy_batch_id"),
                "role_id": posting.get("role_id"),
                "location_id": posting.get("location_id"),
                "stage": row.get("stage"),
                "cutoff": row.get("cutoff"),
                **value.get("competition_spec", {}),
            }
            if not row.get("available_at"):
                result = {
                    "value": None,
                    "kind": "unknown",
                    "reason": "competition_availability_unknown",
                }
            elif timestamp(row["available_at"]) > timestamp(request.as_of):
                result = {
                    "value": None,
                    "reason": "not_available_as_of",
                    "kind": "unknown",
                }
            else:
                result = (
                    stage_pass_rate(row, expected)
                    if row.get("numerator_kind") == "passed"
                    else competition_ratio(row, expected)
                )
            tables["Competition"].append({**deepcopy(row), **result})
    if "financial" in request.purpose:
        history = value.get("history", {})
        financial_rows = [
            r
            for r in snapshot.get("financials", [])
            if _selected(
                r,
                value.get("comparability", {}),
                {k: k for k in value.get("comparability", {})},
            )
            and (
                not value.get("financial_spec", {}).get("concepts")
                or r.get("concept") in value["financial_spec"]["concepts"]
            )
            and (
                not history.get("period_start")
                or r.get("period_start", "") >= history["period_start"]
            )
            and (
                not history.get("period_end")
                or r.get("period_end", "9999") <= history["period_end"]
            )
        ]
        for entity in sorted(entities):
            financial = comparable_financials(
                financial_rows,
                entity_id=entity,
                as_of=request.as_of,
                revision_mode=value.get("history", {}).get(
                    "revision_mode", "known_at_time"
                ),
            )
            tables["FinancialHistory"].extend(
                {**r, "record_kind": "source_fact"} for r in financial["rows"]
            )
            if wants("financial_growth"):
                tables["FinancialHistory"].extend(
                    {**r, "record_kind": "comparison"} for r in financial["comparisons"]
                )
            tables["GapsConflicts"].extend(
                {"field": "financials", **r} for r in financial["excluded"]
            )
        if not entities or not tables["FinancialHistory"]:
            tables["GapsConflicts"].append(
                {"field": "financials", "reason": "comparable_company_facts_missing"}
            )
    if "work-future" in request.purpose:
        for wage in _available_records(
            snapshot, "wages", request.as_of, tables["GapsConflicts"]
        ):
            if (
                not wants("wage_conversion")
                or not roles
                or wage.get("role_id") not in roles
            ):
                continue
            if not _selected(
                wage,
                value.get("wage_comparison", {}),
                {k: k for k in ("country", "currency", "basis", "period")},
            ):
                continue
            if not wage.get("available_at") or timestamp(
                wage["available_at"]
            ) > timestamp(request.as_of):
                tables["GapsConflicts"].append(
                    {"field": "wages", "reason": "wage_availability_unconfirmed"}
                )
                continue
            tables["WageBenchmarks"].append(
                {
                    **deepcopy(wage),
                    **wage_conversion(
                        wage, value.get("wage_comparison", {}).get("assumptions")
                    ),
                }
            )
        tasks = [
            r
            for r in _available_records(
                snapshot, "tasks", request.as_of, tables["GapsConflicts"]
            )
            if roles and r.get("role_id") in roles
        ]
        weights = snapshot.get("task_weight_sets", {}).get(
            value.get("task_weights_ref"), {}
        )
        if weights:
            if (
                not isinstance(weights.get("weights"), dict)
                or not weights.get("author_kind")
                or not weights.get("version")
            ):
                raise ValueError("task weights require weights, version and authorship")
            tasks = [
                {
                    **r,
                    "weight": weights["weights"].get(r.get("task_id")),
                    "weight_origin": weights["author_kind"],
                }
                for r in tasks
            ]
        method = value.get("exposure_method", {})
        if isinstance(method, str):
            method = snapshot.get("exposure_methods", {}).get(method, {})
        result = task_exposure(
            tasks, method, total_weight=weights.get("total_weight", 1.0)
        )
        if wants("task_exposure"):
            tables["TaskExposure"].append(result)
        if not roles:
            tables["GapsConflicts"].append(
                {
                    "field": "role_mapping_ref",
                    "reason": "posting_role_mapping_unconfirmed",
                }
            )
    if "path" in request.purpose:
        graph = snapshot.get("career_graph")
        if graph:
            try:
                career = validate_career_edges(
                    CareerGraph(**graph), as_of=request.as_of
                )
                spec = value.get("career_spec", {})
                if not _selected(
                    career,
                    spec,
                    {"architecture": "architecture", "employer_id": "employer_id"},
                ):
                    raise ValueError(
                        "career structure/employer does not match requested scope"
                    )
                node_ids = {
                    n["node_id"]
                    for n in career["nodes"]
                    if not spec.get("role_tracks")
                    or n.get("role_track") in spec["role_tracks"]
                }
                for node in career["nodes"]:
                    if node["node_id"] in node_ids:
                        tables["CareerEvidence"].append({"record_kind": "node", **node})
                for edge in career["edges"]:
                    if (
                        spec.get("relations")
                        and edge.get("relation") not in spec["relations"]
                    ):
                        continue
                    target = (
                        "ProposedPaths"
                        if edge["evidence_kind"] in {"ai_proposed", "user_assumption"}
                        else "CareerEvidence"
                    )
                    tables[target].append({"record_kind": "edge", **edge})
            except (TypeError, ValueError) as error:
                tables["GapsConflicts"].append(
                    {"field": "career_graph", "reason": str(error)}
                )
        else:
            tables["GapsConflicts"].append(
                {
                    "field": "career_graph",
                    "reason": "employer_path_or_proposal_not_supplied",
                }
            )
    if set(request.purpose) & {"portfolio", "venture"}:
        for opportunity in _available_records(
            snapshot, "opportunities", request.as_of, tables["GapsConflicts"]
        ):
            specs = [
                value.get(p + "_spec", {})
                for p in ("portfolio", "venture")
                if p in request.purpose
            ]
            if specs and not any(
                not s.get("opportunity_ids")
                or opportunity.get("opportunity_id") in s["opportunity_ids"]
                for s in specs
            ):
                continue
            row = deepcopy(opportunity)
            row["payment_evidence_status"] = (
                "payment_observed"
                if row.get("payment_evidence_refs")
                else "not_observed"
            )
            row["demand_interpretation"] = (
                "public_problem_evidence"
                if row.get("source_type") == "oss_issue"
                else "source_declared_opportunity"
            )
            tables["OpportunityEvidence"].append(row)
    for purpose, source_key, table in [
        ("portfolio", "portfolio_plans", "PortfolioPlans"),
        ("venture", "venture_hypotheses", "VentureHypotheses"),
    ]:
        if purpose in request.purpose:
            for proposal in snapshot.get(source_key, []):
                if not _proposal_selected(proposal, value.get(purpose + "_spec", {})):
                    continue
                validated = validate_experiment_spec(proposal, purpose)
                if validated["status"] == "NEEDS_INPUT":
                    tables["GapsConflicts"].append(
                        {
                            "field": source_key,
                            "proposal_id": proposal.get("proposal_id"),
                            "reason": "proposal_contract_incomplete",
                            "missing": validated["missing"],
                        }
                    )
                tables[table].append(
                    {
                        **validated["proposal"],
                        "validation_status": validated["status"],
                        "missing": validated["missing"],
                    }
                )
            if not tables[table]:
                tables["GapsConflicts"].append(
                    {"field": source_key, "reason": "proposal_not_authored"}
                )
    for proposal in snapshot.get("proposed_paths", []):
        if proposal.get("author_kind") not in {"ai_proposed", "user_assumption"}:
            raise ValueError("proposed paths require explicit authorship")
        if "path" in request.purpose:
            tables["ProposedPaths"].append(deepcopy(proposal))
    scenarios = (
        snapshot.get("scenario_sets", {}).get(value["scenario_ref"], [])
        if value.get("scenario_ref")
        else snapshot.get("scenarios", [])
    )
    for scenario in scenarios:
        if scenario.get("author_kind") not in {"ai_proposed", "user_assumption"}:
            raise ValueError("scenarios require explicit assumption authorship")
        item = deepcopy(scenario)
        item["calculation_status"] = "not_calculated"
        if scenario.get("method_id") == "compound_growth/v1":
            base = next(
                (
                    r
                    for r in tables["FinancialHistory"]
                    if r.get("source_id") == scenario.get("base_source_id")
                    and r.get("record_kind") == "source_fact"
                ),
                None,
            )
            rate, years = scenario.get("growth_rate"), scenario.get("years")
            if (
                base
                and type(base.get("value")) in (int, float)
                and type(rate) in (int, float)
                and rate >= -1
                and type(years) is int
                and 0 <= years <= 50
            ):
                item["computed_value"] = base["value"] * (1 + rate) ** years
                item["unit"] = base["unit"]
                item["calculation_status"] = "computed_from_explicit_assumptions"
        tables["Scenarios"].append(item)
    for table, rows in list(tables.items()):
        if table == "Lineage":
            continue
        for index, row in enumerate(rows):
            row["_row_id"] = table + "-" + content_hash([index, row])[:20]
            row.setdefault("source_kind", source_kind)
            tables["Lineage"].append(
                {
                    "table_id": table,
                    "row_id": row["_row_id"],
                    "source_refs": row.get(
                        "source_refs", [row.get("source_id", "saved-bundle")]
                    ),
                    "raw_pointer": row.get("raw_pointer"),
                    "method_version": row.get("method_version"),
                    "namespace": "proposals" if table in PROPOSAL_TABLES else "facts",
                }
            )
    for index, row in enumerate(tables["Lineage"]):
        row["_row_id"] = "Lineage-" + content_hash([index, row])[:20]
    metric_tables = {
        "competition_ratio": "Competition",
        "stage_pass_rate": "Competition",
        "eligibility": "Requirements",
        "financial_growth": "FinancialHistory",
        "wage_conversion": "WageBenchmarks",
        "task_exposure": "TaskExposure",
    }
    for metric in value.get("metric_specs", []):
        table = metric_tables[metric["metric_id"]]
        if not tables[table]:
            tables["GapsConflicts"].append(
                {
                    "_row_id": "metric-gap-" + metric["metric_id"],
                    "field": metric["metric_id"],
                    "reason": "requested_metric_has_no_evidence",
                    "source_kind": source_kind,
                }
            )
    limit = value.get("execution_limits", {}).get("max_rows")
    if limit is not None and sum(len(rows) for rows in tables.values()) > limit:
        raise ValueError("research row limit exceeded; raw data has not been truncated")
    spec = value.get("report_spec", {})
    if set(spec.get("datasets", DATASETS)) - set(DATASETS) or set(
        spec.get("columns", {})
    ) - set(DATASETS):
        raise ValueError("unknown report dataset")
    projection = {
        k: deepcopy(v) for k, v in tables.items() if k in spec.get("datasets", DATASETS)
    }
    for table, columns in spec.get("columns", {}).items():
        if any(c not in {key for row in tables[table] for key in row} for c in columns):
            raise ValueError("unknown report column: " + table)
        if table in projection:
            projection[table] = [
                {k: v for k, v in row.items() if k in columns or k == "_row_id"}
                for row in tables[table]
            ]
    workbook = renderer(projection)
    status = (
        "PARTIAL"
        if tables["GapsConflicts"]
        or any(
            r.get("kind") == "unknown"
            for r in tables["Competition"] + tables["TaskExposure"]
        )
        else "SEALED"
    )
    safe_columns = {
        "_row_id",
        "source_kind",
        "source_id",
        "source_refs",
        "kind",
        "unit",
        "value",
        "reason",
        "method_version",
        "record_kind",
        "posting_id",
        "entity_id",
        "role_id",
        "title",
        "concept",
        "scope",
        "currency",
        "frequency",
        "period_basis",
        "period_start",
        "period_end",
        "available_at",
        "base_value",
        "current_value",
        "growth",
        "verdict",
        "requirement_id",
        "requirement_kind",
        "evidence_refs",
        "coverage",
        "covered_task_score",
        "unmapped_weight",
        "bounds",
        "method_id",
        "study_version",
        "table_id",
        "row_id",
        "column_id",
        "namespace",
        "field",
        "status",
        "architecture",
        "node_id",
        "role_track",
        "relation",
        "from_node",
        "to_node",
        "evidence_kind",
        "author_kind",
        "proposal_id",
        "target_task",
        "gap_refs",
        "baseline",
        "dataset_rights",
        "validation_status",
        "missing",
        "buyer",
        "user",
        "payer",
        "problem",
        "substitutes",
        "kill_criteria",
        "jurisdictions",
        "opportunity_id",
        "source_type",
        "payment_evidence_status",
        "demand_interpretation",
        "calculation_status",
        "computed_value",
    }
    safe_columns |= {
        "necessity",
        "profile_evidence_status",
        "provisional",
        "revision_mode",
        "knowledge_cutoff",
        "basis",
        "source_period",
        "source_value",
        "assumption_kind",
        "conversion",
        "limitations",
        "scope",
        "numerator",
        "denominator",
        "numerator_kind",
        "denominator_kind",
        "from",
        "to",
        "employer_id",
        "grade_system",
        "grade_rank",
        "budget",
        "evaluation",
        "deliverables",
        "differentiation",
        "pilot",
    }
    ai_tables = {
        name: [{k: v for k, v in r.items() if k in safe_columns} for r in rows]
        for name, rows in tables.items()
        if name not in {"RawFields", "Sources", "Run"}
    }
    ai_tables["ReportContext"] = [
        {
            "question": request.question,
            "as_of": request.as_of,
            "locale": spec.get("locale", "ko"),
            "audience": spec.get("audience", "user"),
            "source_kind": source_kind,
        }
    ]
    documents = {
        "inputs/request.json": canonical_bytes(value),
        "inputs/raw.json": canonical_bytes(snapshot),
        "facts/raw.json": canonical_bytes(raw_facts),
        "facts/tables.json": canonical_bytes(
            {k: v for k, v in tables.items() if k not in PROPOSAL_TABLES}
        ),
        "proposals/input-authorship.json": canonical_bytes(
            {key: snapshot[key] for key in PROPOSAL_INPUTS if key in snapshot}
        ),
        "proposals/tables.json": canonical_bytes(
            {k: v for k, v in tables.items() if k in PROPOSAL_TABLES}
        ),
        "tables.json": canonical_bytes(tables),
        "cell-refs.json": canonical_bytes(list(workbook.cell_refs)),
        "overflows.json": canonical_bytes(workbook.overflows),
        "ai-input.json": canonical_bytes(ai_tables),
        "research.xlsx": workbook.data,
    }
    manifest = {
        "contract_version": "sealed-research-bundle-v2",
        "run_id": run_id,
        "status": status,
        "as_of": request.as_of,
        "request_hash": request.request_hash,
        "snapshot_hash": compiled["snapshot_hash"],
        "source_kind": source_kind,
        "layout_version": "research-xlsx-v1",
        "method_version": "1.0.0",
        "selected_skills": compiled["selected_skills"],
        "skill_execution": "routing_metadata_only_no_agents_launched",
        "completed_stages": [
            "compile_request",
            "deterministic_facts",
            "deterministic_workbook",
            "seal_bundle",
        ],
        "narrative_status": "not_generated",
        "namespaces": {
            name: "proposals" if name in PROPOSAL_TABLES else "facts" for name in tables
        },
        "files": {
            path: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for path, data in documents.items()
        },
        "limits": [
            "Claims are limited to supplied evidence and explicit assumptions.",
            "Fixture/demo runs are not real hiring or financial findings.",
            "AI text is a separate derivative, not a fact input.",
        ],
    }
    for path, data in documents.items():
        store.write(path, data)
    raw_manifest = canonical_bytes(manifest)
    store.write("manifest.json", raw_manifest)
    return {
        "status": status,
        "run_id": run_id,
        "manifest_path": "manifest.json",
        "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
        "workbook_sha256": manifest["files"]["research.xlsx"]["sha256"],
        "request_hash": request.request_hash,
        "source_kind": source_kind,
        "selected_skills": compiled["selected_skills"],
        "dataset_rows": {key: len(rows) for key, rows in tables.items()},
    }


def verify_sealed_bundle(
    store: ArtifactStore, expected_manifest_sha256: str
) -> dict[str, Any]:
    raw = store.read("manifest.json")
    if hashlib.sha256(raw).hexdigest() != expected_manifest_sha256.removeprefix(
        "sha256:"
    ):
        raise ValueError("sealed manifest hash mismatch")
    manifest = json.loads(raw)
    if manifest.get("contract_version") != "sealed-research-bundle-v2":
        raise ValueError("unsupported sealed bundle")
    for path, binding in manifest["files"].items():
        data = store.read(path)
        if (
            hashlib.sha256(data).hexdigest() != binding["sha256"]
            or len(data) != binding["bytes"]
        ):
            raise ValueError("sealed artifact hash mismatch: " + path)
    return manifest


def validate_report_claims(
    store: ArtifactStore,
    expected_manifest_sha256: str,
    narrative: str,
    claims: dict[str, Any],
) -> dict[str, Any]:
    """Validate references and exact numeric quotations, never infer prose truth.

    The writer receives a sealed derivative. This function cannot update facts.
    Semantic interpretation still needs human review; arbitrary model arithmetic
    must first become a versioned computed row in another research run.
    """
    import re

    manifest = verify_sealed_bundle(store, expected_manifest_sha256)
    expected = expected_manifest_sha256.removeprefix("sha256:")
    if (
        claims.get("contract_version") != "research-claims-v1"
        or claims.get("manifest_sha256", "").removeprefix("sha256:") != expected
    ):
        raise ValueError("claim manifest/version mismatch")
    if set(claims) - {
        "contract_version",
        "manifest_sha256",
        "claims",
        "model_id",
        "prompt_sha256",
    }:
        raise ValueError("unsupported report claim metadata")
    if (
        not isinstance(narrative, str)
        or not narrative.strip()
        or not isinstance(claims.get("claims"), list)
    ):
        raise ValueError("report text and claims required")
    if manifest["source_kind"] in {"fixture", "demo"} and not any(
        s in narrative.lower() for s in ("시연", "fixture", "demo")
    ):
        raise ValueError("fixture/demo disclosure required")
    tables = json.loads(store.read("tables.json"))
    rows = {
        (table, row["_row_id"]): row
        for table, values in tables.items()
        for row in values
    }
    cells = json.loads(store.read("cell-refs.json"))
    ids: set[str] = set()
    remainder = narrative
    allowed_kinds = {
        "observed",
        "computed",
        "source_modelled",
        "inference",
        "user_assumption",
        "ai_proposed",
        "unknown",
        "conflict",
    }
    numeric = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")

    def at_pointer(value, pointer):
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            raise ValueError("value_pointer must be a JSON pointer")
        for part in pointer[1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            try:
                value = (
                    value[int(part)]
                    if isinstance(value, list) and part.isdigit()
                    else value[part]
                )
            except (KeyError, IndexError, TypeError) as error:
                raise ValueError("unknown claim value_pointer") from error
        return value

    for claim in claims["claims"]:
        if not isinstance(claim, dict) or set(claim) - {
            "claim_id",
            "text",
            "kind",
            "value",
            "unit",
            "refs",
            "assumptions",
        }:
            raise ValueError("unsupported report claim fields")
        if (
            not isinstance(claim, dict)
            or not claim.get("claim_id")
            or claim["claim_id"] in ids
        ):
            raise ValueError("unique claim_id required")
        ids.add(claim["claim_id"])
        text = claim.get("text")
        if (
            not isinstance(text, str)
            or not text
            or text not in narrative
            or claim.get("kind") not in allowed_kinds
        ):
            raise ValueError("invalid claim text/kind")
        refs = claim.get("refs", [])
        if not isinstance(refs, list) or not refs:
            raise ValueError("claim evidence references required")
        referenced = []
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) - {
                "table_id",
                "row_id",
                "column_id",
                "cell",
                "value_pointer",
            }:
                raise ValueError("invalid report reference")
            row = rows.get((ref.get("table_id"), ref.get("row_id")))
            column = ref.get("column_id")
            if row is None or column not in row:
                raise ValueError("unknown claim table/row/column")
            if "cell" in ref and not any(
                all(
                    c.get(k) == ref.get(k)
                    for k in ("table_id", "row_id", "column_id", "cell")
                )
                for c in cells
            ):
                raise ValueError("claim cell mismatch")
            base_value = row[column]
            resolved = (
                at_pointer(base_value, ref["value_pointer"])
                if "value_pointer" in ref
                else base_value
            )
            unit_row = row
            if (
                isinstance(base_value, dict)
                and ref.get("value_pointer") == "/amount"
                and "currency" in base_value
            ):
                unit_row = {**row, "unit": base_value["currency"]}
            referenced.append((unit_row, resolved))
            if (
                row.get("source_kind") in {"unknown", "fixture", "demo"}
                and manifest["source_kind"] == "observed"
                and claim["kind"] == "observed"
            ):
                raise ValueError(
                    "unverified or demonstration row is not observed evidence"
                )
            if ref["table_id"] in PROPOSAL_TABLES and claim["kind"] == "observed":
                raise ValueError("proposal cannot establish an observed claim")
            if ref["table_id"] == "GapsConflicts" and claim["kind"] not in {
                "unknown",
                "conflict",
                "inference",
            }:
                raise ValueError("evidence gap cannot establish an observed claim")
            if (
                row.get("kind")
                in {"computed", "source_modelled", "ai_proposed", "user_assumption"}
                and claim["kind"] == "observed"
            ):
                raise ValueError("derived or proposed value is not an observed claim")
        if numeric.search(text):
            if "value" not in claim or type(claim["value"]) not in (int, float):
                raise ValueError("numeric claim requires a bound numeric value")
            matches = [
                (row, val)
                for row, val in referenced
                if type(val) is type(claim["value"]) and val == claim["value"]
            ]
            if not matches or any(
                token.replace(",", "")
                not in {str(claim["value"]), format(claim["value"], "g")}
                for token in numeric.findall(text)
            ):
                raise ValueError("claim numeric value mismatch")
            if not claim.get("unit") or not any(
                row.get("unit") == claim["unit"] for row, _ in matches
            ):
                raise ValueError("claim unit mismatch")
        if claim["kind"] in {
            "inference",
            "ai_proposed",
            "user_assumption",
        } and not claim.get("assumptions"):
            raise ValueError("interpretation assumptions required")
        if any(
            row.get("kind") in {"unknown", "conflict"} for row, _ in referenced
        ) and claim["kind"] not in {"unknown", "conflict", "inference"}:
            raise ValueError("unknown evidence cannot establish an observed claim")
        remainder = remainder.replace(text, "")
    remainder = remainder.replace(manifest["as_of"], "").replace(manifest["run_id"], "")
    remainder = re.sub(r"https?://\S+", "", remainder)
    if re.search(r"\d", remainder):
        raise ValueError("unbound numeric statement")
    unbound = [
        line.strip()
        for line in remainder.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if any(
        line not in {"시연 자료.", "시연 자료입니다.", "Fixture data.", "Demo data."}
        for line in unbound
    ):
        raise ValueError(
            "unbound report text; every substantive statement needs a claim"
        )
    return {
        "status": "REFERENCES_VALIDATED",
        "manifest_sha256": expected,
        "report_sha256": hashlib.sha256(narrative.encode()).hexdigest(),
        "claims_sha256": content_hash(claims),
        "claim_count": len(ids),
        "semantic_review": "human_required",
        "model_id": claims.get("model_id", "not_recorded"),
        "prompt_sha256": claims.get("prompt_sha256", "not_recorded"),
    }


def seal_report(
    store: ArtifactStore,
    expected_manifest_sha256: str,
    narrative: str,
    claims: dict[str, Any],
) -> dict[str, Any]:
    receipt = validate_report_claims(store, expected_manifest_sha256, narrative, claims)
    directory = "reports/" + content_hash(
        [receipt["report_sha256"], receipt["claims_sha256"]]
    )
    store.write(directory + "/report.md", narrative.encode("utf-8"))
    store.write(directory + "/claims.json", canonical_bytes(claims))
    store.write(directory + "/receipt.json", canonical_bytes(receipt))
    return {**receipt, "report_path": directory + "/report.md"}
