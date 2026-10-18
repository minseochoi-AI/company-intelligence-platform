import io
import zipfile
from pathlib import Path
import pytest
from company_intel.connectors.opendart_master import OpenDartMasterIndex, resolve_corp_code, search_kr_companies


def test_opendart_master_initialization(tmp_path: Path):
    db_file = tmp_path / "test_kr_companies.duckdb"
    master = OpenDartMasterIndex(db_path=db_file)
    
    # Check that curated companies were populated
    samsung = master.resolve_corp_code("삼성전자")
    assert samsung == "00126380"

    kakao = master.resolve_corp_code("카카오")
    assert kakao == "00258801"

    naver = master.resolve_corp_code("네이버")
    assert naver == "00266961"

    # Non-existent company
    assert master.resolve_corp_code("존재하지않는회사ABCXYZ") is None


def test_opendart_master_search(tmp_path: Path):
    db_file = tmp_path / "test_kr_companies.duckdb"
    master = OpenDartMasterIndex(db_path=db_file)

    results = master.search_companies("삼성")
    assert len(results) >= 1
    assert any(r["corp_name"] == "삼성전자" and r["corp_code"] == "00126380" for r in results)

    # Search by stock code
    results_stock = master.search_companies("005930")
    assert len(results_stock) >= 1
    assert results_stock[0]["corp_name"] == "삼성전자"


def test_opendart_master_xml_sync(tmp_path: Path):
    db_file = tmp_path / "test_sync.duckdb"
    master = OpenDartMasterIndex(db_path=db_file)

    sample_xml = """<?xml version="1.0" encoding="utf-8"?>
    <result>
        <list>
            <corp_code>99990001</corp_code>
            <corp_name>테스트테크</corp_name>
            <stock_code>999010</stock_code>
            <modify_date>20261015</modify_date>
        </list>
        <list>
            <corp_code>99990002</corp_code>
            <corp_name>글로벌인텔</corp_name>
            <stock_code></stock_code>
            <modify_date>20261015</modify_date>
        </list>
    </result>
    """

    count = master.sync_from_xml_content(sample_xml)
    assert count == 2

    assert master.resolve_corp_code("테스트테크") == "99990001"
    assert master.resolve_corp_code("글로벌인텔") == "99990002"

    details = master.get_company_by_corp_code("99990001")
    assert details is not None
    assert details["corp_name"] == "테스트테크"
    assert details["stock_code"] == "999010"


def test_opendart_master_zip_sync(tmp_path: Path):
    db_file = tmp_path / "test_zip.duckdb"
    master = OpenDartMasterIndex(db_path=db_file)

    sample_xml = """<?xml version="1.0" encoding="utf-8"?>
    <result>
        <list>
            <corp_code>88880001</corp_code>
            <corp_name>압축테스트법인</corp_name>
            <stock_code>888010</stock_code>
            <modify_date>20261015</modify_date>
        </list>
    </result>
    """
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("CORPCODE.xml", sample_xml.encode("utf-8"))
    zip_bytes = bio.getvalue()

    count = master.sync_from_zip_bytes(zip_bytes)
    assert count == 1
    assert master.resolve_corp_code("압축테스트법인") == "88880001"
