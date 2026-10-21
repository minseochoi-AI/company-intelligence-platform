from cil_integrations.publishing.blogger import BloggerPublisher
from cil_integrations.publishing.notion import NotionApprovalQueue


def test_blogger_html_rendering():
    publisher = BloggerPublisher()
    md = """# 체코 핀테크 기업 분석 보고서
    ## 시장 동향
    * 프라하 중심의 소프트웨어 채용 확대
    * 평균 제시 연봉 상승세
    """
    html_out = publisher.render_html(
        title="체코 핀테크 기업 분석 보고서",
        markdown_content=md,
        svg_urls=["https://example.com/czech_fintech.svg"],
        tags=["CZ", "Fintech"],
    )

    assert "cil-report-container" in html_out
    assert "체코 핀테크 기업 분석 보고서" in html_out
    assert "#CZ" in html_out
    assert "#Fintech" in html_out
    assert "<li>프라하 중심의 소프트웨어 채용 확대</li>" in html_out
    assert "https://example.com/czech_fintech.svg" in html_out


def test_blogger_dry_run_safety():
    publisher = BloggerPublisher()
    result = publisher.publish_post(
        title="테스트 분석 포스트",
        content_markdown="# 내용",
        tags=["Test"],
        dry_run=True,
    )
    assert result["remote_writes_executed"] == 0
    assert "url" in result
    assert result["status"] == "draft_created_dry_run"


def test_blogger_from_notion_flow():
    queue = NotionApprovalQueue(token=None)
    publisher = BloggerPublisher()

    # 1. Create and approve in Notion queue
    draft = queue.create_draft_page(
        title="현대자동차 2026 채용 및 재무 스크리닝",
        content_markdown="# 현대차 분석\n* 당좌비율 양호",
        tags=["KR", "자동차"],
    )
    queue.approve_page(draft["id"])
    approved_items = queue.poll_approved_pages()
    assert len(approved_items) == 1

    # 2. Publish from Notion
    pub_res = publisher.publish_post_from_notion(
        approved_items[0],
        notion_queue=queue,
        is_draft=False,
        dry_run=True,
    )

    assert pub_res["notion_page_id"] == draft["id"]
    assert pub_res["notion_status"] == "발행 완료"
    assert pub_res["remote_writes_executed"] == 0

    # 3. Verify Notion queue reflects published state
    updated_draft = queue._local_queue[draft["id"]]
    assert updated_draft["status"] == "발행 완료"
    assert updated_draft["published_url"] is not None
