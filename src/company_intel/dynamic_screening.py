from __future__ import annotations

import logging
from typing import Any

from .analysis_service import compare_revenue_and_hiring_trends
from .analytics import financial_metrics
from .connectors.ares_dynamic import AresDynamicClient
from .connectors.mpsv_stream import aggregate_by_cz_isco, stream_mpsv_vacancies
from .connectors.opendart_master import OpenDartMasterIndex
from .connectors.worknet import WorknetJobConnector
from .notion_queue import NotionApprovalQueue
from .publisher.blogger_publisher import BloggerPublisher

logger = logging.getLogger(__name__)


class DynamicScreeningEngine:
    """Unified dynamic screening engine connecting Stage #1 (Jobs/Lattice) and Stage #2 (Company Screening).

    Integrates:
    - OpenDART 119k Master Index for instantaneous Korean corporate resolution
    - Financial liquidity metrics (Quick Ratio, Cash Ratio, Debt/Equity, Working Capital)
    - Revenue trajectory vs. hiring trend correlation (Elasticity & Staffing Alignment)
    - Czech ARES registry dynamic lookups (IČO, trade name, CZ-NACE industry codes)
    - Czech MPSV vacancy stream aggregation by CZ-ISCO
    - WorkNet & Public Portal real-time job searches
    - Notion Mobile Approval Queue -> Google Blogger Headless automated publisher
    """

    def __init__(
        self,
        opendart_index: OpenDartMasterIndex | None = None,
        ares_client: AresDynamicClient | None = None,
        worknet_connector: WorknetJobConnector | None = None,
        notion_queue: NotionApprovalQueue | None = None,
        blogger_publisher: BloggerPublisher | None = None,
    ) -> None:
        self.opendart_index = opendart_index or OpenDartMasterIndex()
        self.ares_client = ares_client or AresDynamicClient()
        self.worknet_connector = worknet_connector or WorknetJobConnector()
        self.notion_queue = notion_queue or NotionApprovalQueue()
        self.blogger_publisher = blogger_publisher or BloggerPublisher()

    def screen_korean_company(
        self,
        name_or_code: str,
        facts: dict[str, float | None] | None = None,
        revenue_series: list[dict[str, Any]] | None = None,
        hiring_series: list[dict[str, Any]] | None = None,
        search_jobs: bool = False,
    ) -> dict[str, Any]:
        """Dynamically resolve Korean company and compute liquidity metrics & hiring trends."""
        resolved = self.opendart_index.resolve_corp_code(name_or_code)
        if isinstance(resolved, dict):
            corp_code = resolved.get("corp_code", name_or_code)
            corp_name = resolved.get("corp_name", name_or_code)
            stock_code = resolved.get("stock_code")
        elif isinstance(resolved, str):
            corp_code = resolved
            candidates = self.opendart_index.search_companies(name_or_code, limit=1)
            corp_name = candidates[0]["corp_name"] if candidates else name_or_code
            stock_code = candidates[0].get("stock_code") if candidates else None
        else:
            candidates = self.opendart_index.search_companies(name_or_code, limit=1)
            if candidates:
                corp_code = candidates[0]["corp_code"]
                corp_name = candidates[0]["corp_name"]
                stock_code = candidates[0].get("stock_code")
            else:
                corp_code = name_or_code
                corp_name = name_or_code
                stock_code = None

        company_info = {
            "country": "KR",
            "corp_code": corp_code,
            "corp_name": corp_name,
            "stock_code": stock_code,
        }

        # Calculate liquidity and financial solvency metrics
        computed_financials = {}
        if facts:
            computed_financials = financial_metrics(facts)

        # Revenue vs Hiring Trend Analysis
        trend_analysis = None
        if revenue_series and hiring_series:
            trend_analysis = compare_revenue_and_hiring_trends(revenue_series, hiring_series)

        # Real-time Job Search
        jobs: list[dict[str, Any]] = []
        if search_jobs:
            jobs = self.worknet_connector.search_public_jobs(keyword=corp_name)

        return {
            "status": "success",
            "country": "KR",
            "company_info": company_info,
            "financial_metrics": computed_financials,
            "trend_analysis": trend_analysis,
            "jobs": jobs,
        }

    def screen_czech_company(
        self,
        ico_or_name: str,
        mpsv_vacancies: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Dynamically resolve Czech company via ARES and correlate with MPSV labor demand."""
        raw_res = self.ares_client.get_economic_subject(ico_or_name)
        if not raw_res:
            candidates = self.ares_client.search_by_name(ico_or_name, limit=1)
            raw_res = candidates[0] if candidates else {}

        parsed_info = self.ares_client.extract_industry_and_address(raw_res)

        labor_demand = {}
        if mpsv_vacancies:
            if isinstance(mpsv_vacancies, list) and mpsv_vacancies and (
                "portalId" in mpsv_vacancies[0] or "profeseCzIsco" in mpsv_vacancies[0] or "polozky" in mpsv_vacancies[0]
            ):
                normalized = list(stream_mpsv_vacancies(mpsv_vacancies))
                labor_demand = aggregate_by_cz_isco(normalized)
            else:
                labor_demand = aggregate_by_cz_isco(mpsv_vacancies)

        return {
            "status": "success",
            "country": "CZ",
            "company_info": {
                "ico": parsed_info.get("ico", ico_or_name),
                "trade_name": parsed_info.get("trade_name"),
                "address": parsed_info.get("address"),
            },
            "cz_nace_codes": parsed_info.get("cz_nace", []),
            "labor_demand": labor_demand,
        }

    def sync_notion_to_blogger(self, dry_run: bool = True) -> list[dict[str, Any]]:
        """Poll approved posts from Notion mobile queue and publish to Blogger."""
        approved_pages = self.notion_queue.poll_approved_pages()
        results: list[dict[str, Any]] = []

        for page in approved_pages:
            page_id = page["page_id"]
            title = page.get("title", "Untitled Analysis")
            pub_res = self.blogger_publisher.publish_post_from_notion(page, dry_run=dry_run)

            post_url = pub_res.get("url") or f"https://sample-blog.blogspot.com/{page_id}"
            if not dry_run and pub_res.get("status") == "success":
                self.notion_queue.mark_published(page_id, post_url=post_url)

            results.append({
                "page_id": page_id,
                "title": title,
                "published_status": pub_res.get("status"),
                "post_url": post_url,
                "dry_run": dry_run,
            })

        return results


def run_screening_pipeline(params: dict[str, Any]) -> dict[str, Any]:
    """Execute dynamic screening pipeline based on parameter contracts."""
    country = params.get("country", "KR").upper()
    action = params.get("action", "screen")
    engine = DynamicScreeningEngine()

    if action == "sync_publishing":
        dry_run = params.get("dry_run", True)
        sync_results = engine.sync_notion_to_blogger(dry_run=dry_run)
        return {
            "status": "success",
            "action": "sync_publishing",
            "results": sync_results,
            "count": len(sync_results),
        }

    if country == "KR":
        company_name = params.get("company", "카카오")
        facts = params.get("facts")
        revenue_series = params.get("revenue_series")
        hiring_series = params.get("hiring_series")
        search_jobs = params.get("search_jobs", False)
        return engine.screen_korean_company(
            company_name,
            facts=facts,
            revenue_series=revenue_series,
            hiring_series=hiring_series,
            search_jobs=search_jobs,
        )
    elif country == "CZ":
        ico = params.get("ico", "00177041")
        vacancies = params.get("vacancies")
        return engine.screen_czech_company(ico, mpsv_vacancies=vacancies)
    else:
        return {
            "status": "error",
            "reason": f"Unsupported country: {country}",
        }
