from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import Settings


def duckdb_path(database_url: str) -> Path:
    prefix = "duckdb:///"
    if not database_url.startswith(prefix):
        raise ValueError("Local warehouse currently requires DATABASE_URL=duckdb:///absolute/path")
    return Path("/" + database_url[len(prefix) :].lstrip("/"))


class Warehouse:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.path = duckdb_path(settings.database_url)

    def connect(self):
        try:
            import duckdb
        except ImportError as error:
            raise RuntimeError("duckdb is required; run pip install -e .") from error
        self.path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(self.path))

    def initialize(self) -> None:
        ddl = (self.settings.project_root / "sql/duckdb_schema.sql").read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.execute(ddl)

    def ingest_validation_evidence(self, validation_file: Path | None = None) -> int:
        source = validation_file or self.settings.artifact_dir / "validation_results.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        rows = []
        api_rows = []
        for item in payload.get("results", []):
            if item.get("http_status") is None:
                continue
            rows.append(
                (
                    item.get("provider"),
                    item.get("id"),
                    item.get("url"),
                    item.get("collected_at"),
                    item.get("collected_at"),
                    item.get("raw_file"),
                    item.get("response_sha256_before_redaction"),
                    item.get("stored_body_redacted", False),
                    item.get("http_status"),
                    json.dumps({"status": item.get("status"), "field_checks": item.get("field_checks")}),
                )
            )
            api_rows.append(
                (
                    item.get("id"), item.get("provider"), item.get("id"), item.get("collected_at"),
                    item.get("collected_at"), item.get("http_status"), item.get("elapsed_ms"), item.get("attempts"),
                    item.get("response_bytes"), json.dumps({"quota_note": item.get("quota_note")}),
                    None if item.get("status") == "passed" else item.get("status"),
                    item.get("provider_error") or item.get("parse_error") or item.get("transport_error"),
                )
            )
        with self.connect() as connection:
            connection.executemany("DELETE FROM evidence WHERE request_id=?", [(row[1],) for row in rows])
            connection.executemany(
                """
                INSERT INTO evidence(provider, request_id, source_url_redacted, collected_at, available_at,
                    raw_path, raw_sha256_before_redaction, stored_body_redacted, http_status, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            connection.executemany(
                """INSERT OR REPLACE INTO api_call_log(request_id,provider,probe_id,requested_at,completed_at,
                http_status,elapsed_ms,attempts,response_bytes,quota_json,error_type,error_message_redacted)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                api_rows,
            )
        return len(rows)

    def ingest_normalized_artifacts(self) -> dict[str, int]:
        normalized = self.settings.artifact_dir / "normalized"
        counts = {"financial_fact": 0, "macro_observation": 0, "market_price": 0, "job_posting_snapshot": 0}

        def load(name: str) -> dict[str, Any] | None:
            path = normalized / f"{name}.json"
            return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

        with self.connect() as connection:
            now = datetime.now(UTC).isoformat()
            connection.execute(
                """INSERT OR REPLACE INTO entity(entity_id,legal_name,country_code,entity_type,dart_corp_code,source,collected_at)
                VALUES ('DART:00126380','삼성전자','KR','company','00126380','OpenDART',?)""",
                [now],
            )
            connection.execute(
                """INSERT OR REPLACE INTO entity(entity_id,legal_name,country_code,entity_type,source,collected_at)
                VALUES ('ATS:AIRTABLE','Airtable','US','company','Greenhouse',?),
                       ('ATS:SPOTIFY','Spotify','SE','company','Lever',?)""",
                [now, now],
            )
            connection.execute(
                """INSERT OR REPLACE INTO entity(entity_id,legal_name,country_code,entity_type,source,collected_at)
                VALUES ('TICKER:IBM','International Business Machines','US','company','Alpha Vantage',?)""",
                [now],
            )
            connection.execute(
                """INSERT OR REPLACE INTO security(security_id,entity_id,ticker,exchange,currency,source)
                VALUES ('AV:IBM','TICKER:IBM','IBM','US','USD','Alpha Vantage')"""
            )

            dart = load("opendart_samsung_financials")
            if dart:
                rows = []
                for fact in dart["data"].get("financial_facts", []):
                    receipt = str(fact.get("receipt_no") or "")
                    available_at = (
                        f"{receipt[:4]}-{receipt[4:6]}-{receipt[6:8]}T00:00:00+00:00"
                        if len(receipt) >= 8
                        else dart["collected_at"]
                    )
                    year = str(fact.get("report_year") or "")
                    period_end = f"{year}-12-31" if len(year) == 4 else available_at[:10]
                    fact_key = "|".join(
                        str(part or "")
                        for part in (
                            fact.get("statement"),
                            fact.get("account_id"),
                            fact.get("account_detail"),
                            fact.get("order"),
                        )
                    )
                    rows.append(
                        (
                            "DART:00126380",
                            receipt or None,
                            fact_key,
                            fact.get("account_id") or fact.get("account_name"),
                            fact.get("account_name"),
                            fact.get("statement"),
                            period_end,
                            available_at,
                            fact.get("current_amount"),
                            fact.get("currency"),
                            fact.get("currency"),
                            json.dumps(
                                {"account_detail": fact.get("account_detail"), "order": fact.get("order")},
                                ensure_ascii=False,
                            ),
                            "OpenDART",
                        )
                    )
                connection.executemany(
                    """INSERT OR REPLACE INTO financial_fact(entity_id,filing_id,fact_key,concept_id,concept_name,statement_type,
                    period_end,available_at,value,unit,currency,segment_json,source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    rows,
                )
                counts["financial_fact"] += len(rows)

            for name, source, country in [
                ("fred_federal_funds_rate", "FRED", "US"),
                ("ecos_korea_base_rate", "ECOS", "KR"),
            ]:
                payload = load(name)
                if not payload:
                    continue
                rows = []
                for observation in payload["data"].get("observations", []):
                    raw_date = str(observation.get("observation_date") or "")
                    date_value = (
                        f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
                        if len(raw_date) == 8 and raw_date.isdigit()
                        else raw_date
                    )
                    rows.append(
                        (
                            observation.get("series_id") or observation.get("series_code") or name,
                            country,
                            date_value,
                            observation.get("available_at") or payload["collected_at"],
                            observation.get("value"),
                            observation.get("unit"),
                            observation.get("frequency"),
                            source,
                        )
                    )
                connection.executemany(
                    """INSERT OR REPLACE INTO macro_observation(series_id,country_code,observation_date,available_at,
                    value,unit,frequency,source) VALUES (?,?,?,?,?,?,?,?)""",
                    rows,
                )
                counts["macro_observation"] += len(rows)

            alpha = load("alphavantage_ibm_daily")
            if alpha:
                rows = [
                    (
                        "AV:IBM",
                        price["price_date"],
                        alpha["collected_at"],
                        price.get("open"),
                        price.get("high"),
                        price.get("low"),
                        price.get("close"),
                        price.get("volume"),
                        "USD",
                        "Alpha Vantage",
                    )
                    for price in alpha["data"].get("prices", [])
                ]
                connection.executemany(
                    """INSERT OR REPLACE INTO market_price(security_id,price_date,available_at,open,high,low,close,
                    volume,currency,source) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    rows,
                )
                counts["market_price"] += len(rows)

            for name, provider, entity_id in [
                ("greenhouse_airtable", "greenhouse", "ATS:AIRTABLE"),
                ("lever_spotify", "lever", "ATS:SPOTIFY"),
            ]:
                payload = load(name)
                if not payload:
                    continue
                snapshot = payload["collected_at"][:10]
                rows = []
                for job in payload["data"].get("jobs", []):
                    departments = job.get("departments") or []
                    department = ", ".join(departments) if isinstance(departments, list) else job.get("team")
                    posted_at = job.get("first_published") or job.get("created_at")
                    if isinstance(posted_at, (int, float)):
                        posted_at = datetime.fromtimestamp(posted_at / 1000, UTC).isoformat()
                    rows.append(
                        (
                            provider,
                            str(job.get("job_id")),
                            entity_id,
                            job.get("company_name"),
                            job.get("title"),
                            department or job.get("team"),
                            job.get("location"),
                            job.get("country"),
                            job.get("workplace_type"),
                            posted_at,
                            payload["collected_at"],
                            payload["collected_at"],
                            snapshot,
                            True,
                        )
                    )
                connection.executemany(
                    """INSERT OR REPLACE INTO job_posting_snapshot(provider,job_id,entity_id,company_name,title,department,
                    location,country_code,workplace_type,posted_at,first_seen_at,last_seen_at,snapshot_date,is_active)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    rows,
                )
                counts["job_posting_snapshot"] += len(rows)
        return counts

    def query(self, sql: str, parameters: list[Any] | None = None) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(sql, parameters or [])
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
