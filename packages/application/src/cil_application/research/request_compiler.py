"""Compile a user's purpose into a bounded, provenance-carrying research run."""

from __future__ import annotations
from copy import deepcopy
from typing import Any, Protocol

from cil_contracts.requests import ReportRequest, content_hash, timestamp
from cil_domain.requests.validation import cohort_verdict, predicate_verdict


class CapabilityPort(Protocol):
    def resolve_binding(self, binding: dict[str, Any]) -> list[dict[str, str]]: ...
    def known_field(self, field: str, postings: list[dict[str, Any]]) -> bool: ...


def selected_skills(purposes: tuple[str, ...] | list[str]) -> list[str]:
    chosen = {"S01", "S08"}
    routes = {
        "selected-posting": "S02",
        "financial": "S03",
        "work-future": "S04",
        "path": "S05",
        "portfolio": "S06",
        "venture": "S07",
    }
    for purpose in purposes:
        chosen.add(routes[purpose])
    if set(purposes) & {"path", "portfolio", "work-future"}:
        chosen.add("S02")
    return sorted(chosen)


def compile_request(
    request: ReportRequest,
    snapshot: dict[str, Any],
    registry: CapabilityPort,
    *,
    allow_refresh: bool = False,
) -> dict[str, Any]:
    if not isinstance(request, ReportRequest) or not isinstance(snapshot, dict):
        raise TypeError("ReportRequest and snapshot object required")
    value = request.as_dict()
    gaps: list[dict[str, Any]] = []
    input_gaps: list[dict[str, Any]] = []
    subjects = request.subject_refs
    requires_posting = bool(
        set(request.purpose) & {"selected-posting", "path", "portfolio", "work-future"}
    )
    if requires_posting and not subjects:
        input_gaps.append(
            {"field": "subject_refs", "reason": "selected_posting_reference_required"}
        )
    if (
        value.get("refresh_policy", "saved_only") == "authorized_refresh"
        and not allow_refresh
    ):
        input_gaps.append(
            {"field": "refresh_policy", "reason": "refresh_not_authorized"}
        )
    origins = value.get("argument_origins", [])
    pointers = [x["json_pointer"] for x in origins]
    if len(pointers) != len(set(pointers)):
        input_gaps.append(
            {"field": "argument_origins", "reason": "duplicate_origin_pointer"}
        )
    if any(
        x.get("origin") == "ai_proposed"
        and x["json_pointer"].split("/")[1]
        in {"profile_ref", "subject_refs", "as_of", "source_bindings"}
        for x in origins
    ):
        input_gaps.append(
            {
                "field": "argument_origins",
                "reason": "proposed_identity_or_eligibility_requires_evidence",
            }
        )
    if not origins:
        input_gaps.append(
            {"field": "argument_origins", "reason": "argument_provenance_required"}
        )
    required_origins = {"purpose", "question", "as_of"} | {
        k
        for k, v in request.research.values.items()
        if k != "argument_origins" and v not in (None, [], {})
    }
    if subjects:
        required_origins.add("subject_refs")
    if request.cohort_signature != "ALL:ALL:ALL:ALL:ALL":
        required_origins.add("cohort_signature")
    root_authority = any(
        x["json_pointer"] == "/" and x["origin"] == "user_explicit" for x in origins
    )
    if not root_authority:
        for name in sorted(required_origins):
            if "/" + name not in pointers:
                input_gaps.append(
                    {"field": name, "reason": "argument_origin_not_covered"}
                )
    evidence_refs = {
        str(row.get("source_id")) for row in snapshot.get("sources", [])
    } | {"snapshot:" + content_hash(snapshot)}
    for origin in origins:
        if (
            origin["origin"] == "source_derived"
            and origin["evidence_ref"] not in evidence_refs
        ):
            input_gaps.append(
                {
                    "field": origin["json_pointer"],
                    "reason": "argument_origin_evidence_not_found",
                }
            )
    for binding in value.get("source_bindings", []):
        gaps.extend(registry.resolve_binding(binding))
        sources = snapshot.get("sources", [])
        source = next(
            (s for s in sources if s.get("source_id") == binding.get("source_id")), None
        )
        if source is None:
            gaps.append({"field": "source_bindings", "reason": "bound_source_missing"})
        elif source.get("snapshot_hash", "").removeprefix("sha256:") != binding.get(
            "snapshot_hash", ""
        ).removeprefix("sha256:"):
            gaps.append(
                {"field": "source_bindings", "reason": "bound_snapshot_hash_mismatch"}
            )
        elif "payload" not in source:
            gaps.append(
                {"field": "source_bindings", "reason": "bound_payload_not_archived"}
            )
        elif content_hash(source["payload"]) != binding["snapshot_hash"].removeprefix(
            "sha256:"
        ):
            gaps.append(
                {"field": "source_bindings", "reason": "bound_payload_hash_mismatch"}
            )
    for ref_name, collection in {
        "profile_ref": "profiles",
        "scenario_ref": "scenario_sets",
        "role_mapping_ref": "role_mappings",
        "task_weights_ref": "task_weight_sets",
    }.items():
        if value.get(ref_name) and value[ref_name] not in snapshot.get(collection, {}):
            input_gaps.append(
                {"field": ref_name, "reason": "saved_reference_not_found"}
            )
    limits = value.get("execution_limits", {})
    from cil_contracts.requests import canonical_bytes

    if (
        "max_input_bytes" in limits
        and len(canonical_bytes(snapshot)) > limits["max_input_bytes"]
    ):
        input_gaps.append(
            {"field": "execution_limits", "reason": "input_byte_limit_exceeded"}
        )
    postings = snapshot.get("postings", [])
    if not isinstance(postings, list) or any(not isinstance(p, dict) for p in postings):
        raise ValueError("postings must be an array of objects")
    matched: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    known_time = (
        value.get("history", {}).get("revision_mode", "known_at_time")
        == "known_at_time"
    )
    for ref in subjects:
        found = [
            p
            for p in postings
            if (p.get("provider_id"), p.get("posting_id"), p.get("revision"))
            == (ref.provider_id, ref.posting_id, ref.revision)
        ]
        if len(found) != 1:
            gaps.append(
                {
                    "field": "subject_refs",
                    "reason": "posting_not_found"
                    if not found
                    else "conflicting_posting_identity",
                }
            )
            continue
        posting = deepcopy(found[0])
        if ref.entity_id is not None and posting.get("entity_id") != ref.entity_id:
            gaps.append(
                {"field": "subject_refs", "reason": "employer_identity_conflict"}
            )
            continue
        if ref.role_id is not None and posting.get("role_id") != ref.role_id:
            gaps.append({"field": "subject_refs", "reason": "role_identity_conflict"})
            continue
        if any(
            getattr(ref, name) is not None and posting.get(name) != getattr(ref, name)
            for name in ("vacancy_batch_id", "location_id")
        ):
            gaps.append(
                {
                    "field": "subject_refs",
                    "reason": "posting_batch_or_location_identity_conflict",
                }
            )
            continue
        available_at = posting.get("available_at")
        if not available_at:
            gaps.append(
                {
                    "field": "postings.available_at",
                    "reason": "availability_time_unknown",
                }
            )
        elif timestamp(available_at) > timestamp(request.as_of):
            exclusions.append(
                {"posting_id": ref.posting_id, "reason": "not_available_as_of"}
            )
            continue
        cohort = cohort_verdict(
            request.cohort_signature, posting.get("cluster_signature")
        )
        verdicts = []
        if cohort != "match":
            verdicts.append({"field": "cohort_signature", "verdict": cohort})
        rejected = cohort == "no_match"
        for predicate in value.get("field_filters", []):
            if not registry.known_field(predicate["field_id"], postings):
                input_gaps.append(
                    {
                        "field": predicate["field_id"],
                        "reason": "unregistered_filter_field",
                    }
                )
                continue
            if predicate["field_id"].startswith(
                "raw_attributes."
            ) and not predicate.get("semantic_version"):
                input_gaps.append(
                    {
                        "field": predicate["field_id"],
                        "reason": "raw_filter_semantic_version_required",
                    }
                )
                continue
            verdict = predicate_verdict(posting, predicate)
            verdicts.append({"field": predicate["field_id"], "verdict": verdict})
            policy = predicate.get("unknown_policy", "separate")
            if verdict == "unknown" and policy == "error":
                input_gaps.append(
                    {"field": predicate["field_id"], "reason": "unknown_filter_value"}
                )
            if verdict == "no_match" or (verdict == "unknown" and policy == "exclude"):
                rejected = True
        posting["selection_verdicts"] = verdicts
        if rejected:
            exclusions.append(
                {
                    "posting_id": ref.posting_id,
                    "reason": "filter_not_matched",
                    "verdicts": verdicts,
                }
            )
        else:
            matched.append(posting)
    if subjects and not matched and not input_gaps:
        gaps.append({"field": "postings", "reason": "no_selected_evidence_matches"})
    kind = snapshot.get("source_kind", "unknown")
    if kind == "observed" and any(
        row.get("source_kind") in {"fixture", "demo"}
        for collection in (
            "postings",
            "financials",
            "wages",
            "tasks",
            "competition",
            "opportunities",
            "sources",
        )
        for row in snapshot.get(collection, [])
        if isinstance(row, dict)
    ):
        gaps.append(
            {"field": "provenance", "reason": "fixture_cannot_be_promoted_to_observed"}
        )
    coverage = snapshot.get("coverage")
    if isinstance(coverage, dict) and coverage.get("complete") is not True:
        gaps.append(
            {
                "field": "coverage",
                "reason": "saved_collection_incomplete_or_unknown",
                "coverage": deepcopy(coverage),
            }
        )
    for row in matched:
        if any(
            v.get("verdict") == "unknown" for v in row.get("selection_verdicts", [])
        ):
            gaps.append(
                {
                    "field": "selection",
                    "reason": "selected_posting_has_unknown_filter_evidence",
                    "posting_id": row["posting_id"],
                }
            )
    if kind not in {"observed", "fixture", "demo", "unknown"}:
        raise ValueError("unrecognized snapshot source_kind")
    if kind == "unknown":
        gaps.append({"field": "source_kind", "reason": "snapshot_provenance_unknown"})
    status = (
        "NEEDS_INPUT"
        if input_gaps
        else "NEEDS_EVIDENCE"
        if (subjects and not matched)
        or any(
            g.get("reason") == "fixture_cannot_be_promoted_to_observed" for g in gaps
        )
        or any(g["field"] == "source_bindings" for g in gaps)
        else "PARTIAL"
        if gaps
        else "VALIDATED"
    )
    return {
        "status": status,
        "request": value,
        "request_hash": request.request_hash,
        "snapshot_hash": content_hash(snapshot),
        "source_kind": kind,
        "selected_skills": selected_skills(request.purpose),
        "selected_postings": matched,
        "exclusions": exclusions,
        "gaps": input_gaps + gaps,
        "authority": "saved_evidence_only"
        if not allow_refresh
        else "explicit_refresh_boundary",
    }
