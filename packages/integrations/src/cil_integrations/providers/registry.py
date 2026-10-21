"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py, src/company_intel/connectors/keyless.py, src/company_intel/connectors/registry.py."""

from __future__ import annotations
from cil_contracts.facts import Probe
from cil_domain.providers.contracts import evaluate_activation
from cil_domain.providers.parsing import get_path
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from cil_domain.providers.selection import ProviderCluster
from cil_domain.providers.selection import classify_operation
from cil_domain.providers.selection import select_operations
from cil_integrations.catalog.repository import load_source_catalog
from cil_integrations.providers.alio.adapter import _alio_plus
from cil_integrations.providers.alphavantage.market import _alpha
from cil_integrations.providers.bea.cubes import _bea
from cil_integrations.providers.ecos.adapter import _ecos
from cil_integrations.providers.fred.adapter import _fred
from cil_integrations.providers.greenhouse.jobs import _greenhouse
from cil_integrations.providers.hrdkorea.occupations import _ncs_duty_normalizer
from cil_integrations.providers.lever.jobs import _lever
from cil_integrations.providers.mpm.jobs import _public_employment
from cil_integrations.providers.opendart.filings import _dart
from cil_integrations.providers.parsing import _select
from cil_integrations.providers.worknet.occupations import _worknet_duty_normalizer
from cil_integrations.runtime.settings import Settings
from datetime import UTC, date, datetime
from datetime import UTC, datetime, timedelta
from typing import Any
from typing import Any, Callable, Mapping
from typing import Any, Iterable, Iterator, Mapping
import json
import os


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
            capabilities=[
                "us_interest_rate",
                "macro_timeseries",
                "point_in_time_vintage",
            ],
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
            capabilities=[
                "dataset_discovery",
                "gdp",
                "industry_value_added",
                "input_output",
            ],
            quota_note="Official guide: 100 requests/minute, 100 MB/minute, 30 errors/minute.",
        ),
    ]
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
            capabilities=[
                "kr_financial_statements",
                "cashflow",
                "margins",
                "filing_evidence",
            ],
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
                url=f"https://ecos.bok.or.kr/api/StatisticSearch/{os.getenv('ECOS_API_KEY', '')}/json/kr/1/1000/722Y001/D/{start.strftime('%Y%m%d')}/{today.strftime('%Y%m%d')}/0101000",
                secret_env="ECOS_API_KEY",
                expected_format="json",
                required_paths=[
                    "StatisticSearch.row.0.TIME",
                    "StatisticSearch.row.0.DATA_VALUE",
                ],
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
                form_body={
                    "X-API-AUTH-KEY": os.getenv("ALIO_PLUS_FACILITY_API_KEY", ""),
                    "pageSize": 1,
                },
                secret_env="ALIO_PLUS_FACILITY_API_KEY",
                expected_format="json",
                required_paths=["0.facltNa", "0.apbaNa"],
                normalizer=_alio_plus,
                capabilities=[
                    "kr_public_facilities",
                    "public_institution_service_signal",
                ],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="alioplus_event",
                provider="alioplus",
                category="public_events",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/event",
                form_body={
                    "X-API-AUTH-KEY": os.getenv("ALIO_PLUS_EVENT_API_KEY", ""),
                    "pageSize": 1,
                },
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
                form_body={
                    "X-API-AUTH-KEY": os.getenv("ALIO_PLUS_BUSINESS_API_KEY", ""),
                    "pageSize": 1,
                },
                secret_env="ALIO_PLUS_BUSINESS_API_KEY",
                expected_format="json",
                required_paths=["0.bsnNa", "0.apbaNa"],
                normalizer=_alio_plus,
                capabilities=[
                    "kr_public_businesses",
                    "public_institution_service_signal",
                ],
                limitation="ALIO Plus guide v1.6 specifies HTTP only; do not send personally identifying search terms.",
            ),
            Probe(
                id="alioplus_organization",
                provider="alioplus",
                category="public_institutions",
                regions=["KR"],
                method="POST",
                url="http://openapi.alioplus.go.kr/api/apba",
                form_body={
                    "X-API-AUTH-KEY": os.getenv("ALIO_PLUS_ORGANIZATION_API_KEY", ""),
                    "pageSize": 1,
                },
                secret_env="ALIO_PLUS_ORGANIZATION_API_KEY",
                expected_format="json",
                required_paths=["0.title", "0.apbaTypeNa"],
                normalizer=_alio_plus,
                capabilities=[
                    "kr_public_institution_name",
                    "public_institution_businesses",
                ],
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
                capabilities=[
                    "kr_public_job_postings",
                    "civil_service_job_postings",
                    "public_institution_job_postings",
                ],
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
            Probe(
                id="hrdkorea_ncs_duty",
                provider="hrdkorea",
                category="job_taxonomy",
                regions=["KR"],
                method="GET",
                url="http://apis.data.go.kr/B490001/ncs/getNcsJobInfo",
                params={
                    "serviceKey": os.getenv("HRDKOREA_NCS_API_KEY", ""),
                    "numOfRows": 100,
                    "pageNo": 1,
                },
                secret_env="HRDKOREA_NCS_API_KEY",
                expected_format="xml",
                required_paths=["items.0.ncs_sub_cd"],
                normalizer=_ncs_duty_normalizer,
                capabilities=[
                    "ncs_competency",
                    "job_standard",
                    "korean_occupational_taxonomy",
                ],
                quota_note="Public Data Portal (data.go.kr) daily quota: 10,000 calls/day.",
            ),
            Probe(
                id="worknet_job_duty_bridge",
                provider="worknet",
                category="job_taxonomy_bridge",
                regions=["KR"],
                method="GET",
                url="http://openapi.work.go.kr/opi/opi/opia/jobDutySrch.do",
                params={
                    "authKey": os.getenv("WORKNET_JOB_DUTY_API_KEY", ""),
                    "returnType": "XML",
                    "target": "jobDuty",
                },
                secret_env="WORKNET_JOB_DUTY_API_KEY",
                expected_format="xml",
                required_paths=["duties.0.ncs_cl_cd"],
                normalizer=_worknet_duty_normalizer,
                capabilities=["keco_to_ncs_bridge", "worknet_competency_mapping"],
                quota_note="Worknet Open API: 10,000 calls/day.",
            ),
        ]
    )
    return probes


def keyless_probes(sec_user_agent: str) -> list[Probe]:
    today = datetime.now(UTC).date()
    month_start = today.replace(day=1)
    year_start = date(today.year, 1, 1)
    common_sec_headers = {"User-Agent": sec_user_agent}
    return [
        Probe(
            "sec_submissions_apple",
            "sec",
            "filing_index",
            ["US"],
            "GET",
            "https://data.sec.gov/submissions/CIK0000320193.json",
            headers=common_sec_headers,
            required_paths=["cik", "name", "filings.recent.accessionNumber.0"],
            normalizer=_select(
                {
                    "cik": "cik",
                    "name": "name",
                    "sic": "sic",
                    "recent": "filings.recent.accessionNumber.0",
                }
            ),
            capabilities=["filing_events", "company_identity"],
            limitation="Automated use must identify the caller with a real contact in SEC_USER_AGENT.",
        ),
        Probe(
            "sec_companyfacts_apple",
            "sec",
            "financial_facts",
            ["US"],
            "GET",
            "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
            headers=common_sec_headers,
            required_paths=[
                "cik",
                "entityName",
                "facts.us-gaap.Assets.units.USD.0.val",
            ],
            normalizer=_select(
                {
                    "cik": "cik",
                    "entity_name": "entityName",
                    "assets": "facts.us-gaap.Assets.units.USD",
                }
            ),
            capabilities=[
                "us_financial_statements",
                "cashflow",
                "margins",
                "point_in_time_facts",
            ],
        ),
        Probe(
            "bls_total_nonfarm",
            "bls",
            "macro_labor",
            ["US"],
            "POST",
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
            headers={"Content-Type": "application/json"},
            json_body={
                "seriesid": ["CES0000000001"],
                "startyear": str(today.year - 1),
                "endyear": str(today.year),
            },
            required_paths=[
                "status",
                "Results.series.0.seriesID",
                "Results.series.0.data.0.value",
            ],
            normalizer=_select(
                {
                    "status": "status",
                    "series": "Results.series.0.seriesID",
                    "observations": "Results.series.0.data",
                }
            ),
            capabilities=["employment_macro_control", "time_series"],
        ),
        Probe(
            "gleif_apple",
            "gleif",
            "entity_identity",
            ["GLOBAL", "US"],
            "GET",
            "https://api.gleif.org/api/v1/lei-records",
            params={"filter[entity.legalName]": "Apple Inc.", "page[size]": 1},
            required_paths=["data.0.id", "data.0.attributes.entity.legalName.name"],
            normalizer=_select(
                {
                    "lei": "data.0.id",
                    "entity": "data.0.attributes.entity",
                    "relationships": "data.0.relationships",
                }
            ),
            capabilities=["lei_identity", "ownership_discovery"],
        ),
        Probe(
            "ares_czech_company",
            "ares",
            "entity_registry",
            ["CZ"],
            "GET",
            "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/27074358",
            required_paths=["ico", "obchodniJmeno", "sidlo.kodStatu"],
            normalizer=_select(
                {
                    "ico": "ico",
                    "legal_name": "obchodniJmeno",
                    "address": "sidlo",
                    "nace": "czNace",
                }
            ),
            capabilities=["czech_company_master", "nace_industry"],
        ),
        Probe(
            "eurostat_czech_gdp",
            "eurostat",
            "macro_economy",
            ["EU", "CZ"],
            "GET",
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tec00115",
            params={"geo": "CZ", "sinceTimePeriod": str(today.year - 3)},
            required_paths=["class", "id", "value"],
            normalizer=_select(
                {
                    "label": "label",
                    "updated": "updated",
                    "dimensions": "id",
                    "values": "value",
                }
            ),
            capabilities=["czech_gdp_growth", "eu_cross_country_macro"],
        ),
        Probe(
            "ecb_usd_eur",
            "ecb",
            "macro_financial",
            ["EU", "GLOBAL"],
            "GET",
            "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A",
            params={"startPeriod": month_start.isoformat(), "format": "jsondata"},
            required_paths=["header.sender.id", "dataSets.0.series"],
            normalizer=_select(
                {
                    "sender": "header.sender.id",
                    "prepared": "header.prepared",
                    "series": "dataSets.0.series",
                    "structure": "structure",
                }
            ),
            capabilities=["eur_fx", "market_control"],
        ),
        Probe(
            "oecd_cli",
            "oecd",
            "macro_leading_indicator",
            ["OECD", "EU", "CZ"],
            "GET",
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/.M.LI...AA...H",
            params={
                "startPeriod": f"{today.year - 1}-01",
                "dimensionAtObservation": "AllDimensions",
                "format": "jsondata",
            },
            required_paths=["meta.sender.id", "data.dataSets.0.observations"],
            normalizer=_select(
                {
                    "sender": "meta.sender.id",
                    "prepared": "meta.prepared",
                    "observations": "data.dataSets.0.observations",
                    "structures": "data.structures",
                }
            ),
            capabilities=["leading_indicator", "industry_cycle_control"],
        ),
        Probe(
            "imf_czech_growth",
            "imf",
            "macro_forecast",
            ["GLOBAL", "CZ"],
            "GET",
            "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/CZE",
            required_paths=["values.NGDP_RPCH.CZE"],
            normalizer=_select(
                {"series": "values.NGDP_RPCH.CZE", "periods": "periods"}
            ),
            capabilities=["gdp_forecast", "scenario_control"],
            limitation="The endpoint may over-return countries; normalization keeps the explicit CZE path.",
        ),
        Probe(
            "world_bank_gdp",
            "world_bank",
            "macro_cross_country",
            ["US", "KR", "CZ"],
            "GET",
            "https://api.worldbank.org/v2/country/USA;KOR;CZE/indicator/NY.GDP.MKTP.CD",
            params={
                "format": "json",
                "date": f"{today.year - 3}:{today.year}",
                "per_page": 100,
            },
            required_paths=["0.total", "1.0.countryiso3code", "1.0.date"],
            normalizer=_select({"metadata": "0", "observations": "1"}),
            capabilities=["cross_country_gdp", "country_size_control"],
        ),
        Probe(
            "cnb_exchange",
            "cnb",
            "macro_financial",
            ["CZ"],
            "GET",
            "https://api.cnb.cz/cnbapi/exrates/daily",
            params={"date": today.isoformat()},
            required_paths=["rates.0.currencyCode", "rates.0.rate", "rates.0.validFor"],
            normalizer=_select({"valid_for": "rates.0.validFor", "rates": "rates"}),
            capabilities=["czk_fx", "currency_exposure"],
        ),
        Probe(
            "cnb_czeonia",
            "cnb",
            "macro_rate",
            ["CZ"],
            "GET",
            "https://api.cnb.cz/cnbapi/czeonia/daily",
            params={"date": today.isoformat()},
            required_paths=[
                "czeoniaDaily.validFor",
                "czeoniaDaily.rate",
                "czeoniaDaily.volumeInCZKmio",
            ],
            normalizer=_select(
                {
                    "valid_for": "czeoniaDaily.validFor",
                    "rate": "czeoniaDaily.rate",
                    "volume": "czeoniaDaily.volumeInCZKmio",
                }
            ),
            capabilities=["czech_money_market_rate", "discount_rate_control"],
        ),
        Probe(
            "ted_czech_notices",
            "ted",
            "public_procurement",
            ["EU", "CZ"],
            "POST",
            "https://api.ted.europa.eu/v3/notices/search",
            headers={"Content-Type": "application/json"},
            json_body={
                "query": f"buyer-country = CZE AND publication-date >= {year_start.strftime('%Y%m%d')}",
                "fields": [
                    "publication-number",
                    "publication-date",
                    "buyer-country",
                    "buyer-name",
                    "winner-name",
                    "total-value",
                ],
                "limit": 1,
            },
            required_paths=["totalNoticeCount", "notices.0.publication-number"],
            normalizer=_select({"count": "totalNoticeCount", "notice": "notices.0"}),
            capabilities=["czech_contract_demand", "buyer_supplier_evidence"],
        ),
        Probe(
            "usaspending_contracts",
            "usaspending",
            "public_procurement",
            ["US"],
            "POST",
            "https://api.usaspending.gov/api/v2/search/spending_by_award/",
            headers={"Content-Type": "application/json"},
            json_body={
                "filters": {
                    "time_period": [
                        {
                            "start_date": year_start.isoformat(),
                            "end_date": today.isoformat(),
                        }
                    ],
                    "award_type_codes": ["A", "B", "C", "D"],
                },
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Award Amount",
                    "Awarding Agency",
                    "Start Date",
                    "End Date",
                    "NAICS Code",
                ],
                "page": 1,
                "limit": 1,
                "subawards": False,
            },
            required_paths=["results.0.Award ID", "results.0.Recipient Name"],
            normalizer=_select({"award": "results.0", "page": "page_metadata"}),
            capabilities=[
                "us_contract_revenue_signal",
                "government_customer_concentration",
            ],
            limitation="Filter dates can refer to transaction/action activity; use transaction endpoints for event timing.",
        ),
        Probe(
            "greenhouse_airtable",
            "greenhouse",
            "company_jobs",
            ["US", "GLOBAL"],
            "GET",
            "https://boards-api.greenhouse.io/v1/boards/airtable/jobs",
            params={"content": "true"},
            required_paths=["jobs.0.id", "jobs.0.title", "jobs.0.updated_at"],
            normalizer=_greenhouse,
            capabilities=["job_posting_snapshot", "department_demand"],
            limitation="A company board token must be discovered; removed postings require historical snapshots.",
        ),
        Probe(
            "lever_spotify",
            "lever",
            "company_jobs",
            ["EU", "US", "GLOBAL"],
            "GET",
            "https://api.lever.co/v0/postings/spotify",
            params={"mode": "json"},
            required_paths=["0.id", "0.text", "0.createdAt"],
            normalizer=_lever,
            capabilities=["job_posting_snapshot", "team_location_demand"],
            limitation="A company site slug must be discovered; removed postings require historical snapshots.",
        ),
        Probe(
            "github_microsoft",
            "github",
            "technology_activity",
            ["GLOBAL", "US"],
            "GET",
            "https://api.github.com/orgs/microsoft/repos",
            params={"per_page": 1, "sort": "updated"},
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            required_paths=["0.id", "0.full_name", "0.pushed_at"],
            normalizer=lambda body, _: {
                "repository": preserve_payload(json_payload(body)[0])
            },
            capabilities=["engineering_activity_proxy", "ai_adoption_evidence"],
        ),
        Probe(
            "openalex_microsoft",
            "openalex",
            "research_activity",
            ["GLOBAL"],
            "GET",
            "https://api.openalex.org/works",
            params={
                "filter": "institutions.id:I1290206253",
                "per-page": 1,
                "sort": "publication_date:desc",
            },
            required_paths=["meta.count", "results.0.id", "results.0.publication_year"],
            normalizer=_select({"count": "meta.count", "work": "results.0"}),
            capabilities=["research_output_proxy", "innovation_signal"],
            quota_note="Keyless access is a small demo budget; production volume needs provider-compliant access.",
        ),
    ]


def build_probes(
    settings: Settings, provider_filter: set[str] | None = None, purpose: str = "probe"
) -> list[Probe]:
    probes = keyed_probes() + keyless_probes(settings.sec_user_agent)
    if purpose not in {"probe", "production"}:
        raise ValueError("purpose must be probe or production")
    selected = (
        probes
        if not provider_filter or "all" in provider_filter
        else [
            probe
            for probe in probes
            if probe.provider in provider_filter or probe.id in provider_filter
        ]
    )
    if purpose == "probe":
        return selected
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    environment = dict(os.environ)
    return [
        probe
        for probe in selected
        if evaluate_activation(catalog.by_id(probe.id), environment).status.startswith(
            "ready"
        )
    ]


def source_health(settings: Settings) -> dict[str, dict[str, Any]]:
    """Show declared eligibility separately from the last saved live probe.

    A configured credential may still be rejected by its provider (for
    example, an inactive BEA key).  Combining those states would make
    ``provider-status`` deceptively green, so the latest validation receipt is
    surfaced as observation data rather than overwriting the catalog policy.
    """
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    environment = dict(os.environ)
    latest: dict[str, dict[str, Any]] = {}
    validation_file = settings.artifact_dir / "validation_results.json"
    if validation_file.is_file():
        try:
            payload = json.loads(validation_file.read_text(encoding="utf-8"))
            latest = {
                str(item["id"]): item
                for item in payload.get("results", [])
                if isinstance(item, dict) and item.get("id")
            }
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            latest = {}
    health: dict[str, dict[str, Any]] = {}
    for operation in catalog.operations:
        selection = classify_operation(operation)
        last = latest.get(operation.operation_id)
        health[operation.operation_id] = {
            "activation": evaluate_activation(operation, environment).status,
            "disposition": selection.disposition,
            "reason": selection.reason,
            "last_probe": None
            if last is None
            else {
                "status": last.get("status"),
                "http_status": last.get("http_status"),
                "collected_at": last.get("collected_at"),
                "detail": last.get("provider_error")
                or last.get("transport_error")
                or last.get("parse_error"),
            },
        }
    return health


def production_adapters(
    settings: Settings, cluster: ProviderCluster | None = None
) -> list[Probe]:
    """Select enabled production operations, never fixed validation fixtures."""
    catalog = load_source_catalog(settings.project_root / "config/providers.json")
    if cluster is None:
        allowed = {
            item.operation_id
            for selected_cluster in ProviderCluster
            for item in select_operations(catalog.operations, selected_cluster)
        }
    else:
        allowed = {
            item.operation_id for item in select_operations(catalog.operations, cluster)
        }
    return [
        probe
        for probe in build_probes(settings, purpose="production")
        if probe.id in allowed
    ]
