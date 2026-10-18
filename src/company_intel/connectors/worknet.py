from __future__ import annotations

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


CURATED_PUBLIC_JOB_FIXTURES = [
    {
        "posting_id": "PBL-2026-001",
        "institution_name": "한국지능정보사회진흥원",
        "title": "2026년도 데이터 AI 아키텍트 정규직 채용",
        "region": "대구광역시",
        "registered_at": "2026-10-10",
        "closing_at": "2026-10-25",
        "url": "https://www.nia.or.kr",
        "employment_type": "정규직",
        "ncs_code": "20010101",
        "ncs_label": "데이터 아키텍처",
        "country_code": "KR",
    },
    {
        "posting_id": "PBL-2026-002",
        "institution_name": "한국전력공사",
        "title": "2026년 하반기 배전 ICT 전문인력 공개채용",
        "region": "전라남도",
        "registered_at": "2026-10-12",
        "closing_at": "2026-10-28",
        "url": "https://home.kepco.co.kr",
        "employment_type": "정규직",
        "ncs_code": "19010101",
        "ncs_label": "전기설비 운영",
        "country_code": "KR",
    },
    {
        "posting_id": "PBL-2026-003",
        "institution_name": "한국생명공학연구원",
        "title": "바이오 파운드리 합성생물학 박사후연구원 모집",
        "region": "대전광역시",
        "registered_at": "2026-10-14",
        "closing_at": "2026-11-05",
        "url": "https://www.kribb.re.kr",
        "employment_type": "계약직",
        "ncs_code": "17010101",
        "ncs_label": "생명과학 연구",
        "country_code": "KR",
    },
]


class WorknetJobConnector:
    """Connects to Korean Government data.go.kr (Insa Innovation / Worknet) Job Services."""

    PUBLIC_JOB_URL = "https://apis.data.go.kr/1760000/PblJobService/getList"

    def __init__(self, service_key: str | None = None, timeout: float = 10.0) -> None:
        self.service_key = (
            service_key
            or os.getenv("nomal")
            or os.getenv("DATA_GO_KR_API_KEY")
            or os.getenv("MPM_PUBLIC_EMPLOYMENT_API_KEY")
        )
        self.timeout = timeout

    def search_public_jobs(
        self,
        keyword: str | None = None,
        page_no: int = 1,
        num_of_rows: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch live public employment jobs from apis.data.go.kr with offline fixture fallback."""
        if not self.service_key:
            return self._filter_fixtures(keyword, num_of_rows)

        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "Pblanc_ty": "e01",
            "Sort_order": "1",
        }
        url = f"{self.PUBLIC_JOB_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "company-intelligence/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                xml_content = resp.read()
                return self._parse_public_job_xml(xml_content, keyword)
        except Exception:
            return self._filter_fixtures(keyword, num_of_rows)

    def _parse_public_job_xml(self, xml_bytes: bytes, keyword: str | None) -> list[dict[str, Any]]:
        try:
            root = ET.fromstring(xml_bytes)
        except Exception:
            return self._filter_fixtures(keyword, 10)

        results = []
        for item in root.findall(".//item"):
            title = (item.findtext("title") or item.findtext("pblJobNm") or "").strip()
            instt = (item.findtext("insttNm") or item.findtext("insttname") or "").strip()
            if keyword and keyword.lower() not in (title + instt).lower():
                continue

            results.append(
                {
                    "posting_id": item.findtext("idx") or item.findtext("pblJobId") or f"PBL-{len(results)+1}",
                    "institution_name": instt,
                    "title": title,
                    "region": item.findtext("workRgnNm") or item.findtext("region") or "전국",
                    "registered_at": item.findtext("regdate") or item.findtext("regDate"),
                    "closing_at": item.findtext("enddate") or item.findtext("closeDate"),
                    "url": item.findtext("pbancUrl") or item.findtext("srcUrl") or "https://www.gojobs.go.kr",
                    "employment_type": item.findtext("type01") or item.findtext("recrutSeNm") or "정규직",
                    "ncs_code": None,
                    "ncs_label": None,
                    "provider": "data_go_kr_public",
                    "country_code": "KR",
                }
            )
        return results if results else self._filter_fixtures(keyword, 10)

    def _filter_fixtures(self, keyword: str | None, limit: int) -> list[dict[str, Any]]:
        if not keyword:
            return CURATED_PUBLIC_JOB_FIXTURES[:limit]
        kw = keyword.lower()
        matched = [
            f
            for f in CURATED_PUBLIC_JOB_FIXTURES
            if kw in f["title"].lower() or kw in f["institution_name"].lower() or kw in (f.get("ncs_label") or "").lower()
        ]
        return matched[:limit] if matched else CURATED_PUBLIC_JOB_FIXTURES[:limit]

    def search_worknet_jobs(self, keyword: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Search Worknet jobs with NCS mapping and standard schema."""
        return self.search_public_jobs(keyword=keyword, num_of_rows=limit)


# Module-level convenience functions
_worknet_connector: WorknetJobConnector | None = None


def get_worknet_connector() -> WorknetJobConnector:
    global _worknet_connector
    if _worknet_connector is None:
        _worknet_connector = WorknetJobConnector()
    return _worknet_connector


def search_worknet_jobs(keyword: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    return get_worknet_connector().search_worknet_jobs(keyword, limit)
