from __future__ import annotations

import html
import json
import os
import re
import urllib.request
import urllib.error
from typing import Any


class BloggerPublisher:
    """Headless automated publisher for Google Blogger API v3."""

    BASE_URL = "https://www.googleapis.com/blogger/v3"

    def __init__(self, access_token: str | None = None, default_blog_id: str | None = None) -> None:
        self.access_token = access_token or os.getenv("BLOGGER_ACCESS_TOKEN")
        self.default_blog_id = default_blog_id or os.getenv("BLOGGER_BLOG_ID", "default-company-intel-blog")

    def render_html(
        self,
        title: str,
        markdown_content: str,
        svg_urls: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Convert markdown and diagram attachments to clean Blogger HTML."""
        lines = markdown_content.strip().splitlines()
        html_parts = [
            f"<div class='cil-report-container' style='font-family: sans-serif; line-height: 1.6; color: #2d3748;'>",
            f"<h1 style='color: #1a202c; border-bottom: 2px solid #3182ce; padding-bottom: 8px;'>{html.escape(title)}</h1>",
        ]

        if tags:
            tag_badges = "".join(
                f"<span style='background: #e2e8f0; color: #4a5568; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; margin-right: 6px;'>#{html.escape(t)}</span>"
                for t in tags
            )
            html_parts.append(f"<div style='margin-bottom: 16px;'>{tag_badges}</div>")

        in_list = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                continue

            if stripped.startswith("### "):
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<h3 style='color: #2b6cb0; margin-top: 18px;'>{html.escape(stripped[4:])}</h3>")
            elif stripped.startswith("## "):
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<h2 style='color: #2c5282; margin-top: 24px;'>{html.escape(stripped[3:])}</h2>")
            elif stripped.startswith("# "):
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<h1 style='color: #1a202c; margin-top: 28px;'>{html.escape(stripped[2:])}</h1>")
            elif stripped.startswith("* ") or stripped.startswith("- "):
                if not in_list:
                    html_parts.append("<ul style='padding-left: 20px; margin-bottom: 12px;'>")
                    in_list = True
                html_parts.append(f"<li>{html.escape(stripped[2:])}</li>")
            else:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<p style='margin-bottom: 12px;'>{html.escape(stripped)}</p>")

        if in_list:
            html_parts.append("</ul>")

        if svg_urls:
            html_parts.append("<div class='cil-diagram-gallery' style='margin-top: 24px; text-align: center;'>")
            for url in svg_urls:
                html_parts.append(
                    f"<div style='margin-bottom: 16px;'><img src='{html.escape(url)}' style='max-width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 8px;' alt='Career Lattice Diagram'/></div>"
                )
            html_parts.append("</div>")

        html_parts.append("</div>")
        return "\n".join(html_parts)

    def publish_post(
        self,
        title: str,
        content_markdown: str,
        blog_id: str | None = None,
        svg_urls: list[str] | None = None,
        tags: list[str] | None = None,
        is_draft: bool = True,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Publish a post to Google Blogger. Defaults to dry-run/isDraft=True for test safety."""
        target_blog = blog_id or self.default_blog_id
        rendered_html = self.render_html(title, content_markdown, svg_urls=svg_urls, tags=tags)

        post_body = {
            "kind": "blogger#post",
            "title": title,
            "content": rendered_html,
            "labels": tags or ["CompanyIntel"],
        }

        if dry_run or not self.access_token:
            # Deterministic, zero-remote-write dry-run response
            return {
                "status": "published_dry_run" if not is_draft else "draft_created_dry_run",
                "blog_id": target_blog,
                "post_id": "dry-run-post-001",
                "url": f"https://company-intel.blogspot.com/2026/10/{re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-')}.html",
                "is_draft": is_draft,
                "rendered_html_length": len(rendered_html),
                "remote_writes_executed": 0,
            }

        # Real API execution
        url = f"{self.BASE_URL}/blogs/{target_blog}/posts?isDraft={'true' if is_draft else 'false'}"
        req = urllib.request.Request(
            url,
            data=json.dumps(post_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                return {
                    "status": "published" if not is_draft else "draft_created",
                    "blog_id": target_blog,
                    "post_id": resp_json.get("id"),
                    "url": resp_json.get("url"),
                    "is_draft": is_draft,
                    "rendered_html_length": len(rendered_html),
                    "remote_writes_executed": 1,
                }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "remote_writes_executed": 0,
            }

    def publish_post_from_notion(
        self,
        notion_item: dict[str, Any],
        notion_queue: Any,
        blog_id: str | None = None,
        is_draft: bool = False,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Publish an approved item from Notion queue and update the Notion status."""
        title = notion_item.get("title", "Untitled Report")
        content_md = notion_item.get("content_markdown", "")
        tags = notion_item.get("tags") or []

        result = self.publish_post(
            title=title,
            content_markdown=content_md,
            blog_id=blog_id,
            tags=tags,
            is_draft=is_draft,
            dry_run=dry_run,
        )

        published_url = result.get("url") or f"https://company-intel.blogspot.com/published/{notion_item['id']}"
        notion_queue.mark_published(notion_item["id"], published_url)
        result["notion_page_id"] = notion_item["id"]
        result["notion_status"] = "발행 완료"
        return result
