"""Versioned research specifications embedded in the common report request.

This module uses the standard library only. Interpretation and IO belong to the
domain and application packages; parsing never silently discards an input field.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import hashlib
import json
import math

REQUEST_FIELDS = frozenset(
    {
        "purpose",
        "question",
        "cohort_signature",
        "subject_refs",
        "profile_ref",
        "as_of",
        "history",
        "field_filters",
        "comparability",
        "source_bindings",
        "refresh_policy",
        "metric_specs",
        "competition_spec",
        "requirement_policy",
        "financial_spec",
        "scenario_ref",
        "role_mapping_ref",
        "task_weights_ref",
        "exposure_method",
        "wage_comparison",
        "career_spec",
        "portfolio_spec",
        "venture_spec",
        "report_spec",
        "argument_origins",
        "execution_limits",
    }
)
PURPOSES = frozenset(
    {"selected-posting", "financial", "path", "portfolio", "venture", "work-future"}
)
ORIGINS = frozenset(
    {"user_explicit", "source_derived", "policy_default", "ai_proposed"}
)
UNKNOWN_POLICIES = frozenset({"exclude", "include", "separate", "error"})
OPTION_FIELDS = {
    "history": {"revision_mode", "period_start", "period_end"},
    "comparability": {
        "country",
        "concept",
        "scope",
        "currency",
        "unit",
        "frequency",
        "period_basis",
    },
    "competition_spec": {"round_id", "stage", "role_id", "location_id", "cutoff"},
    "requirement_policy": {"kinds", "include_unknown"},
    "financial_spec": {"entity_id", "entity_ids", "concepts"},
    "wage_comparison": {"assumptions", "country", "currency", "basis", "period"},
    "career_spec": {"architecture", "role_tracks", "relations", "employer_id"},
    "portfolio_spec": {
        "proposal_ids",
        "opportunity_ids",
        "task_ids",
        "dataset_rights",
        "max_budget",
    },
    "venture_spec": {"proposal_ids", "opportunity_ids", "jurisdictions", "max_budget"},
    "report_spec": {
        "datasets",
        "columns",
        "locale",
        "audience",
        "layout_version",
        "claim_policy",
    },
    "execution_limits": {"max_input_bytes", "max_rows", "max_provider_calls"},
}
METRICS = {
    "competition_ratio",
    "stage_pass_rate",
    "eligibility",
    "financial_growth",
    "wage_conversion",
    "task_exposure",
}


def _validate_options(options: dict[str, Any]) -> None:
    for name, allowed in OPTION_FIELDS.items():
        if name in options and set(options[name]) - allowed:
            raise ValueError(
                "unsupported "
                + name
                + " options: "
                + ", ".join(sorted(set(options[name]) - allowed))
            )
    for metric in options.get("metric_specs", []):
        if (
            not isinstance(metric, dict)
            or set(metric) - {"metric_id", "method_version"}
            or metric.get("metric_id") not in METRICS
            or metric.get("method_version") != "1.0.0"
        ):
            raise ValueError("unsupported metric/version")
    history = options.get("history", {})
    assumptions = options.get("wage_comparison", {}).get("assumptions", {})
    if not isinstance(assumptions, dict) or set(assumptions) - {
        "hours_per_year",
        "payments_per_year",
        "paid_weeks_per_year",
        "author_kind",
    }:
        raise ValueError("unsupported wage conversion assumptions")
    if (
        "datasets" in options.get("report_spec", {})
        and not options["report_spec"]["datasets"]
    ):
        raise ValueError("report datasets cannot be empty")
    for key in ("period_start", "period_end"):
        if key in history:
            try:
                datetime.strptime(history[key], "%Y-%m-%d")
            except (TypeError, ValueError) as error:
                raise ValueError("history period must be YYYY-MM-DD") from error
    if history.get("period_start", "") > history.get("period_end", "9999-12-31"):
        raise ValueError("history period is reversed")
    for name in ("scenario_ref", "role_mapping_ref", "task_weights_ref", "profile_ref"):
        if name in options and (
            not isinstance(options[name], str) or not options[name].strip()
        ):
            raise ValueError(name + " must be a saved snapshot identifier")
    method = options.get("exposure_method")
    if method is not None and not isinstance(method, (str, dict)):
        raise ValueError("exposure_method must be an identifier or explicit method")
    if isinstance(method, dict) and set(method) - {
        "method_id",
        "version",
        "scale_min",
        "scale_max",
    }:
        raise ValueError("unsupported exposure method option")
    report = options.get("report_spec", {})
    if (
        report.get("layout_version", "research-xlsx-v1") != "research-xlsx-v1"
        or report.get("claim_policy", "strict") != "strict"
    ):
        raise ValueError("unsupported report layout/claim policy")
    for name, opt in options.items():
        if name not in OPTION_FIELDS:
            continue
        for key, val in opt.items():
            if key in {
                "kinds",
                "entity_ids",
                "concepts",
                "role_tracks",
                "relations",
                "proposal_ids",
                "opportunity_ids",
                "task_ids",
                "jurisdictions",
                "datasets",
            } and (
                not isinstance(val, list) or any(not isinstance(x, str) for x in val)
            ):
                raise ValueError(name + "." + key + " requires string array")
    policy = options.get("requirement_policy", {})
    if (
        set(policy.get("kinds", [])) - {"required", "preferred", "disqualifier"}
        or type(policy.get("include_unknown", True)) is not bool
    ):
        raise ValueError("invalid requirement policy")
    limits = options.get("execution_limits", {})
    for key, val in limits.items():
        if type(val) is not int or val < 0:
            raise ValueError("execution limits require nonnegative integers")
    if limits.get("max_provider_calls", 0) != 0:
        raise ValueError("saved research supports zero provider calls")
    if "columns" in report and (
        not isinstance(report["columns"], dict)
        or any(
            not isinstance(v, list) or any(not isinstance(c, str) for c in v)
            for v in report["columns"].values()
        )
    ):
        raise ValueError("report columns require table-to-column arrays")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string with an explicit timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("invalid timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires an explicit timezone")
    return parsed


def _finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite numeric input")
    if isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _finite(item)


@dataclass(frozen=True)
class PostingRef:
    provider_id: str
    posting_id: str
    revision: str
    entity_id: str | None = None
    role_id: str | None = None
    vacancy_batch_id: str | None = None
    location_id: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> PostingRef:
        fields = set(cls.__dataclass_fields__)
        if not isinstance(value, dict) or set(value) - fields:
            raise ValueError("unknown posting reference field")
        for name in ("provider_id", "posting_id", "revision"):
            if not isinstance(value.get(name), str) or not value[name].strip():
                raise ValueError("posting reference requires " + name)
        for name in fields - {"provider_id", "posting_id", "revision"}:
            if (
                name in value
                and value[name] is not None
                and (not isinstance(value[name], str) or not value[name].strip())
            ):
                raise ValueError(
                    "posting reference identifier must be nonempty text: " + name
                )
        return cls(**value)

    def as_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}


@dataclass(frozen=True)
class ArgumentOrigin:
    json_pointer: str
    origin: str
    evidence_ref: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ArgumentOrigin:
        if not isinstance(value, dict) or set(value) - {
            "json_pointer",
            "origin",
            "evidence_ref",
        }:
            raise ValueError("unknown argument origin field")
        if (
            not str(value.get("json_pointer", "")).startswith("/")
            or value.get("origin") not in ORIGINS
        ):
            raise ValueError("invalid argument origin")
        if value["origin"] == "source_derived" and not value.get("evidence_ref"):
            raise ValueError("source-derived arguments require evidence_ref")
        return cls(**value)


@dataclass(frozen=True)
class ResearchSpec:
    """Domain-specific options inside ReportRequest, never another root parser."""

    values: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return deepcopy(self.values)


@dataclass(frozen=True)
class ReportRequest:
    purpose: tuple[str, ...]
    question: str
    cohort_signature: str
    subject_refs: tuple[PostingRef, ...]
    as_of: str
    research: ResearchSpec
    schema_version: str = "2.0.0"

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ReportRequest:
        if not isinstance(value, dict):
            raise ValueError("request must be an object")
        unknown = (
            set(value) - REQUEST_FIELDS - {"schema_version", "request_schema_version"}
        )
        if unknown:
            raise ValueError("unknown request fields: " + ", ".join(sorted(unknown)))
        version = value.get(
            "schema_version", value.get("request_schema_version", "2.0.0")
        )
        if version != "2.0.0":
            raise ValueError("unsupported report request version")
        _finite(value)
        purposes = value.get("purpose", [])
        if not isinstance(purposes, list) or not purposes or set(purposes) - PURPOSES:
            raise ValueError("purpose must select registered research purposes")
        question = value.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question is required")
        signature = value.get("cohort_signature", "ALL:ALL:ALL:ALL:ALL")
        if (
            not isinstance(signature, str)
            or len(signature.split(":")) != 5
            or any(not p for p in signature.split(":"))
        ):
            raise ValueError(
                "legacy cohort signature requires exactly five nonempty dimensions"
            )
        timestamp(value.get("as_of"))
        refs = value.get("subject_refs", [])
        if not isinstance(refs, list):
            raise ValueError("subject_refs must be an array")
        subjects = tuple(PostingRef.from_dict(item) for item in refs)
        if len({(r.provider_id, r.posting_id, r.revision) for r in subjects}) != len(
            subjects
        ):
            raise ValueError("duplicate posting reference")
        options = deepcopy(
            {
                k: v
                for k, v in value.items()
                if k
                in REQUEST_FIELDS
                - {"purpose", "question", "cohort_signature", "subject_refs", "as_of"}
            }
        )
        if options.get("refresh_policy", "saved_only") not in {
            "saved_only",
            "authorized_refresh",
        }:
            raise ValueError("invalid refresh policy")
        for name in (
            "field_filters",
            "source_bindings",
            "metric_specs",
            "argument_origins",
        ):
            if name in options and not isinstance(options[name], list):
                raise ValueError(name + " must be an array")
        for name in (
            "history",
            "comparability",
            "competition_spec",
            "requirement_policy",
            "financial_spec",
            "wage_comparison",
            "career_spec",
            "portfolio_spec",
            "venture_spec",
            "report_spec",
            "execution_limits",
        ):
            if name in options and not isinstance(options[name], dict):
                raise ValueError(name + " must be an object")
        for predicate in options.get("field_filters", []):
            if not isinstance(predicate, dict) or set(predicate) - {
                "field_id",
                "operator",
                "value",
                "unknown_policy",
                "semantic_version",
            }:
                raise ValueError("unknown predicate field")
            if not predicate.get("field_id") or predicate.get("operator") not in {
                "eq",
                "in",
                "contains",
                "gte",
                "lte",
                "exists",
            }:
                raise ValueError("invalid field predicate")
            if predicate.get("unknown_policy", "separate") not in UNKNOWN_POLICIES:
                raise ValueError("invalid predicate unknown policy")
        for origin in options.get("argument_origins", []):
            ArgumentOrigin.from_dict(origin)
        _validate_options(options)
        mode = options.get("history", {}).get("revision_mode", "known_at_time")
        if mode not in {"known_at_time", "current_restated"}:
            raise ValueError("invalid history revision mode")
        return cls(
            tuple(dict.fromkeys(purposes)),
            question,
            signature,
            subjects,
            value["as_of"],
            ResearchSpec(options),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "purpose": list(self.purpose),
            "question": self.question,
            "cohort_signature": self.cohort_signature,
            "subject_refs": [r.as_dict() for r in self.subject_refs],
            "as_of": self.as_of,
            **self.research.as_dict(),
        }

    @property
    def request_hash(self) -> str:
        return content_hash(self.as_dict())


# Historical design documents used this view name. There is one parser and type.
ResearchRequest = ReportRequest
