from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from company_intel.dynamic_screening import DynamicScreeningEngine, run_screening_pipeline


def test_dynamic_screening_korean_company():
    mock_opendart = MagicMock()
    mock_opendart.resolve_corp_code.return_value = "00258801"
    mock_opendart.search_companies.return_value = [
        {
            "corp_code": "00258801",
            "corp_name": "카카오",
            "stock_code": "035720",
            "modify_date": "20240101",
        }
    ]

    mock_worknet = MagicMock()
    mock_worknet.search_public_jobs.return_value = [
        {"wanted_title": "데이터 엔지니어 채용", "company_name": "카카오"}
    ]

    engine = DynamicScreeningEngine(
        opendart_index=mock_opendart,
        worknet_connector=mock_worknet,
    )

    facts = {
        "revenue": 1000.0,
        "revenue_previous": 800.0,
        "current_assets": 500.0,
        "current_liabilities": 250.0,
        "inventory": 50.0,
        "cash": 150.0,
        "debt": 200.0,
        "equity": 600.0,
        "cfo": 120.0,
        "capex": 40.0,
        "net_income": 80.0,
    }

    revenue_series = [
        {"period": "2024-01", "revenue": 800.0},
        {"period": "2024-02", "revenue": 1000.0},
    ]
    hiring_series = [
        {"collected_at": "2024-01-15", "active_postings": 50},
        {"collected_at": "2024-02-15", "active_postings": 65},
    ]

    result = engine.screen_korean_company(
        "카카오",
        facts=facts,
        revenue_series=revenue_series,
        hiring_series=hiring_series,
        search_jobs=True,
    )

    assert result["status"] == "success"
    assert result["country"] == "KR"
    assert result["company_info"]["corp_code"] == "00258801"
    assert result["company_info"]["corp_name"] == "카카오"

    metrics = result["financial_metrics"]
    assert metrics["current_ratio"] == 2.0  # 500 / 250
    assert metrics["quick_ratio"] == 1.8  # (500 - 50) / 250
    assert metrics["cash_ratio"] == 0.6  # 150 / 250
    assert metrics["working_capital"] == 250.0  # 500 - 250
    assert metrics["debt_to_equity"] == pytest.approx(200.0 / 600.0)

    trends = result["trend_analysis"]
    assert trends is not None
    assert trends["status"] == "success"
    assert len(trends["aligned_series"]) == 2

    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["wanted_title"] == "데이터 엔지니어 채용"


def test_dynamic_screening_czech_company():
    mock_ares = MagicMock()
    mock_ares.get_economic_subject.return_value = {
        "ico": "00177041",
        "obchodniJmeno": "Škoda Auto a.s.",
        "czNace": ["29100", "29200", "29320"],
    }
    mock_ares.extract_industry_and_address.return_value = {
        "ico": "00177041",
        "trade_name": "Škoda Auto a.s.",
        "cz_nace": ["29100", "29200", "29320"],
        "address": "Tř. Václava Klementa 869, 29301 Mladá Boleslav",
    }

    engine = DynamicScreeningEngine(ares_client=mock_ares)

    vacancies = [
        {
            "occupation_pivot": "2512",
            "occupation_code": "25121",
            "salary_min": 65000,
            "salary_max": 95000,
            "city": "Praha",
            "occupation_label": "Vývojáři software",
        },
        {
            "occupation_pivot": "2512",
            "occupation_code": "25121",
            "salary_min": 70000,
            "salary_max": 100000,
            "city": "Mladá Boleslav",
            "occupation_label": "Vývojáři software",
        },
    ]

    result = engine.screen_czech_company("00177041", mpsv_vacancies=vacancies)
    assert result["status"] == "success"
    assert result["country"] == "CZ"
    assert result["company_info"]["trade_name"] == "Škoda Auto a.s."
    assert "29100" in result["cz_nace_codes"]

    demand = result["labor_demand"]
    assert "2512" in demand
    assert demand["2512"]["vacancy_count"] == 2
    assert demand["2512"]["avg_salary_min"] == 67500.0


def test_dynamic_screening_notion_blogger_sync():
    mock_queue = MagicMock()
    mock_queue.poll_approved_pages.return_value = [
        {
            "page_id": "p-101",
            "title": "카카오 4대 관점 투자 및 채용 분석",
            "approved": True,
            "published": False,
            "content": "## 카카오 분석 내용\n본문...",
        }
    ]

    mock_pub = MagicMock()
    mock_pub.publish_post_from_notion.return_value = {
        "status": "success",
        "id": "post-789",
        "url": "https://company-intel.blogspot.com/2026/10/kakao.html",
        "dry_run": False,
    }

    engine = DynamicScreeningEngine(
        notion_queue=mock_queue,
        blogger_publisher=mock_pub,
    )

    results = engine.sync_notion_to_blogger(dry_run=False)
    assert len(results) == 1
    assert results[0]["page_id"] == "p-101"
    assert results[0]["published_status"] == "success"
    assert results[0]["post_url"] == "https://company-intel.blogspot.com/2026/10/kakao.html"

    mock_queue.mark_published.assert_called_once_with(
        "p-101",
        post_url="https://company-intel.blogspot.com/2026/10/kakao.html",
    )


def test_dynamic_screening_pipeline():
    """Verify run_screening_pipeline entrypoint for all dispatch actions."""
    # Test KR dispatch
    kr_res = run_screening_pipeline({
        "country": "KR",
        "company": "삼성전자",
        "facts": {"revenue": 2000.0, "current_assets": 1000.0, "current_liabilities": 500.0},
    })
    assert kr_res["status"] == "success"
    assert kr_res["country"] == "KR"
    assert kr_res["financial_metrics"]["current_ratio"] == 2.0

    # Test CZ dispatch
    cz_res = run_screening_pipeline({
        "country": "CZ",
        "ico": "00177041",
    })
    assert cz_res["status"] == "success"
    assert cz_res["country"] == "CZ"

    # Test sync dispatch
    sync_res = run_screening_pipeline({
        "action": "sync_publishing",
        "dry_run": True,
    })
    assert sync_res["status"] == "success"
    assert sync_res["action"] == "sync_publishing"
