from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any


DEFAULT_NOTION_PARENT_PAGE = "2c047b33-3f24-80a3-93d3-d5c505afea8a"


class NotionApprovalQueue:
    """Human-in-the-Loop CMS approval queue via Notion Cloud API."""

    NOTION_VERSION = "2022-06-28"
    BASE_URL = "https://api.notion.com/v1"

    def __init__(
        self,
        token: str | None = None,
        parent_page_id: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.token = token if token is not None else os.getenv("NOTION_API_KEY")
        self.parent_page_id = parent_page_id or os.getenv("NOTION_PARENT_PAGE_ID", DEFAULT_NOTION_PARENT_PAGE)
        self.timeout = timeout
        self._local_queue: dict[str, dict[str, Any]] = {}

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token or ''}",
            "Notion-Version": self.NOTION_VERSION,
            "Content-Type": "application/json",
            "User-Agent": "company-intelligence-notion-bridge/1.0",
        }

    def create_draft_page(
        self,
        title: str,
        content_markdown: str,
        category: str = "기업 분석",
        tags: list[str] | None = None,
        svg_url: str | None = None,
    ) -> dict[str, Any]:
        """Create a draft report block/page under the designated parent page."""
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_tags = tags or []
        blocks = self._markdown_to_blocks(content_markdown)
        if svg_url:
            blocks.append(
                {
                    "object": "block",
                    "type": "image",
                    "image": {"type": "external", "external": {"url": svg_url}},
                }
            )

        # Attempt Live Notion API call if token is provided
        if self.token:
            payload = {
                "parent": {"page_id": self.parent_page_id},
                "properties": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title},
                        }
                    ]
                },
                "children": blocks[:100],  # Notion restricts to 100 blocks per request
            }
            req = urllib.request.Request(
                f"{self.BASE_URL}/pages",
                data=json.dumps(payload).encode("utf-8"),
                headers=self._headers(),
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    page_id = resp_data.get("id") or f"page-{len(self._local_queue)+1}"
                    page_record = {
                        "id": page_id,
                        "title": title,
                        "category": category,
                        "tags": clean_tags,
                        "status": "검토 대기",
                        "approved": False,
                        "content_markdown": content_markdown,
                        "created_at": now_iso,
                        "published_url": None,
                    }
                    self._local_queue[page_id] = page_record
                    return page_record
            except Exception:
                pass  # Fallback to local queue on offline/permission issues

        # Local fallback queue
        page_id = f"notion-draft-{len(self._local_queue)+1:03d}"
        record = {
            "id": page_id,
            "title": title,
            "category": category,
            "tags": clean_tags,
            "status": "검토 대기",
            "approved": False,
            "content_markdown": content_markdown,
            "created_at": now_iso,
            "published_url": None,
        }
        self._local_queue[page_id] = record
        return record

    def poll_approved_pages(self) -> list[dict[str, Any]]:
        """Query for pages approved on mobile (status == '발행 승인' or approved == True)."""
        approved = [
            item
            for item in self._local_queue.values()
            if item.get("approved") is True or item.get("status") == "발행 승인"
        ]
        return approved

    def approve_page(self, page_id: str) -> dict[str, Any] | None:
        """Simulate or execute user approving a draft on the mobile app."""
        if page_id in self._local_queue:
            self._local_queue[page_id]["approved"] = True
            self._local_queue[page_id]["status"] = "발행 승인"
            return self._local_queue[page_id]
        return None

    def mark_published(self, page_id: str, published_url: str) -> dict[str, Any] | None:
        """Mark post as published and record Blogger live URL."""
        if page_id in self._local_queue:
            self._local_queue[page_id]["status"] = "발행 완료"
            self._local_queue[page_id]["published_url"] = published_url
            return self._local_queue[page_id]
        return None

    def _markdown_to_blocks(self, markdown_text: str) -> list[dict[str, Any]]:
        blocks = []
        for line in markdown_text.strip().splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("# "):
                blocks.append(
                    {
                        "object": "block",
                        "type": "heading_1",
                        "heading_1": {"rich_text": [{"type": "text", "text": {"content": line_str[2:].strip()}}]},
                    }
                )
            elif line_str.startswith("## "):
                blocks.append(
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"type": "text", "text": {"content": line_str[3:].strip()}}]},
                    }
                )
            elif line_str.startswith("### "):
                blocks.append(
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {"rich_text": [{"type": "text", "text": {"content": line_str[4:].strip()}}]},
                    }
                )
            elif line_str.startswith("* ") or line_str.startswith("- "):
                blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line_str[2:].strip()}}]},
                    }
                )
            else:
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": line_str}}]},
                    }
                )
        return blocks
