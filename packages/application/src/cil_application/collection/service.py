"""Bounded collection orchestration with explicit status and no demo fallback."""

from copy import deepcopy
from cil_application.ports.collection import PageSource
from cil_contracts.requests import content_hash


class CollectionService:
    def collect(
        self,
        source: PageSource,
        parameters: dict,
        *,
        authorized: bool = False,
        max_pages: int = 1,
    ) -> dict:
        if not authorized:
            return {"status": "NEEDS_AUTHORIZATION", "pages": [], "provider_calls": 0}
        if type(max_pages) is not int or max_pages < 1:
            raise ValueError("positive max_pages required")
        pages, cursor, visited = [], None, set()
        for count in range(max_pages):
            try:
                page = source.fetch_page(deepcopy(parameters), cursor)
                if (
                    not isinstance(page, dict)
                    or not isinstance(page.get("records"), list)
                    or "payload" not in page
                ):
                    raise ValueError("provider page contract violation")
                pages.append(deepcopy(page))
            except (OSError, ValueError, RuntimeError) as error:
                # Error messages can contain request URLs or credentials. Keep the class only.
                return {
                    "status": "ERROR",
                    "error_type": type(error).__name__,
                    "pages": pages,
                    "provider_calls": count + 1,
                    "complete": False,
                }
            cursor = page.get("next_cursor")
            if cursor is None:
                return {
                    "status": "EMPTY"
                    if not any(p["records"] for p in pages)
                    else "COLLECTED",
                    "pages": pages,
                    "provider_calls": count + 1,
                    "complete": True,
                    "snapshot_hash": content_hash(pages),
                }
            if not isinstance(cursor, str) or not cursor or cursor in visited:
                return {
                    "status": "ERROR",
                    "error_type": "PaginationCycle",
                    "pages": pages,
                    "provider_calls": count + 1,
                    "complete": False,
                }
            visited.add(cursor)
        return {
            "status": "PARTIAL",
            "pages": pages,
            "provider_calls": max_pages,
            "complete": False,
            "next_cursor": cursor,
            "snapshot_hash": content_hash(pages),
        }
