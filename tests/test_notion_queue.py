from cil_integrations.publishing.notion import NotionApprovalQueue


def test_notion_approval_flow():
    queue = NotionApprovalQueue(token="")  # Explicit offline test mode

    # 1. Create a draft report
    md_content = """# 카카오 기업 및 직무 분석
    ## 핵심 요약
    * 당좌비율 145.2%로 유동성 건전
    * 고용 탄력성 0.82로 완만한 채용 기조 유지
    """
    draft = queue.create_draft_page(
        title="2026년 카카오 기업 분석 및 직무 트랙 리포트",
        content_markdown=md_content,
        category="기업 분석",
        tags=["KR", "카카오", "테크"],
        svg_url="https://example.com/kakao_lattice.svg",
    )

    assert draft["id"].startswith("notion-draft-") or len(draft["id"]) > 5
    assert draft["status"] == "검토 대기"
    assert draft["approved"] is False

    # 2. Poll approved - initially none
    approved = queue.poll_approved_pages()
    assert len(approved) == 0

    # 3. Simulate user tapping "Approve" on Notion mobile app
    updated = queue.approve_page(draft["id"])
    assert updated is not None
    assert updated["approved"] is True
    assert updated["status"] == "발행 승인"

    # 4. Polling now returns the approved draft
    approved = queue.poll_approved_pages()
    assert len(approved) == 1
    assert approved[0]["id"] == draft["id"]

    # 5. Mark as published to Blogger
    published = queue.mark_published(draft["id"], "https://company-intel.blogspot.com/2026/10/kakao-analysis.html")
    assert published is not None
    assert published["status"] == "발행 완료"
    assert published["published_url"] == "https://company-intel.blogspot.com/2026/10/kakao-analysis.html"


def test_notion_markdown_to_blocks():
    queue = NotionApprovalQueue(token=None)
    md = "# 제목1\n## 제목2\n* 항목A\n단락 텍스트"
    blocks = queue._markdown_to_blocks(md)
    assert len(blocks) == 4
    assert blocks[0]["type"] == "heading_1"
    assert blocks[1]["type"] == "heading_2"
    assert blocks[2]["type"] == "bulleted_list_item"
    assert blocks[3]["type"] == "paragraph"
