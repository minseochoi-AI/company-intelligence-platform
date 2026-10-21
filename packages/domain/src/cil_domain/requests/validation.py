"""Pure predicates for report filtering; unknown is never the ALL wildcard."""

from __future__ import annotations
from typing import Any


def field_value(record: dict[str, Any], field: str) -> Any:
    value: Any = record
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def predicate_verdict(record: dict[str, Any], predicate: dict[str, Any]) -> str:
    actual = field_value(record, predicate["field_id"])
    operator = predicate["operator"]
    if operator == "exists":
        return "match" if actual is not None else "no_match"
    if actual is None or actual == "" or actual in ("unknown", "ALL"):
        return "unknown"
    expected = predicate.get("value")
    if expected == "ALL":
        return "not_applicable"
    if operator == "eq":
        matched = type(actual) is type(expected) and actual == expected
    elif operator == "in":
        if not isinstance(expected, list):
            raise ValueError("in requires a typed list")
        matched = any(
            type(actual) is type(item) and actual == item for item in expected
        )
    elif operator == "contains":
        matched = (
            isinstance(actual, str)
            and isinstance(expected, str)
            and expected.casefold() in actual.casefold()
        )
    elif operator in {"gte", "lte"}:
        if (
            isinstance(actual, bool)
            or isinstance(expected, bool)
            or not isinstance(actual, (float, int))
            or not isinstance(expected, (float, int))
        ):
            return "unknown"
        matched = actual >= expected if operator == "gte" else actual <= expected
    else:
        raise ValueError("unregistered predicate operator")
    return "match" if matched else "no_match"


def cohort_verdict(query: str, record: str | None) -> str:
    if len(query.split(":")) != 5:
        raise ValueError("exactly five legacy dimensions required")
    if record is None:
        return "unknown"
    if len(record.split(":")) != 5:
        raise ValueError("malformed record signature")
    unknown = False
    for expected, actual in zip(query.split(":"), record.split(":"), strict=True):
        if expected == "ALL":
            continue
        if actual in {"ALL", "unknown", "", "UNKNOWN"}:
            unknown = True
        elif expected != actual:
            return "no_match"
    return "unknown" if unknown else "match"
