"""Unit tests for JobProvenanceVerifier.
Validates Decision JP-D02 for decision campaign cil-live-job-provenance-20261018.
"""
from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import pytest

from company_intel.classification import CanonicalJobRecord, ClusterSignature
from company_intel.live_job_provenance import JobProvenanceVerifier


def test_validate_url_syntax():
    # Valid URLs
    assert JobProvenanceVerifier.validate_url_syntax("https://www.uradprace.cz/web/cz/volna-mista-detail/12345")
    assert JobProvenanceVerifier.validate_url_syntax("http://job.alio.go.kr/recruitview.do?idx=101")
    assert JobProvenanceVerifier.validate_url_syntax("https://www.usajobs.gov/job/78910")

    # Invalid URLs
    assert not JobProvenanceVerifier.validate_url_syntax(None)
    assert not JobProvenanceVerifier.validate_url_syntax("")
    assert not JobProvenanceVerifier.validate_url_syntax("none")
    assert not JobProvenanceVerifier.validate_url_syntax("ftp://invalid-scheme.com")
    assert not JobProvenanceVerifier.validate_url_syntax("just_plain_text")


def test_parse_deadline_and_compute_freshness():
    ref_date = datetime.date(2026, 10, 18)

    # Format 1: ISO YYYY-MM-DD
    assert JobProvenanceVerifier.parse_deadline("2026-10-20") == datetime.date(2026, 10, 20)
    # Format 2: European DD.MM.YYYY
    assert JobProvenanceVerifier.parse_deadline("31.12.2026") == datetime.date(2026, 12, 31)
    # Format 3: Dense YYYYMMDD
    assert JobProvenanceVerifier.parse_deadline("20261025") == datetime.date(2026, 10, 25)

    # Freshness evaluations
    # 1. Closed (in past)
    assert JobProvenanceVerifier.compute_freshness("2026-10-01", reference_date=ref_date) == "CLOSED"
    # 2. Approaching deadline (within 7 days: Oct 18 to Oct 25)
    assert JobProvenanceVerifier.compute_freshness("2026-10-22", reference_date=ref_date) == "APPROACHING_DEADLINE"
    assert JobProvenanceVerifier.compute_freshness("2026-10-25", reference_date=ref_date) == "APPROACHING_DEADLINE"
    # 3. Live Active (> 7 days)
    assert JobProvenanceVerifier.compute_freshness("2026-11-15", reference_date=ref_date) == "LIVE_ACTIVE"
    # 4. Open-ended / Empty / Unspecified
    assert JobProvenanceVerifier.compute_freshness("", reference_date=ref_date) == "LIVE_ACTIVE"
    assert JobProvenanceVerifier.compute_freshness("상시채용", reference_date=ref_date) == "LIVE_ACTIVE"


def test_generate_clickable_hyperlink():
    formula = JobProvenanceVerifier.generate_clickable_hyperlink("O", 15)
    assert formula == '=HYPERLINK(O15, "공고 확인 ↗")'


def test_verify_record_end_to_end():
    sig = ClusterSignature(region="KR", sector="STATE_OWNED", tier="MARKET_SOE", contract="REGULAR", workplace="ONSITE")
    record = CanonicalJobRecord(
        job_id="KR-2026-001",
        job_url="https://job.alio.go.kr/recruitview.do?idx=2026-001",
        employer_name="한국가스공사",
        org_id="KOGAS",
        job_title="IT 인프라 및 클라우드 엔지니어",
        occupation_code="020101",
        education_level="학사 이상",
        contract_type="정규직",
        salary_min="45000000",
        salary_max="55000000",
        currency="KRW",
        location="대구광역시",
        deadline="2026-11-10",
        description="IT 인프라 및 클라우드 유지보수",
        source_api="JOB_ALIO",
        cluster_signature=sig,
    )

    ref_date = datetime.date(2026, 10, 18)
    verified = JobProvenanceVerifier.verify_record(record, verify_live=False, reference_date=ref_date, row_idx=5)

    assert verified["url_valid"] is True
    assert verified["freshness"] == "LIVE_ACTIVE"
    assert verified["hyperlink_formula"] == '=HYPERLINK(O5, "공고 확인 ↗")'
    assert verified["parsed_deadline"] == "2026-11-10"


def test_verify_url_live_mocked():
    # Test successful 200 response
    mock_cm = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_cm.__enter__.return_value = mock_resp
    with patch("urllib.request.urlopen", return_value=mock_cm):
        res = JobProvenanceVerifier.verify_url_live("https://example.com/job/1", timeout=1.0)
        assert res["reachable"] is True
        assert res["http_code"] == 200
        assert res["status"] == "REACHABLE"
