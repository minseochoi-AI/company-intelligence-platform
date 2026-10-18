"""Tests for ClusterSignature, JobSchemaContract, KeyAlignmentError, and CanonicalJobRecord factories.
Validates Decision JP-D01 in decision campaign cil-live-job-provenance-20261018.
"""
from __future__ import annotations

import pytest

from company_intel.classification import (
    CanonicalJobRecord,
    ClusterSignature,
    JobSchemaContract,
    KeyAlignmentError,
    from_cz_mpsv_job_record,
    from_kr_public_job_record,
    from_sk_upsvar_record,
    from_us_usajobs_record,
)


def test_cluster_signature_key_and_matches():
    sig = ClusterSignature(
        region="KR",
        sector="PUBLIC_INSTITUTION",
        tier="QUASI_GOV",
        contract="REGULAR",
        workplace="ONSITE",
    )
    assert sig.key == "KR:PUBLIC_INSTITUTION:QUASI_GOV:REGULAR:ONSITE"

    # Wildcard matches
    pattern = ClusterSignature.parse("KR:PUBLIC_INSTITUTION:ALL:ALL:ALL")
    assert pattern.matches(sig)

    different_country = ClusterSignature.parse("CZ:PUBLIC_INSTITUTION:ALL:ALL:ALL")
    assert not different_country.matches(sig)


def test_job_schema_contract_alias_resolution():
    raw_kr = {
        "pblJobId": "KR-1001",
        "pbancUrl": "https://job.alio.go.kr/recruitview.do?idx=1001",
        "insttNm": "한국전력공사",
        "pblJobNm": "정보보안 및 IT 기획 신입 채용",
    }
    clean = JobSchemaContract.validate_and_normalize(raw_kr, provider="JOB_ALIO")
    assert clean["job_id"] == "KR-1001"
    assert clean["job_url"] == "https://job.alio.go.kr/recruitview.do?idx=1001"
    assert clean["employer_name"] == "한국전력공사"
    assert clean["job_title"] == "정보보안 및 IT 기획 신입 채용"
    assert clean["_job_id_source_alias"] == "pblJobId"


def test_job_schema_contract_missing_raises_key_alignment_error():
    broken_job = {
        "job_id": "CZ-999",
        "job_title": "IT Specialist",
        # Missing employer_name and job_url
    }
    with pytest.raises(KeyAlignmentError) as exc_info:
        JobSchemaContract.validate_and_normalize(broken_job, provider="CZ_MPSV")
    assert "Job schema contract violation" in str(exc_info.value)
    assert "employer_name" in str(exc_info.value)


def test_czech_mpsv_portal_url_synthesis_fallback():
    # Only portal_id given, no job_url or posting_url
    cz_raw = {
        "portal_id": "28192300721",
        "employer_name": "Ministerstvo vnitra",
        "job_title": "Správce sítě IT",
        "employer_ico": "00007064",
    }
    clean = JobSchemaContract.validate_and_normalize(cz_raw, provider="CZ_MPSV")
    assert clean["job_url"] == "https://www.uradprace.cz/web/cz/volna-mista-v-cr#/volna-mista-detail/28192300721"
    assert clean["_job_url_source_alias"] == "synthesized:portal_id"


def test_from_cz_mpsv_job_record_factory():
    raw_cz = {
        "portal_id": "301920001",
        "job_title": "IT administrátor / systémový inženýr",
        "employer_name": "Státní úřad pro jadernou bezpečnost",
        "employer_ico": "49629167",
        "minimum_education_code": "VzdelaniDetailniKategorie/VysokoskolskeMagisterske",
        "cz_isco": "CzIsco/25121",
        "statni_sprava": "true",
        "salary_from_czk": "42000",
        "salary_to_czk": "58000",
        "expiry_date": "2026-11-30",
        "job_description_cz": "Zajištění provozu a správy IT infrastruktury SÚJB",
    }
    record = from_cz_mpsv_job_record(raw_cz)
    assert isinstance(record, CanonicalJobRecord)
    assert record.job_id == "301920001"
    assert record.job_url == "https://www.uradprace.cz/web/cz/volna-mista-v-cr#/volna-mista-detail/301920001"
    assert record.employer_name == "Státní úřad pro jadernou bezpečnost"
    assert record.cluster_signature.region == "CZ"
    assert record.cluster_signature.sector == "PUBLIC_INSTITUTION"
    assert record.education_level == "VysokoskolskeMagisterske"
    assert record.occupation_code == "25121"
    assert record.deadline == "2026-11-30"


def test_from_kr_public_job_record_factory():
    raw_kr = {
        "idx": "2026-0812",
        "url": "https://job.alio.go.kr/recruitview.do?idx=2026-0812",
        "insttname": "한국원자력안전기술원",
        "title": "원자력 안전정보망 사이버보안 전문연구원 채용",
        "instt_se": "p02",  # QUASI_GOV
        "pblanc_ty": "e01",  # REGULAR
        "closeDate": "2026-10-31",
        "education": "대졸 이상(석박사 우대)",
    }
    record = from_kr_public_job_record(raw_kr)
    assert isinstance(record, CanonicalJobRecord)
    assert record.job_id == "2026-0812"
    assert record.employer_name == "한국원자력안전기술원"
    assert record.cluster_signature.region == "KR"
    assert record.cluster_signature.sector == "PUBLIC_INSTITUTION"
    assert record.cluster_signature.tier == "QUASI_GOV"
    assert record.cluster_signature.contract == "REGULAR"


def test_from_sk_upsvar_record_factory():
    raw_sk = {
        "job_id": "SK-55102",
        "posting_url": "https://www.sluzbyzamestnanosti.gov.sk/volne-miesto/55102",
        "employer_name": "Jadrová a vyraďovacia spoločnosť, a.s. (JAVYS)",
        "job_title": "Inžinier kybernetickej bezpečnosti",
        "legal_form": "Štátny podnik",
        "edu": "Vysokoškolské II. stupňa",
    }
    record = from_sk_upsvar_record(raw_sk)
    assert record.cluster_signature.region == "SK"
    assert record.cluster_signature.sector == "STATE_OWNED"
    assert record.job_url == "https://www.sluzbyzamestnanosti.gov.sk/volne-miesto/55102"


def test_from_us_usajobs_record_factory():
    raw_us = {
        "PositionID": "USA-78910",
        "PositionURI": "https://www.usajobs.gov/job/78910",
        "OrganizationName": "Department of Energy",
        "PositionTitle": "IT Cybersecurity Specialist (INFOSEC)",
        "PositionOfferingType": "Permanent",
        "PositionRemuneration": [{"MinimumRange": 95000, "MaximumRange": 145000}],
    }
    record = from_us_usajobs_record(raw_us)
    assert record.cluster_signature.region == "US"
    assert record.cluster_signature.sector == "GOVERNMENT"
    assert record.cluster_signature.tier == "FEDERAL_GS"
    assert record.salary_min == 95000


def test_dynamic_job_schema_registry():
    from company_intel.classification import DynamicJobSchemaRegistry

    # Register a dynamic attribute with a validator
    JobSchemaContract.register_dynamic_attribute(
        name="weekly_hours",
        aliases=("weekly_hours", "tydenni_uvazek"),
        data_type=float,
        required=False,
        default=40.0,
        validator=lambda x: 0 < x <= 60,
        description="Weekly working hours",
    )

    registered = JobSchemaContract.list_dynamic_attributes()
    assert any(r["canonical_name"] == "weekly_hours" for r in registered)

    raw_cz = {
        "portal_id": "CZ-12345",
        "job_url": "https://example.com/job/1",
        "employer_name": "Test Agency",
        "job_title": "Network Admin",
        "weekly_hours": "38.5",
    }
    clean = JobSchemaContract.validate_and_normalize(raw_cz, provider="CZ_MPSV")
    assert clean["weekly_hours"] == 38.5

    # Test constraint violation
    raw_invalid = {
        "portal_id": "CZ-12345",
        "job_url": "https://example.com/job/1",
        "employer_name": "Test Agency",
        "job_title": "Network Admin",
        "weekly_hours": "120.0",  # Fails constraint validator
    }
    with pytest.raises(KeyAlignmentError) as exc_info:
        JobSchemaContract.validate_and_normalize(raw_invalid, provider="CZ_MPSV")
    assert "Constraint check failed for 'weekly_hours'" in str(exc_info.value)

    # Clean up registry
    DynamicJobSchemaRegistry._registry.clear()
