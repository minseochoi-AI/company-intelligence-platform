"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from dataclasses import dataclass
from typing import Any, Callable, Mapping
import xml.etree.ElementTree as ET


def _public_employment(body: bytes, _: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    jobs = []
    for item in root.findall(".//item"):
        jobs.append(
            {
                "posting_id": item.findtext("idx"),
                "institution_name": item.findtext("insttname"),
                "title": item.findtext("title"),
                "institution_type": item.findtext("type01"),
                "posting_type": item.findtext("type02"),
                "registered_at": item.findtext("regdate"),
                "closing_at": item.findtext("enddate"),
            }
        )
    return {
        "result_code": root.findtext(".//resultCode"),
        "result_message": root.findtext(".//resultMsg"),
        "total": to_number(root.findtext(".//totalCount")),
        "jobs": jobs,
    }


@dataclass(frozen=True)
class MPMPublicEmploymentConnector:
    """Bounded MPM list collection without embedding a service key in results."""

    fetch_page: Callable[[Mapping[str, Any]], Mapping[str, Any]]

    def iter_pages(
        self, *, page_size: int = 100, max_pages: int = 100, sort_order: str = "2"
    ) -> list[dict[str, Any]]:
        if page_size < 1 or max_pages < 1:
            raise ValueError("page_size and max_pages must be positive")
        seen: set[str] = set()
        results: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            payload = self.fetch_page(
                {"pageNo": page, "numOfRows": page_size, "Sort_order": sort_order}
            )
            rows = (
                payload.get("jobs")
                or payload.get("postings")
                or payload.get("items")
                or []
            )
            if not isinstance(rows, list):
                raise ValueError("mpm_page_rows_invalid")
            for row in rows:
                if not isinstance(row, dict):
                    continue
                posting_id = str(row.get("posting_id") or row.get("idx") or "")
                if posting_id and posting_id in seen:
                    continue
                if posting_id:
                    seen.add(posting_id)
                results.append(dict(row))
            if len(rows) < page_size:
                break
        return results

    def collect_snapshot(self, **kwargs: Any) -> dict[str, Any]:
        rows = self.iter_pages(**kwargs)
        return {
            "jobs": rows,
            "record_count": len(rows),
            "deduplicated_by": "posting_id",
        }
