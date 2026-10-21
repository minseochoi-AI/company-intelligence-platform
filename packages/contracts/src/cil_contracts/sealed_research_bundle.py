"""Stable references between evidence datasets, workbooks and AI claims."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkbookBuild:
    data: bytes
    cell_refs: tuple[dict[str, Any], ...]
    overflows: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SealedResearchBundle:
    run_id: str
    manifest_path: str
    manifest_sha256: str
    workbook_sha256: str
    request_hash: str
    source_kind: str
    status: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class ClaimRef:
    table_id: str
    row_id: str
    column_id: str
    value_pointer: str | None = None


@dataclass(frozen=True)
class ReportReceipt:
    manifest_sha256: str
    report_sha256: str
    claims_sha256: str
    model: str
    prompt_sha256: str | None
    status: str
