from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from typing import Any

from ..models import Probe
from .base import compact, json_payload, to_number


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


def _work24(body: bytes, _: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    jobs = []
    for wanted in root.findall(".//wanted"):
        jobs.append(
            {
                "wanted_auth_no": wanted.findtext("wantedAuthNo"),
                "company": wanted.findtext("company"),
                "title": wanted.findtext("title"),
                "sal": wanted.findtext("sal"),
                "region": wanted.findtext("region"),
                "close_date": wanted.findtext("closeDt"),
                "detail_url": wanted.findtext("wantedInfoUrl"),
            }
        )
    return {
        "total": to_number(root.findtext(".//total")),
        "start_page": root.findtext(".//startPage"),
        "display": root.findtext(".//display"),
        "jobs": jobs,
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
        "meta": compact(data.get("Meta Data", {})),
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
                id="work24_job_search",
                provider="work24",
                category="company_jobs",
                regions=["KR"],
                method="GET",
                url="https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do",
                params={
                    "authKey": os.getenv("WORK24_API_KEY", ""),
                    "callTp": "L",
                    "returnType": "XML",
                    "startPage": 1,
                    "display": 10,
                },
                secret_env="WORK24_API_KEY",
                expected_format="xml",
                required_paths=["jobs.0.wanted_auth_no", "jobs.0.company", "jobs.0.title"],
                normalizer=_work24,
                capabilities=["kr_job_postings", "occupation_demand", "region_demand"],
                limitation="Job postings measure hiring demand, not completed hires; periodic snapshots are required.",
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
