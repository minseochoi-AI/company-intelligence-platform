"""Pure URL syntax and deadline classification; caller supplies reference date."""

from __future__ import annotations
import datetime
import re
import urllib.parse


class FreshnessPolicy:
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
        if not clean_str or clean_str.lower() in (
            "none",
            "null",
            "상시",
            "채용시",
            "상시채용",
            "9999-12-31",
        ):
            return None
        if "~" in clean_str:
            clean_str = clean_str.split("~")[-1].strip()
        match_iso = re.search("(\\d{4})[-/.](\\d{1,2})[-/.](\\d{1,2})", clean_str)
        if match_iso:
            try:
                year, month, day = map(int, match_iso.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass
        match_yy = re.search("\\b(\\d{2})[-/.](\\d{1,2})[-/.](\\d{1,2})\\b", clean_str)
        if match_yy:
            try:
                yy, month, day = map(int, match_yy.groups())
                return datetime.date(2000 + yy, month, day)
            except ValueError:
                pass
        match_dense = re.search("\\b(\\d{4})(\\d{2})(\\d{2})\\b", clean_str)
        if match_dense:
            try:
                year, month, day = map(int, match_dense.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass
        match_eu = re.search("(\\d{1,2})\\.(\\d{1,2})\\.(\\d{4})", clean_str)
        if match_eu:
            try:
                day, month, year = map(int, match_eu.groups())
                return datetime.date(year, month, day)
            except ValueError:
                pass
        return None

    @classmethod
    def compute_freshness(
        cls, deadline_str: str | None, reference_date: datetime.date | None = None
    ) -> str:
        """Classify job posting freshness against reference date.

        Returns:
            - "CLOSED": Deadline has passed prior to reference date
            - "APPROACHING_DEADLINE": Within 7 days of deadline
            - "LIVE_ACTIVE": More than 7 days remaining or continuous/open-ended
        """
        if reference_date is None:
            raise ValueError("reference_date required for reproducible freshness")
        ref = reference_date
        dt = cls.parse_deadline(deadline_str)
        if dt is None:
            return (
                "OPEN_ENDED_UNVERIFIED"
                if str(deadline_str or "").strip() in {"상시", "채용시", "상시채용"}
                else "UNKNOWN"
            )
        diff_days = (dt - ref).days
        if diff_days < 0:
            return "CLOSED"
        elif diff_days <= 7:
            return "APPROACHING_DEADLINE"
        else:
            return "LIVE_ACTIVE"
