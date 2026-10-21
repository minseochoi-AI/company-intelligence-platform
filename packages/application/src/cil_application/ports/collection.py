"""Explicit collection boundary. Saved analysis never invokes this port."""

from typing import Any, Protocol


class PageSource(Protocol):
    def fetch_page(
        self, parameters: dict[str, Any], cursor: str | None
    ) -> dict[str, Any]:
        """Return records, archived payload, optional next_cursor and available_at."""
        ...
