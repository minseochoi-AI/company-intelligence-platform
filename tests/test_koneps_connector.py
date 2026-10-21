from __future__ import annotations

import pytest
from cil_integrations.providers.koneps.procurements import CanonicalProcurementRecord, CURATED_KONEPS_FIXTURES, KONEPSProcurementConnector


def test_koneps_fixtures_structure():
    assert len(CURATED_KONEPS_FIXTURES) >= 5
    for item in CURATED_KONEPS_FIXTURES:
        rec = CanonicalProcurementRecord(**item)
        assert rec.country == "KR"
        assert rec.source_system == "KONEPS"
        assert rec.currency == "KRW"
        assert rec.contract_amount > 0
        assert rec.buyer_name
        assert rec.title


def test_koneps_search_filter():
    connector = KONEPSProcurementConnector(service_key=None, demo=True)
    
    # Search for AI related bids
    ai_results = connector.search_procurements(query="AI", num_of_rows=5)
    assert len(ai_results) >= 1
    assert any("AI" in r.title for r in ai_results)

    # Search for KEPCO / 한국전력공사
    kepco_results = connector.search_procurements(query="한국전력공사", num_of_rows=5)
    assert len(kepco_results) >= 1
    assert any("한국전력공사" in r.buyer_name for r in kepco_results)


def test_koneps_xml_parser():
    connector = KONEPSProcurementConnector(service_key="test-key")
    sample_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
        </header>
        <body>
            <items>
                <item>
                    <bidNtceNo>20261019001</bidNtceNo>
                    <bidNtceOrd>01</bidNtceOrd>
                    <bidNtceNm>\xec\xb0\xa8\xec\x84\xb8\xeb\x8c\x80 \xeb\x94\x94\xec\xa7\x80\xed\x84\xb8 \xed\x96\x89\xec\xa0\x95 \xed\x81\xb4\xeb\x9d\xbc\xec\x9a\xb0\xeb\x93\x9c \xea\xb5\xac\xec\xb6\x95</bidNtceNm>
                    <orderInsttNm>\xed\x96\x89\xec\xa0\x95\xec\x95\x88\xec\xa0\x84\xeb\xb6\x80</orderInsttNm>
                    <asignBdgtAmt>25000000000</asignBdgtAmt>
                    <bidNtceDt>2026-10-15</bidNtceDt>
                    <opengCorpNm>\xec\x82\xbc\xec\x84\xb1SDS</opengCorpNm>
                    <indstrytyNm>\xec\x86\x8f\xed\x8a\xb8\xec\x9b\xa8\xec\x96\xb4\xec\x82\xac\xec\x97\x85</indstrytyNm>
                    <bidNtceDtlUrl>https://www.g2b.go.kr/bid/20261019001</bidNtceDtlUrl>
                </item>
            </items>
        </body>
    </response>
    """
    records = connector._parse_koneps_xml(sample_xml)
    assert len(records) == 1
    rec = records[0]
    assert rec.procurement_id == "KR-KONEPS-20261019001-01"
    assert rec.buyer_name == "행정안전부"
    assert rec.contract_amount == 25000000000.0
    assert rec.winner_name == "삼성SDS"
    assert rec.country == "KR"
    assert rec.currency == "KRW"
