"""Canonical responsibility owner; migrated from src/company_intel/connectors/koneps.py."""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
import os
import math
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class CanonicalProcurementRecord:
    """Universal canonical schema for cross-national public procurement (KR/US/EU-CZ)."""

    procurement_id: str
    source_system: str
    country: str
    buyer_name: str
    title: str
    contract_amount: float | None
    currency: str
    notice_date: str
    winner_name: str | None
    industry_category: str | None
    url: str
    source_kind: str = "observed"
    amount_kind: str = "budget_or_estimate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CURATED_KONEPS_FIXTURES: list[dict[str, Any]] = [
    {
        "procurement_id": "KR-KONEPS-2026-001",
        "source_system": "KONEPS",
        "country": "KR",
        "buyer_name": "한국지능정보사회진흥원",
        "title": "2026년 차세대 국가 AI 초거대 모델 기반 디지털 공공혁신 플랫폼 구축",
        "contract_amount": 45000000000.0,
        "currency": "KRW",
        "notice_date": "2026-09-15",
        "winner_name": "네이버클라우드",
        "industry_category": "소프트웨어 개발 및 정보인프라",
        "url": "https://www.g2b.go.kr",
    },
    {
        "procurement_id": "KR-KONEPS-2026-002",
        "source_system": "KONEPS",
        "country": "KR",
        "buyer_name": "한국전력공사",
        "title": "차세대 지능형 배전망(ADMS) 통신 연계 및 IT 보안 통합 소프트웨어 용역",
        "contract_amount": 18500000000.0,
        "currency": "KRW",
        "notice_date": "2026-08-20",
        "winner_name": "삼성SDS",
        "industry_category": "전력 IT 시스템 용역",
        "url": "https://www.g2b.go.kr",
    },
    {
        "procurement_id": "KR-KONEPS-2026-003",
        "source_system": "KONEPS",
        "country": "KR",
        "buyer_name": "국민건강보험공단",
        "title": "차세대 빅데이터 클라우드 정보보안 위협 탐지 및 침해대응 체계 고도화",
        "contract_amount": 9200000000.0,
        "currency": "KRW",
        "notice_date": "2026-10-01",
        "winner_name": "안랩",
        "industry_category": "정보보안 및 침해대응",
        "url": "https://www.g2b.go.kr",
    },
    {
        "procurement_id": "KR-KONEPS-2026-004",
        "source_system": "KONEPS",
        "country": "KR",
        "buyer_name": "한국도로공사",
        "title": "C-ITS 차세대 지능형 고속도로 AI 영상인식 및 차량 통신 인프라 공급",
        "contract_amount": 12000000000.0,
        "currency": "KRW",
        "notice_date": "2026-07-10",
        "winner_name": "현대오토에버",
        "industry_category": "지능형 교통 시스템",
        "url": "https://www.g2b.go.kr",
    },
    {
        "procurement_id": "KR-KONEPS-2026-005",
        "source_system": "KONEPS",
        "country": "KR",
        "buyer_name": "우정사업정보센터",
        "title": "우체국 차세대 종합금융시스템 클라우드 네이티브 MSA 아키텍처 전환 사업",
        "contract_amount": 32000000000.0,
        "currency": "KRW",
        "notice_date": "2026-06-15",
        "winner_name": "LG CNS",
        "industry_category": "금융 클라우드 IT 구축",
        "url": "https://www.g2b.go.kr",
    },
]


class KONEPSProcurementConnector:
    """Connects to Korean Public Data Portal KONEPS (조달청 나라장터 입찰/낙찰) Open API."""

    KONEPS_BID_URL = "http://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoServcPPSSrch"

    def __init__(
        self,
        service_key: str | None = None,
        timeout: float = 10.0,
        *,
        demo: bool = False,
    ) -> None:
        self.service_key = (
            service_key
            or os.getenv("KONEPS_API_KEY")
            or os.getenv("DATA_GO_KR_API_KEY")
            or os.getenv("nomal")
        )
        self.timeout = timeout
        self.demo = demo

    def search_procurements(
        self, query: str | None = None, page_no: int = 1, num_of_rows: int = 10
    ) -> list[CanonicalProcurementRecord]:
        """Query one page. Only explicit demo mode reads synthetic fixtures."""
        if page_no < 1 or not 1 <= num_of_rows <= 1000:
            raise ValueError("invalid procurement page bounds")
        if self.demo:
            return self._filter_fixtures(query, num_of_rows)
        if not self.service_key:
            raise ValueError("KONEPS service key required")
        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "type": "xml",
        }
        if query:
            params["bidNtceNm"] = query
        url = f"{self.KONEPS_BID_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "company-intelligence/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                xml_content = resp.read()
                parsed = self._parse_koneps_xml(xml_content)
                return parsed[:num_of_rows]
        except (OSError, ET.ParseError) as error:
            raise RuntimeError("KONEPS request failed; no fixture fallback") from error

    def _parse_koneps_xml(self, xml_bytes: bytes) -> list[CanonicalProcurementRecord]:
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as error:
            raise ValueError("invalid KONEPS response XML") from error
        code = root.findtext(".//resultCode")
        if code not in {"00", "0", "000"}:
            raise ValueError("KONEPS response status: " + str(code))
        records = []
        for item in root.findall(".//item"):
            bid_no = item.findtext("bidNtceNo", "")
            bid_seq = item.findtext("bidNtceOrd", "00")
            proc_id = f"KR-KONEPS-{bid_no}-{bid_seq}" if bid_no else "KR-KONEPS-UNKNOWN"
            if not bid_no:
                raise ValueError("KONEPS response missing bid identity")
            buyer = (
                item.findtext("dminsttNm")
                or item.findtext("orderInsttNm")
                or "대한민국 공공기관"
            )
            title = item.findtext("bidNtceNm", "공공조달 입찰공고")
            amt_str = item.findtext("asignBdgtAmt") or item.findtext("presmptPrce")
            try:
                contract_amount = float(amt_str.replace(",", "")) if amt_str else None
            except ValueError as error:
                raise ValueError("invalid KONEPS amount") from error
            if contract_amount is not None and (
                not math.isfinite(contract_amount) or contract_amount < 0
            ):
                raise ValueError("invalid KONEPS amount")
            notice_date = (item.findtext("bidNtceDt") or "")[:10]
            winner = (
                item.findtext("opengCorpNm") or item.findtext("sucsfCorpNm") or None
            )
            category = item.findtext("indstrytyNm") or "공공용역"
            url = item.findtext("bidNtceDtlUrl") or "https://www.g2b.go.kr"
            records.append(
                CanonicalProcurementRecord(
                    procurement_id=proc_id,
                    source_system="KONEPS",
                    country="KR",
                    buyer_name=buyer,
                    title=title,
                    contract_amount=contract_amount,
                    currency="KRW",
                    notice_date=notice_date,
                    winner_name=winner,
                    industry_category=category,
                    url=url,
                )
            )
        return records

    def _filter_fixtures(
        self, query: str | None, limit: int
    ) -> list[CanonicalProcurementRecord]:
        items = CURATED_KONEPS_FIXTURES
        if query:
            q_lower = query.lower()
            items = [
                f
                for f in items
                if q_lower in f["title"].lower()
                or q_lower in f["buyer_name"].lower()
                or (f["winner_name"] and q_lower in f["winner_name"].lower())
                or (
                    f["industry_category"] and q_lower in f["industry_category"].lower()
                )
            ]
        selected = items[:limit]
        return [
            CanonicalProcurementRecord(**item, source_kind="fixture")
            for item in selected
        ]
