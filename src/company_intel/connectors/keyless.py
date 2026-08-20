from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from ..models import Probe
from .base import compact, get_path, json_payload


def _select(mapping: dict[str, str]):
    from .base import MISSING

    def safe_normalize(body: bytes, _: str) -> dict[str, Any]:
        data = json_payload(body)
        output: dict[str, Any] = {}
        for label, path in mapping.items():
            value = get_path(data, path)
            output[label] = None if value is MISSING else compact(value)
        return output

    return safe_normalize


def _greenhouse(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    jobs = data.get("jobs", [])
    return {
        "job_count": len(jobs),
        "jobs": [
            {
                "job_id": str(job.get("id")),
                "company_name": job.get("company_name"),
                "title": job.get("title"),
                "location": (job.get("location") or {}).get("name"),
                "departments": [department.get("name") for department in job.get("departments", [])],
                "first_published": job.get("first_published"),
                "updated_at": job.get("updated_at"),
                "absolute_url": job.get("absolute_url"),
            }
            for job in jobs
        ],
    }


def _lever(body: bytes, _: str) -> dict[str, Any]:
    jobs = json_payload(body)
    return {
        "job_count": len(jobs),
        "jobs": [
            {
                "job_id": job.get("id"),
                "title": job.get("text"),
                "country": job.get("country"),
                "workplace_type": job.get("workplaceType"),
                "team": (job.get("categories") or {}).get("team"),
                "location": (job.get("categories") or {}).get("location"),
                "created_at": job.get("createdAt"),
                "hosted_url": job.get("hostedUrl"),
            }
            for job in jobs
        ],
    }


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
                {"cik": "cik", "name": "name", "sic": "sic", "recent": "filings.recent.accessionNumber.0"}
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
            required_paths=["cik", "entityName", "facts.us-gaap.Assets.units.USD.0.val"],
            normalizer=_select(
                {"cik": "cik", "entity_name": "entityName", "assets": "facts.us-gaap.Assets.units.USD"}
            ),
            capabilities=["us_financial_statements", "cashflow", "margins", "point_in_time_facts"],
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
            required_paths=["status", "Results.series.0.seriesID", "Results.series.0.data.0.value"],
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
                {"ico": "ico", "legal_name": "obchodniJmeno", "address": "sidlo", "nace": "czNace"}
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
                {"label": "label", "updated": "updated", "dimensions": "id", "values": "value"}
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
            normalizer=_select({"series": "values.NGDP_RPCH.CZE", "periods": "periods"}),
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
            params={"format": "json", "date": f"{today.year - 3}:{today.year}", "per_page": 100},
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
            required_paths=["czeoniaDaily.validFor", "czeoniaDaily.rate", "czeoniaDaily.volumeInCZKmio"],
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
                    "time_period": [{"start_date": year_start.isoformat(), "end_date": today.isoformat()}],
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
            capabilities=["us_contract_revenue_signal", "government_customer_concentration"],
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
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
            required_paths=["0.id", "0.full_name", "0.pushed_at"],
            normalizer=lambda body, _: {"repository": compact(json_payload(body)[0])},
            capabilities=["engineering_activity_proxy", "ai_adoption_evidence"],
        ),
        Probe(
            "openalex_microsoft",
            "openalex",
            "research_activity",
            ["GLOBAL"],
            "GET",
            "https://api.openalex.org/works",
            params={"filter": "institutions.id:I1290206253", "per-page": 1, "sort": "publication_date:desc"},
            required_paths=["meta.count", "results.0.id", "results.0.publication_year"],
            normalizer=_select({"count": "meta.count", "work": "results.0"}),
            capabilities=["research_output_proxy", "innovation_signal"],
            quota_note="Keyless access is a small demo budget; production volume needs provider-compliant access.",
        ),
    ]
