from cil_integrations.providers.worknet.jobs import WorknetJobConnector, search_worknet_jobs


def test_worknet_jobs_parsing():
    connector = WorknetJobConnector()
    jobs = connector.search_public_jobs(num_of_rows=3)
    assert len(jobs) >= 1

    first = jobs[0]
    assert "title" in first
    assert "institution_name" in first
    assert first["country_code"] == "KR"


def test_worknet_mock_xml_parsing():
    connector = WorknetJobConnector(service_key="dummy_key")
    sample_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
        </header>
        <body>
            <items>
                <item>
                    <idx>9991</idx>
                    <insttname>\xed\x95\x9c\xea\xb5\xad\xec\x97\x90\xeb\x84\x88\xec\xa7\x80\xea\xb3\xb5\xeb\x8b\xa8</insttname>
                    <title>\xec\x8b\xa0\xec\x9e\xac\xec\x83\x9d\xec\x97\x90\xeb\x84\x88\xec\xa7\x80 \xec\xa0\x84\xeb\xac\xb8\xea\xb0\x80 \xec\xb1\x84\xec\x9a\xa9</title>
                    <workRgnNm>\xec\x9a\xb8\xec\x82\xb0\xea\xb4\x91\xec\x97\xad\xec\x8b\x9c</workRgnNm>
                    <regdate>2026-10-15</regdate>
                    <enddate>2026-10-30</enddate>
                    <pbancUrl>https://www.energy.or.kr</pbancUrl>
                    <type01>\xec\xa0\x95\xea\xb7\x9c\xec\xa7\x81</type01>
                </item>
            </items>
        </body>
    </response>
    """
    parsed = connector._parse_public_job_xml(sample_xml, keyword=None)
    assert len(parsed) == 1
    assert parsed[0]["institution_name"] == "한국에너지공단"
    assert "신재생에너지" in parsed[0]["title"]
    assert parsed[0]["region"] == "울산광역시"


def test_worknet_keyword_filter():
    connector = WorknetJobConnector(service_key="")
    ai_jobs = connector.search_public_jobs(keyword="데이터")
    assert len(ai_jobs) >= 1
    assert any("데이터" in j["title"] for j in ai_jobs)


def test_worknet_convenience():
    results = search_worknet_jobs(limit=2)
    assert len(results) <= 2
