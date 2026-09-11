from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from typing import Any

from ..models import Probe
from .base import json_payload, preserve_payload, to_number


def _fred(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    rows = data.get("observations", [])
    return {
        "series_id": "FEDFUNDS",
        "realtime_start": data.get("realtime_start"),
        "realtime_end": data.get("realtime_end"),
        "count": data.get("count"),
        "observations": [
            {
                "observation_date": row.get("date"),
                "available_at": row.get("realtime_start"),
                "revision_end": row.get("realtime_end"),
                "value": to_number(row.get("value")),
                "unit": "percent",
            }
            for row in rows
        ],
    }


def _bea(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body).get("BEAAPI", {})
    results = data.get("Results", {})
    datasets = results.get("Dataset", [])
    return {
        "dataset_count": len(datasets),
        "datasets": [
            {"name": row.get("DatasetName"), "description": row.get("DatasetDescription")} for row in datasets
        ],
        "error": results.get("Error"),
    }


def _dart(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    rows = data.get("list", [])
    normalized = []
    for row in rows:
        normalized.append(
            {
                "corp_code": row.get("corp_code"),
                "report_year": row.get("bsns_year"),
                "report_code": row.get("reprt_code"),
                "statement": row.get("sj_div"),
                "account_id": row.get("account_id"),
                "account_name": row.get("account_nm"),
                "account_detail": row.get("account_detail"),
                "order": row.get("ord"),
                "current_amount": to_number(row.get("thstrm_amount")),
                "current_cumulative_amount": to_number(row.get("thstrm_add_amount")),
                "previous_amount": to_number(row.get("frmtrm_amount")),
                "currency": row.get("currency"),
                "receipt_no": row.get("rcept_no"),
            }
        )
    return {
        "status": data.get("status"),
        "message": data.get("message"),
        "row_count": len(rows),
        "financial_facts": normalized,
    }


def _ecos(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    root = data.get("StatisticSearch", {})
    rows = root.get("row", [])
    return {
        "result": root.get("RESULT") or data.get("RESULT"),
        "list_total_count": root.get("list_total_count"),
        "observations": [
            {
                "series_code": row.get("STAT_CODE"),
                "series_name": row.get("STAT_NAME"),
                "item_code": row.get("ITEM_CODE1"),
                "item_name": row.get("ITEM_NAME1"),
                "frequency": row.get("CYCLE"),
                "observation_date": row.get("TIME"),
                "value": to_number(row.get("DATA_VALUE")),
                "unit": row.get("UNIT_NAME"),
            }
            for row in rows
        ],
    }


def _alio_plus(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    if not isinstance(data, dict):
        return {"response_type": type(data).__name__, "records": preserve_payload(data)}
    return {
        "result_code": data.get("resultCode") or data.get("code") or data.get("status"),
        "result_message": data.get("resultMsg") or data.get("message"),
        "records": preserve_payload(data),
    }


def _public_employment(body: bytes, _: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    jobs = []
    for item in root.findall(".//item"):
        jobs.append(
            {
                "posting_id": item.findtext("idx"),
                "institution_name": item.findtext("insttname"),
                "title": item.findtext("title"),
                "institution_type": item.findtext("type01"),
                "posting_type": item.findtext("type02"),
                "registered_at": item.findtext("regdate"),
                "closing_at": item.findtext("enddate"),
            }
        )
    return {
        "result_code": root.findtext(".//resultCode"),
        "result_message": root.findtext(".//resultMsg"),
        "total": to_number(root.findtext(".//totalCount")),
        "jobs": jobs,
    }


def mpm_detail_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Return only explicit detail fields supplied by a separately authorized MPM detail response.

    The registered list endpoint is intentionally not treated as a requirement source.
    """
    detail = record.get("detail") if isinstance(record.get("detail"), dict) else record
    explicit = detail.get("requirements")
    return {
        "posting_id": detail.get("idx") or detail.get("posting_id"),
        "requirements": explicit if isinstance(explicit, list) else [],
        "availability": "available" if isinstance(explicit, list) else "requirement_unavailable",
    }


def alio_context_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """Return ALIO+ organisation context without inventing a legal identity.

    The live organisation response can leave ``apbaId`` blank and ``apbaNa``
    null while supplying its displayed institution name in ``title``.  A
    missing provider identifier must remain missing; ``title`` is useful for
    contextual grouping only and is not an entity-resolution key.
    """
    return {
        "institution_id": record.get("apbaId") or None,
        "institution_name": record.get("apbaNa") or record.get("title"),
        "institution_type": record.get("apbaTypeNa"),
        "identity_status": "source_identifier_present" if record.get("apbaId") else "context_only_no_source_identifier",
        "evidence_scope": "public_institution_context", "is_job_requirement": False,
    }


def _alpha(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    series_key = next((key for key in data if "Time Series" in key), None)
    series = data.get(series_key, {}) if series_key else {}
    prices = [
        {
            "symbol": data.get("Meta Data", {}).get("2. Symbol", "IBM"),
            "price_date": day,
            "open": to_number(values.get("1. open")),
            "high": to_number(values.get("2. high")),
            "low": to_number(values.get("3. low")),
            "close": to_number(values.get("4. close")),
            "volume": to_number(values.get("5. volume")),
            "adjustment": "raw",
        }
        for day, values in series.items()
    ]
    return {
        "meta": preserve_payload(data.get("Meta Data", {})),
        "row_count": len(prices),
        "prices": prices,
        "provider_note": data.get("Note") or data.get("Information") or data.get("Error Message"),
    }


def keyed_probes() -> list[Probe]:
    today = datetime.now(UTC).date()
    start = today - timedelta(days=370)
    dart_years = [str(today.year - 1), str(today.year - 2)]
    probes: list[Probe] = [
        Probe(
            id="fred_federal_funds_rate",
            provider="fred",
            category="macro_rate",
            regions=["US"],
            method="GET",
            url="https://api.stlouisfed.org/fred/series/observations",
            params={
                "series_id": "FEDFUNDS",
                "file_type": "json",
                "observation_start": start.isoformat(),
                "api_key": os.getenv("FRED_API_KEY", ""),
            },
            secret_env="FRED_API_KEY",
            expected_format="json",
            required_paths=["observations.0.date", "observations.0.value"],
            normalizer=_fred,
            capabilities=["us_interest_rate", "macro_timeseries", "point_in_time_vintage"],
            quota_note="Registered-key service; cache observations and use ALFRED/vintages for revisions.",
        ),
        Probe(
            id="bea_dataset_catalog",
            provider="bea",
            category="macro_industry",
            regions=["US"],
            method="GET",
            url="https://apps.bea.gov/api/data",
            params={
                "UserID": os.getenv("BEA_API_KEY", ""),
                "method": "GETDATASETLIST",
                "ResultFormat": "JSON",
            },
            secret_env="BEA_API_KEY",
            expected_format="json",
            required_paths=["BEAAPI.Results.Dataset.0.DatasetName"],
            normalizer=_bea,
            capabilities=["dataset_discovery", "gdp", "industry_value_added", "input_output"],
            quota_note="Official guide: 100 requests/minute, 100 MB/minute, 30 errors/minute.",
        ),
    ]
    # Annual CFS first; the validator can retry the prior year when DART reports no data.
    probes.append(
        Probe(
            id="opendart_samsung_financials",
            provider="opendart",
            category="financial_facts",
            regions=["KR"],
            method="GET",
            url="https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json",
            params={
                "crtfc_key": os.getenv("OPENDART_API_KEY", ""),
                "corp_code": "00126380",
                "bsns_year": dart_years[0],
                "reprt_code": "11011",
                "fs_div": "CFS",
            },
            secret_env="OPENDART_API_KEY",
            expected_format="json",
            required_paths=["status", "list.0.account_nm", "list.0.thstrm_amount"],
            normalizer=_dart,
            capabilities=["kr_financial_statements", "cashflow", "margins", "filing_evidence"],
            quota_note="Official guide reports status 020 generally after 20,000+ requests; account limits can differ.",
            limitation=f"Probe targets Samsung Electronics annual consolidated statement for {dart_years[0]}.",
        )
    )
    probes.extend(
        [
            Probe(
                id="ecos_korea_base_rate",
                provider="ecos",
                category="macro_rate",
                regions=["KR"],
                method="GET",
                url=(
                    "https://ecos.bok.or.kr/api/StatisticSearch/"
                    f"{os.getenv('ECOS_API_KEY', '')}/json/kr/1/1000/722Y001/D/"
                    f"{start.strftime('%Y%m%d')}/{today.strftime('%Y%m%d')}/0101000"
                ),
                secret_env="ECOS_API_KEY",
                expected_format="json",
                required_paths=["StatisticSearch.row.0.TIME", "StatisticSearch.row.0.DATA_VALUE"],
                normalizer=_ecos,
                capabilities=["kr_policy_rate", "kr_macro_timeseries"],
            ),
            Probe(
                id="alioplus_facility",
                provider="alioplus",
                category="public_facilities",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/facility",
                form_body={"X-API-AUTH-KEY": os.getenv("ALIO_PLUS_FACILITY_API_KEY", ""), "pageSize": 1},
                secret_env="ALIO_PLUS_FACILITY_API_KEY",
                expected_format="json",
                required_paths=["0.facltNa", "0.apbaNa"],
                normalizer=_alio_plus,
                capabilities=["kr_public_facilities", "public_institution_service_signal"],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="alioplus_event",
                provider="alioplus",
                category="public_events",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/event",
                form_body={"X-API-AUTH-KEY": os.getenv("ALIO_PLUS_EVENT_API_KEY", ""), "pageSize": 1},
                secret_env="ALIO_PLUS_EVENT_API_KEY",
                expected_format="json",
                required_paths=["0.evtNa", "0.apbaNa"],
                normalizer=_alio_plus,
                capabilities=["kr_public_events", "public_institution_activity_signal"],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="alioplus_business",
                provider="alioplus",
                category="public_businesses",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/business",
                form_body={"X-API-AUTH-KEY": os.getenv("ALIO_PLUS_BUSINESS_API_KEY", ""), "pageSize": 1},
                secret_env="ALIO_PLUS_BUSINESS_API_KEY",
                expected_format="json",
                required_paths=["0.bsnNa", "0.apbaNa"],
                normalizer=_alio_plus,
                capabilities=["kr_public_businesses", "public_institution_service_signal"],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="alioplus_organization",
                provider="alioplus",
                category="public_institutions",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/apba",
                form_body={"X-API-AUTH-KEY": os.getenv("ALIO_PLUS_ORGANIZATION_API_KEY", ""), "pageSize": 1},
                secret_env="ALIO_PLUS_ORGANIZATION_API_KEY",
                expected_format="json",
                # In the live response, ``title`` is the populated display
                # name while apbaId/apbaNa may be blank/null.  Do not validate
                # an optional value as a required legal identifier.
                required_paths=["0.title", "0.apbaTypeNa"],
                normalizer=_alio_plus,
                capabilities=["kr_public_institution_name", "public_institution_businesses"],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="mpm_public_employment_list",
                provider="mpm_public_employment",
                category="public_job_postings",
                regions=["KR"],
                method="GET",
                url="https://apis.data.go.kr/1760000/PblJobService/getList",
                params={
                    "serviceKey": os.getenv("MPM_PUBLIC_EMPLOYMENT_API_KEY", ""),
                    "pageNo": 1,
                    "numOfRows": 1,
                    "Pblanc_ty": "e01",
                    "Instt_se": "g01",
                    "Sort_order": "1",
                },
                secret_env="MPM_PUBLIC_EMPLOYMENT_API_KEY",
                expected_format="xml",
                required_paths=["result_code"],
                normalizer=_public_employment,
                capabilities=["kr_public_job_postings", "civil_service_job_postings", "public_institution_job_postings"],
                limitation="The list API returns postings, not hires; save snapshots and retrieve details by posting ID only when needed.",
            ),
            Probe(
                id="alphavantage_ibm_daily",
                provider="alphavantage",
                category="market_price",
                regions=["US", "GLOBAL"],
                method="GET",
                url="https://www.alphavantage.co/query",
                params={
                    "function": "TIME_SERIES_DAILY",
                    "symbol": "IBM",
                    "outputsize": "compact",
                    "datatype": "json",
                    "apikey": os.getenv("ALPHAVANTAGE_API_KEY", ""),
                },
                secret_env="ALPHAVANTAGE_API_KEY",
                expected_format="json",
                required_paths=["Time Series (Daily)"],
                normalizer=_alpha,
                capabilities=["daily_ohlcv", "returns", "event_study"],
                quota_note="Official support: generally 25 requests/day for the ordinary free stock API tier.",
                limitation="Free compact daily output is suitable for validation/MVP, not global full-history collection.",
            ),
        ]
    )
    return probes
