"""Canonical responsibility owner; migrated from src/company_intel/connectors/opendart_master.py."""

from __future__ import annotations
from pathlib import Path
from typing import Any
import io
import os
import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

DEFAULT_CURATED_COMPANIES = [
    {
        "corp_code": "00126380",
        "corp_name": "삼성전자",
        "stock_code": "005930",
        "modify_date": "20240320",
    },
    {
        "corp_code": "00258801",
        "corp_name": "카카오",
        "stock_code": "035720",
        "modify_date": "20240315",
    },
    {
        "corp_code": "00266961",
        "corp_name": "네이버",
        "stock_code": "035420",
        "modify_date": "20240318",
    },
    {
        "corp_code": "00164779",
        "corp_name": "현대자동차",
        "stock_code": "005380",
        "modify_date": "20240321",
    },
    {
        "corp_code": "00164742",
        "corp_name": "SK하이닉스",
        "stock_code": "000660",
        "modify_date": "20240319",
    },
    {
        "corp_code": "00401731",
        "corp_name": "LG전자",
        "stock_code": "066570",
        "modify_date": "20240322",
    },
    {
        "corp_code": "00185040",
        "corp_name": "엔씨소프트",
        "stock_code": "036570",
        "modify_date": "20240314",
    },
]


class OpenDartMasterIndex:
    """Manages the full Korean registered corporation master index (119k+ entities)."""

    def __init__(
        self, db_path: Path | str | None = None, api_key: str | None = None
    ) -> None:
        self.api_key = api_key or os.getenv("OPENDART_API_KEY")
        if db_path is None:
            configured_root = os.getenv("COMPANY_INTEL_PROJECT_ROOT", ".")
            self.db_path = Path(configured_root) / "data/kr_company_master.duckdb"
        else:
            self.db_path = Path(db_path)
        self._ensure_initialized()

    def _get_connection(self):
        try:
            import duckdb

            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            return duckdb.connect(str(self.db_path))
        except (ImportError, Exception):
            sqlite_path = self.db_path.with_suffix(".sqlite")
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            return sqlite3.connect(str(sqlite_path))

    def _ensure_initialized(self) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                "\n                CREATE TABLE IF NOT EXISTS kr_company_master (\n                    corp_code VARCHAR PRIMARY KEY,\n                    corp_name VARCHAR,\n                    stock_code VARCHAR,\n                    modify_date VARCHAR\n                )\n                "
            )
            res = conn.execute("SELECT COUNT(*) FROM kr_company_master").fetchone()
            count = res[0] if res else 0
            if count == 0:
                self._load_curated_defaults(conn)
        finally:
            conn.close()

    def _load_curated_defaults(self, conn) -> None:
        for comp in DEFAULT_CURATED_COMPANIES:
            conn.execute(
                "\n                INSERT OR REPLACE INTO kr_company_master (corp_code, corp_name, stock_code, modify_date)\n                VALUES (?, ?, ?, ?)\n                ",
                (
                    comp["corp_code"],
                    comp["corp_name"],
                    comp["stock_code"],
                    comp["modify_date"],
                ),
            )

    def sync_from_xml_content(self, xml_content: str | bytes) -> int:
        """Parse raw XML string or bytes and upsert into the master table."""
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = ET.fromstring(xml_content)
        records = []
        for item in root.findall(".//list"):
            c_code = (item.findtext("corp_code") or "").strip()
            c_name = (item.findtext("corp_name") or "").strip()
            s_code = (item.findtext("stock_code") or "").strip()
            m_date = (item.findtext("modify_date") or "").strip()
            if c_code and c_name:
                records.append((c_code, c_name, s_code, m_date))
        if not records:
            return 0
        conn = self._get_connection()
        try:
            conn.executemany(
                "\n                INSERT OR REPLACE INTO kr_company_master (corp_code, corp_name, stock_code, modify_date)\n                VALUES (?, ?, ?, ?)\n                ",
                records,
            )
        finally:
            conn.close()
        return len(records)

    def sync_from_zip_bytes(self, zip_data: bytes) -> int:
        """Extract CORPCODE.xml from OpenDART downloaded ZIP archive and ingest."""
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".xml"):
                    with zf.open(name) as xml_file:
                        return self.sync_from_xml_content(xml_file.read())
        return 0

    def sync_from_api(self, timeout: float = 30.0) -> int:
        """Fetch live corpCode.xml from OpenDART and update local master index."""
        if not self.api_key:
            raise ValueError("OPENDART_API_KEY is required to sync from OpenDART API.")
        url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={urllib.parse.quote(self.api_key)}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "company-intelligence/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            return self.sync_from_zip_bytes(content)

    def resolve_corp_code(self, company_name: str) -> str | None:
        """Resolve OpenDART corp_code from company name with exact and normalized matching."""
        if not company_name:
            return None
        target = company_name.strip()
        conn = self._get_connection()
        try:
            cur = conn.execute(
                "SELECT corp_code FROM kr_company_master WHERE corp_name = ? LIMIT 1",
                (target,),
            )
            row = cur.fetchone()
            if row:
                return row[0]
            cur = conn.execute(
                "SELECT corp_code FROM kr_company_master WHERE LOWER(REPLACE(corp_name, ' ', '')) = LOWER(REPLACE(?, ' ', '')) LIMIT 1",
                (target,),
            )
            row = cur.fetchone()
            if row:
                return row[0]
            cur = conn.execute(
                "\n                SELECT corp_code FROM kr_company_master \n                WHERE corp_name LIKE ? OR corp_name LIKE ?\n                ORDER BY LENGTH(corp_name) ASC\n                LIMIT 1\n                ",
                (f"%{target}%", f"{target}%"),
            )
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def search_companies(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search registered Korean corporations matching query."""
        if not query:
            return []
        conn = self._get_connection()
        try:
            cur = conn.execute(
                "\n                SELECT corp_code, corp_name, stock_code, modify_date\n                FROM kr_company_master\n                WHERE corp_name LIKE ? OR stock_code LIKE ?\n                ORDER BY CASE WHEN corp_name = ? THEN 1 WHEN corp_name LIKE ? THEN 2 ELSE 3 END,\n                         LENGTH(corp_name) ASC\n                LIMIT ?\n                ",
                (f"%{query}%", f"%{query}%", query, f"{query}%", limit),
            )
            results = []
            for row in cur.fetchall():
                results.append(
                    {
                        "corp_code": row[0],
                        "corp_name": row[1],
                        "stock_code": row[2] or None,
                        "modify_date": row[3],
                    }
                )
            return results
        finally:
            conn.close()

    def get_company_by_corp_code(self, corp_code: str) -> dict[str, Any] | None:
        """Lookup company details by corp_code."""
        conn = self._get_connection()
        try:
            cur = conn.execute(
                "\n                SELECT corp_code, corp_name, stock_code, modify_date\n                FROM kr_company_master\n                WHERE corp_code = ?\n                LIMIT 1\n                ",
                (corp_code.strip(),),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "corp_code": row[0],
                "corp_name": row[1],
                "stock_code": row[2] or None,
                "modify_date": row[3],
            }
        finally:
            conn.close()


_global_index: OpenDartMasterIndex | None = None


def get_master_index() -> OpenDartMasterIndex:
    global _global_index
    if _global_index is None:
        _global_index = OpenDartMasterIndex()
    return _global_index


def resolve_corp_code(company_name: str) -> str | None:
    return get_master_index().resolve_corp_code(company_name)


def search_kr_companies(query: str, limit: int = 10) -> list[dict[str, Any]]:
    return get_master_index().search_companies(query, limit)
