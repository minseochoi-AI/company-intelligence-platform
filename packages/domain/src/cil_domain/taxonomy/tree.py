"""Canonical responsibility owner; migrated from src/company_intel/category_tree.py."""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping

PURPOSE_ROOTS = (
    ("data_status", "데이터 준비 상태"),
    ("current_jobs", "현재 채용 검색"),
    ("job_trends", "채용 동향"),
    ("organization_analysis", "기업·기관 분석"),
    ("delivery", "설명·내보내기"),
)


@dataclass(frozen=True)
class PurposeNode:
    value: str
    label: str
    detail: str = ""


@dataclass(frozen=True)
class FacetBranch:
    field: str
    value: str
    count: int
    coverage: float
    enabled: bool
    disabled_reason: str | None = None


@dataclass(frozen=True)
class SelectionSession:
    purpose: str | None = None
    selections: tuple[tuple[str, str], ...] = ()
    snapshot_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "purpose": self.purpose,
            "selections": dict(self.selections),
            "snapshot_id": self.snapshot_id,
        }


def _matches(row: Mapping[str, Any], selections: Iterable[tuple[str, str]]) -> bool:
    for field, expected in selections:
        observed = row.get(field)
        values = observed if isinstance(observed, (list, tuple, set)) else (observed,)
        if not any(
            (
                str(item).casefold() == expected.casefold()
                for item in values
                if item is not None
            )
        ):
            return False
    return True


def preview_selection(
    rows: Iterable[Mapping[str, Any]], session: SelectionSession
) -> dict[str, Any]:
    selected = [dict(row) for row in rows if _matches(row, session.selections)]
    providers = {str(row.get("provider")) for row in selected if row.get("provider")}
    return {
        "count": len(selected),
        "coverage": len(providers),
        "snapshot_id": session.snapshot_id,
        "rows": selected,
    }


def advance_selection(
    session: SelectionSession, rows: Iterable[Mapping[str, Any]], field: str, value: str
) -> SelectionSession:
    candidate = replace(session, selections=(*session.selections, (field, value)))
    if preview_selection(rows, candidate)["count"] == 0:
        raise ValueError("invalid_selection")
    return candidate


def backtrack_selection(
    session: SelectionSession, field: str | None = None
) -> SelectionSession:
    if not session.selections:
        return session
    if field is None:
        return replace(session, selections=session.selections[:-1])
    return replace(
        session,
        selections=tuple((item for item in session.selections if item[0] != field)),
    )


def branches_for_selection(
    rows: Iterable[Mapping[str, Any]], session: SelectionSession, field: str
) -> list[FacetBranch]:
    preview = preview_selection(rows, session)["rows"]
    total = len(preview)
    values: dict[str, int] = {}
    for row in preview:
        raw = row.get(field)
        iterable = raw if isinstance(raw, (list, tuple, set)) else (raw,)
        for item in iterable:
            if item not in (None, "", "unknown"):
                values[str(item)] = values.get(str(item), 0) + 1
    if not values:
        return [
            FacetBranch(field, "__unavailable__", 0, 0.0, False, f"{field}_unavailable")
        ]
    return [
        FacetBranch(field, value, count, count / total if total else 0.0, count > 0)
        for value, count in sorted(values.items())
    ]


def roots() -> tuple[PurposeNode, ...]:
    return tuple((PurposeNode(value, label) for value, label in PURPOSE_ROOTS))
