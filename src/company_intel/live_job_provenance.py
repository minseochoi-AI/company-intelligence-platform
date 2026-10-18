"""Live Job Provenance Verifier and freshness analyzer.
Implements Decision JP-D02 for decision campaign cil-live-job-provenance-20261018.
"""
from __future__ import annotations

import datetime
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .classification import CanonicalJobRecord


class JobProvenanceVerifier:
    """Verifies job listing URL validity, deadline-based freshness, and generates Excel formulas."""

    # Default reference date if none provided: 2026-10-18 (or current date)
    DEFAULT_REFERENCE_DATE = datetime.date(2026, 10, 18)

    @staticmethod
    def validate_url_syntax(url: str | None) -> bool:
        """Check if URL has valid HTTP/HTTPS scheme and non-empty network location."""
        if not url or not isinstance(url, str):
            return False
        url_str = url.strip()
        if not url_str or url_str.lower() in ("none", "nan", "null"):
            return False
        try:
            parsed = urllib.parse.urlparse(url_str)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    @classmethod
    def parse_deadline(cls, deadline_str: str | None) -> datetime.date | None:
        """Parse various cross-national deadline string formats into datetime.date."""
        if not deadline_str or not isinstance(deadline_str, str):
            return None

        clean_str = deadline_str.strip()
        if not clean_str or clean_str.lower() in ("none", "null", "상시", "채용시", "상시채용", "9999-12-31"):
            return None

        if "~" in clean_str:
            clean_str = clean_str.split("~")[-1].strip()

        # Format 1: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS
        match_iso = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", clean_str)
        if match_iso:
            try:
                year, month, day = map(int, match_iso.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass

        # Format 1b: 2-digit year YY.MM.DD (e.g. 26.09.27 -> 2026-09-27)
        match_yy = re.search(r"\b(\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b", clean_str)
        if match_yy:
            try:
                yy, month, day = map(int, match_yy.groups())
                return datetime.date(2000 + yy, month, day)
            except ValueError:
                pass

        # Format 2: YYYYMMDD
        match_dense = re.search(r"\b(\d{4})(\d{2})(\d{2})\b", clean_str)
        if match_dense:
            try:
                year, month, day = map(int, match_dense.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass

        # Format 3: DD.MM.YYYY (European / Czech format)
        match_eu = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", clean_str)
        if match_eu:
            try:
                day, month, year = map(int, match_eu.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass

        return None

    @classmethod
    def compute_freshness(
        cls,
        deadline_str: str | None,
        reference_date: datetime.date | None = None,
    ) -> str:
        """Classify job posting freshness against reference date.
        
        Returns:
            - "CLOSED": Deadline has passed prior to reference date
            - "APPROACHING_DEADLINE": Within 7 days of deadline
            - "LIVE_ACTIVE": More than 7 days remaining or continuous/open-ended
        """
        ref = reference_date or cls.DEFAULT_REFERENCE_DATE
        dt = cls.parse_deadline(deadline_str)
        if dt is None:
            return "LIVE_ACTIVE"  # Open-ended, continuous, or unstated

        diff_days = (dt - ref).days
        if diff_days < 0:
            return "CLOSED"
        elif diff_days <= 7:
            return "APPROACHING_DEADLINE"
        else:
            return "LIVE_ACTIVE"

    @classmethod
    def generate_clickable_hyperlink(
        cls,
        target_col: str,
        row_idx: int,
        label: str = "공고 확인 ↗",
    ) -> str:
        """Generate Excel =HYPERLINK(col_row, label) formula string."""
        return f'=HYPERLINK({target_col}{row_idx}, "{label}")'

    @classmethod
    def verify_url_live(cls, url: str, timeout: float = 3.0) -> dict[str, Any]:
        """Perform live network probing via HTTP HEAD request (Local-first / optional)."""
        if not cls.validate_url_syntax(url):
            return {"status": "INVALID_SYNTAX", "reachable": False, "http_code": None}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CompanyIntel/0.1 LiveProvenanceVerifier",
            "Accept": "*/*",
        }
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return {
                    "status": "REACHABLE",
                    "reachable": True,
                    "http_code": response.status,
                }
        except urllib.error.HTTPError as e:
            if e.code == 405:
                # HEAD method not allowed, retry with shallow GET
                try:
                    get_req = urllib.request.Request(url, headers=headers, method="GET")
                    with urllib.request.urlopen(get_req, timeout=timeout) as get_resp:
                        return {
                            "status": "REACHABLE",
                            "reachable": True,
                            "http_code": get_resp.status,
                        }
                except Exception as inner_e:
                    return {
                        "status": f"HTTP_{getattr(inner_e, 'code', 'ERROR')}",
                        "reachable": False,
                        "http_code": getattr(inner_e, "code", None),
                        "error": str(inner_e),
                    }
            return {
                "status": f"HTTP_{e.code}",
                "reachable": False,
                "http_code": e.code,
            }
        except Exception as e:
            return {
                "status": "NETWORK_UNREACHABLE",
                "reachable": False,
                "http_code": None,
                "error": str(e),
            }

    @classmethod
    def verify_record(
        cls,
        record: CanonicalJobRecord,
        verify_live: bool = False,
        reference_date: datetime.date | None = None,
        row_idx: int = 2,
        target_url_col: str = "O",
    ) -> dict[str, Any]:
        """Inspect and augment a single CanonicalJobRecord with verification metadata."""
        url_valid = cls.validate_url_syntax(record.job_url)
        freshness = cls.compute_freshness(record.deadline, reference_date=reference_date)
        hyperlink_formula = cls.generate_clickable_hyperlink(target_url_col, row_idx)

        live_result = None
        if verify_live and url_valid:
            live_result = cls.verify_url_live(record.job_url)

        return {
            "url_valid": url_valid,
            "freshness": freshness,
            "hyperlink_formula": hyperlink_formula,
            "live_status": live_result,
            "parsed_deadline": str(cls.parse_deadline(record.deadline) or record.deadline or ""),
        }
