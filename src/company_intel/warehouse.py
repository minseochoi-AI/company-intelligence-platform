from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import Settings
from .identity import IdentifierLink
from .models import AtomicFact, CompanyClassification, RequirementEvidence


def duckdb_path(database_url: str, project_root: Path | None = None) -> Path:
    prefix = "duckdb:///"
    if not database_url.startswith(prefix):
        raise ValueError("Local warehouse currently requires DATABASE_URL=duckdb:///absolute/path")
    stripped = database_url[len(prefix) :].lstrip("/")
    raw_path = Path("/" + stripped)
    if not raw_path.exists() and project_root is not None:
        candidate = project_root / stripped
        if candidate.exists():
            return candidate
        candidate_data = project_root / "data" / Path(stripped).name
        if candidate_data.exists():
            return candidate_data
    return raw_path


class Warehouse:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.path = duckdb_path(settings.database_url, settings.project_root)

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
            # This is a direct identifier assertion from the same OpenDART
            # source used to create the entity; unlike an ALIO+ display name,
            # it is safe to make the entity searchable as resolved.
            connection.execute(
                """INSERT OR REPLACE INTO identifier_mapping(identifier_type,identifier_value,entity_id,source,confidence,resolved_at)
                VALUES ('dart_corp_code','00126380','DART:00126380','OpenDART',1.0,?)""",
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

    def upsert_identity(self, link: IdentifierLink) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO identifier_mapping(identifier_type,identifier_value,entity_id,source,confidence,resolved_at)
                VALUES (?,?,?,?,?,?)""",
                [link.identifier_type, link.identifier_value, link.entity_id, link.source, link.confidence, datetime.now(UTC).isoformat()],
            )

    def upsert_capability(self, entity_id: str, operation_id: str, capability: str, status: str, source_url: str | None, available_at: str | None) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO company_source_capability(entity_id,operation_id,capability,status,source_url,available_at)
                VALUES (?,?,?,?,?,?)""", [entity_id, operation_id, capability, status, source_url, available_at]
            )

    def record_field_availability(self, entity_id: str, operation_id: str, field_name: str, status: str, observation_date: str | None, available_at: str | None) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO field_availability(entity_id,operation_id,field_name,status,observation_date,available_at)
                VALUES (?,?,?,?,?,?)""", [entity_id, operation_id, field_name, status, observation_date, available_at]
            )

    def record_classification(self, classification: CompanyClassification) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO classification_history(entity_id,classified_at,capabilities_json,correlation_ready,causal_ready,reasons_json)
                VALUES (?,?,?,?,?,?)""",
                [classification.entity_id, datetime.now(UTC).isoformat(), json.dumps(classification.capabilities),
                 classification.analysis_eligibility.correlation_ready, classification.analysis_eligibility.causal_ready,
                 json.dumps([*classification.classification_reasons, *classification.analysis_eligibility.reasons])],
            )

    def store_source_snapshot(self, *, operation_id: str, collected_at: str, raw_sha256: str,
                              source_url: str | None, coverage: str | None,
                              disposition: str) -> str:
        snapshot_id = hashlib.sha256(f"{operation_id}|{collected_at}|{raw_sha256}".encode()).hexdigest()
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO source_snapshot(snapshot_id,operation_id,collected_at,source_url,raw_sha256,coverage,disposition)
                VALUES (?,?,?,?,?,?,?)""",
                [snapshot_id, operation_id, collected_at, source_url, raw_sha256, coverage, disposition],
            )
        return snapshot_id

    def store_atomic_fact(self, fact: AtomicFact, *, snapshot_id: str) -> str:
        fact_id = hashlib.sha256("|".join((fact.operation_id, fact.raw_record_id or "", fact.fact_key, fact.available_at or "")).encode()).hexdigest()
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO atomic_fact(fact_id,entity_id,operation_id,fact_key,value_json,unit,currency,period,concept,available_at,source_url,raw_record_id,snapshot_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [fact_id, fact.entity_id, fact.operation_id, fact.fact_key, json.dumps(fact.value, ensure_ascii=False), fact.unit,
                 fact.currency, fact.period, fact.concept, fact.available_at, fact.source_url, fact.raw_record_id, snapshot_id],
            )
        return fact_id

    def store_verdict(self, *, subject_type: str, subject_id: str, field_name: str,
                      verdict: str, reason: str | None, observed_value: object = None) -> str:
        created_at = datetime.now(UTC).isoformat()
        verdict_id = hashlib.sha256(f"{subject_type}|{subject_id}|{field_name}|{verdict}|{created_at}".encode()).hexdigest()
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO search_verdict(verdict_id,subject_type,subject_id,field_name,verdict,reason,observed_value,created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                [verdict_id, subject_type, subject_id, field_name, verdict, reason,
                 None if observed_value is None else json.dumps(observed_value, ensure_ascii=False), created_at],
            )
        return verdict_id

    def resolve_current_fact(self, entity_id: str, fact_key: str) -> list[dict[str, Any]]:
        return self.query(
            """SELECT * FROM atomic_fact WHERE entity_id=? AND fact_key=?
            ORDER BY available_at DESC NULLS LAST, snapshot_id DESC""", [entity_id, fact_key]
        )

    def store_requirement_evidence(self, provider: str, job_id: str, requirement_id: str, requirement: RequirementEvidence, observed_at: str) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO job_requirement(provider,job_id,requirement_id,text,requirement_status,evidence_scope,source_url,observed_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                [provider, job_id, requirement_id, requirement.text, requirement.status, requirement.evidence_scope, requirement.source_url, observed_at],
            )
            if requirement.source_url:
                connection.execute(
                    """INSERT OR REPLACE INTO credential_evidence(requirement_id,source_url,source_kind,excerpt,collected_at)
                    VALUES (?,?,?,?,?)""",
                    [requirement_id, requirement.source_url, requirement.evidence_scope, None, observed_at],
                )

    def store_job_snapshot(self, row: dict[str, Any]) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO job_posting_snapshot(provider,job_id,entity_id,company_name,title,department,
                occupation_code,location,country_code,workplace_type,posted_at,first_seen_at,last_seen_at,snapshot_date,is_active)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    row["provider"], row["job_id"], row.get("entity_id"), row.get("company_name"), row.get("title"),
                    row.get("department"), row.get("occupation_code"), row.get("location"), row.get("country_code"),
                    row.get("workplace_type"), row.get("posted_at"), row["first_seen_at"], row["last_seen_at"],
                    row["snapshot_date"], row.get("is_active", True),
                ],
            )

    def search_candidates(self, countries: tuple[str, ...]) -> list[dict[str, Any]]:
        placeholders = ",".join("?" for _ in countries)
        rows = self.query(
            f"SELECT entity_id, legal_name, country_code, industry_code FROM entity WHERE country_code IN ({placeholders}) ORDER BY entity_id",
            list(countries),
        )
        for row in rows:
            capability_rows = self.query(
                "SELECT capability,status,source_url FROM company_source_capability WHERE entity_id=?", [row["entity_id"]]
            )
            row["name"] = row.pop("legal_name")
            row["capabilities"] = {item["capability"]: item["status"] for item in capability_rows}
            row["evidence_urls"] = [item["source_url"] for item in capability_rows if item.get("source_url")]
            row["identity_status"] = "resolved" if self.query("SELECT 1 FROM identifier_mapping WHERE entity_id=? LIMIT 1", [row["entity_id"]]) else "unresolved"
        return rows

    def query_export_bundle(self, entity_ids: list[str] | None = None) -> dict[str, list[dict[str, Any]]]:
        filter_sql, params = "", []
        if entity_ids:
            filter_sql = " WHERE entity_id IN (" + ",".join("?" for _ in entity_ids) + ")"
            params = entity_ids
        companies = self.query("SELECT entity_id AS company_id, legal_name, country_code, industry_code FROM entity" + filter_sql + " ORDER BY entity_id", params)
        capabilities = self.query("SELECT entity_id AS company_id, operation_id, capability, status, source_url, available_at FROM company_source_capability" + filter_sql + " ORDER BY entity_id, operation_id, capability", params)
        job_filter, job_params = "", []
        if entity_ids:
            job_filter = " WHERE entity_id IN (" + ",".join("?" for _ in entity_ids) + ")"
            job_params = entity_ids
        jobs = self.query("SELECT provider, job_id, entity_id AS company_id, title, country_code, posted_at, snapshot_date, is_active FROM job_posting_snapshot" + job_filter + " ORDER BY provider, job_id, snapshot_date", job_params)
        job_pairs = {(row["provider"], row["job_id"]) for row in jobs}
        requirements = [
            row for row in self.query("SELECT provider, job_id, requirement_id, text, requirement_status, evidence_scope, source_url, observed_at FROM job_requirement ORDER BY provider, job_id, requirement_id")
            if (row["provider"], row["job_id"]) in job_pairs
        ]
        sources = self.query("SELECT DISTINCT operation_id AS source_id, source_url FROM company_source_capability WHERE source_url IS NOT NULL ORDER BY operation_id")
        exclusions = self.query("SELECT entity_id AS company_id, reasons_json AS reason FROM classification_history WHERE correlation_ready=false ORDER BY entity_id, classified_at")
        return {"companies": companies, "capabilities": capabilities, "jobs": jobs, "requirements": requirements, "sources": sources, "exclusions": exclusions}

    def materialize_export_snapshot(self, entity_ids: list[str] | None = None) -> dict[str, list[dict[str, Any]]]:
        return self.query_export_bundle(entity_ids)

    def _ensure_live_snapshot_schema(self, connection: Any) -> None:
        """Install additive snapshot lineage tables for existing DuckDB files."""

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_run (
                snapshot_id VARCHAR PRIMARY KEY, collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
                parameters_json JSON, status VARCHAR NOT NULL, partial_failure BOOLEAN NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshot_source (
                snapshot_id VARCHAR NOT NULL, provider VARCHAR NOT NULL, operation_id VARCHAR,
                raw_sha256 VARCHAR, provider_denominator BIGINT, normalized_count BIGINT,
                active_count BIGINT, coverage_json JSON, status VARCHAR NOT NULL, reason VARCHAR,
                PRIMARY KEY(snapshot_id, provider)
            );
            CREATE TABLE IF NOT EXISTS entity_link (
                provider_entity_id VARCHAR, canonical_entity_id VARCHAR, snapshot_id VARCHAR NOT NULL,
                link_status VARCHAR NOT NULL, link_method VARCHAR NOT NULL, evidence_json JSON,
                PRIMARY KEY(provider_entity_id, snapshot_id, link_method)
            );
            CREATE TABLE IF NOT EXISTS posting_snapshot_membership (
                snapshot_id VARCHAR NOT NULL, provider VARCHAR NOT NULL, job_id VARCHAR NOT NULL,
                taxonomy_version VARCHAR, normalizer_version VARCHAR, coverage_cohort VARCHAR,
                PRIMARY KEY(snapshot_id, provider, job_id)
            );
            CREATE TABLE IF NOT EXISTS posting_lifecycle (
                provider VARCHAR NOT NULL, job_id VARCHAR NOT NULL, first_snapshot_id VARCHAR NOT NULL,
                last_snapshot_id VARCHAR NOT NULL, appearances BIGINT NOT NULL, lifecycle VARCHAR NOT NULL,
                PRIMARY KEY(provider, job_id, last_snapshot_id)
            );
            """
        )

    def store_snapshot(self, manifest: dict[str, Any]) -> str:
        """Persist the redacted snapshot manifest and per-provider denominators."""

        snapshot_id = str(manifest["snapshot_id"])
        with self.connect() as connection:
            self._ensure_live_snapshot_schema(connection)
            connection.execute(
                "INSERT OR REPLACE INTO snapshot_run VALUES (?,?,?,?,?)",
                [snapshot_id, manifest.get("collected_at"), json.dumps(manifest.get("request", {}), ensure_ascii=False), manifest.get("status", "unknown"), bool(manifest.get("partial_failure"))],
            )
            for source in manifest.get("sources", []):
                if not isinstance(source, dict):
                    continue
                connection.execute(
                    "INSERT OR REPLACE INTO snapshot_source VALUES (?,?,?,?,?,?,?,?,?,?)",
                    [snapshot_id, source.get("provider"), source.get("operation_id"), source.get("payload_sha256"), source.get("record_count"), source.get("normalized_count"), source.get("active_count"), json.dumps(source.get("coverage", {}), ensure_ascii=False), source.get("status", "unknown"), source.get("reason")],
                )
        return snapshot_id

    def load_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            self._ensure_live_snapshot_schema(connection)
            row = connection.execute("SELECT * FROM snapshot_run WHERE snapshot_id=?", [snapshot_id]).fetchone()
            if row is None:
                return None
            columns = [item[0] for item in connection.description]
            result = dict(zip(columns, row))
            sources = connection.execute("SELECT * FROM snapshot_source WHERE snapshot_id=? ORDER BY provider", [snapshot_id]).fetchall()
            source_columns = [item[0] for item in connection.description]
            result["sources"] = [dict(zip(source_columns, item)) for item in sources]
            return result

    def store_entity_link(self, link: dict[str, Any], *, snapshot_id: str) -> None:
        with self.connect() as connection:
            self._ensure_live_snapshot_schema(connection)
            connection.execute(
                "INSERT OR REPLACE INTO entity_link VALUES (?,?,?,?,?,?)",
                [link.get("provider_entity_id"), link.get("canonical_entity_id"), snapshot_id, link.get("status", "unresolved"), link.get("method", "unknown"), json.dumps(link.get("evidence", {}), ensure_ascii=False)],
            )

    def store_posting_membership(self, snapshot_id: str, rows: list[dict[str, Any]], *, taxonomy_version: str, normalizer_version: str, coverage_cohort: str) -> None:
        with self.connect() as connection:
            self._ensure_live_snapshot_schema(connection)
            connection.executemany(
                "INSERT OR REPLACE INTO posting_snapshot_membership VALUES (?,?,?,?,?,?)",
                [(snapshot_id, row.get("provider"), row.get("job_id"), taxonomy_version, normalizer_version, coverage_cohort) for row in rows if row.get("provider") and row.get("job_id")],
            )

    def load_snapshot_series(self, *, provider: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as connection:
            self._ensure_live_snapshot_schema(connection)
            sql = "SELECT m.*, r.collected_at FROM posting_snapshot_membership m JOIN snapshot_run r USING(snapshot_id)"
            params: list[Any] = []
            if provider:
                sql += " WHERE m.provider=?"
                params.append(provider)
            sql += " ORDER BY r.collected_at, m.provider, m.job_id"
            cursor = connection.execute(sql, params)
            return [dict(zip([item[0] for item in cursor.description], row)) for row in cursor.fetchall()]

    def _ensure_watermark_schema(self, connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS etl_sync_watermarks (
                source_name VARCHAR PRIMARY KEY,
                last_sync_time TIMESTAMP WITH TIME ZONE NOT NULL,
                records_synced BIGINT DEFAULT 0,
                sync_status VARCHAR NOT NULL,
                last_watermark_value VARCHAR,
                details_json JSON
            );
            CREATE TABLE IF NOT EXISTS public_procurement (
                procurement_id VARCHAR PRIMARY KEY,
                source_system VARCHAR NOT NULL,
                country VARCHAR NOT NULL,
                buyer_name VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                contract_amount DOUBLE,
                currency VARCHAR NOT NULL,
                notice_date DATE NOT NULL,
                winner_name VARCHAR,
                industry_category VARCHAR,
                url VARCHAR,
                collected_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
            );
            """
        )

    def get_watermark(self, source_name: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            self._ensure_watermark_schema(connection)
            cursor = connection.execute(
                "SELECT source_name, last_sync_time, records_synced, sync_status, last_watermark_value, details_json FROM etl_sync_watermarks WHERE source_name=?",
                [source_name],
            )
            row = cursor.fetchone()
            if not row:
                return None
            cols = [item[0] for item in cursor.description]
            res = dict(zip(cols, row))
            if res.get("details_json") and isinstance(res["details_json"], str):
                try:
                    res["details_json"] = json.loads(res["details_json"])
                except Exception:
                    pass
            return res

    def update_watermark(
        self,
        source_name: str,
        records_synced: int,
        sync_status: str = "SUCCESS",
        last_watermark_value: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        now = datetime.now(UTC)
        with self.connect() as connection:
            self._ensure_watermark_schema(connection)
            connection.execute(
                """
                INSERT INTO etl_sync_watermarks(source_name, last_sync_time, records_synced, sync_status, last_watermark_value, details_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (source_name) DO UPDATE SET
                    last_sync_time=excluded.last_sync_time,
                    records_synced=etl_sync_watermarks.records_synced + excluded.records_synced,
                    sync_status=excluded.sync_status,
                    last_watermark_value=excluded.last_watermark_value,
                    details_json=excluded.details_json
                """,
                [
                    source_name,
                    now,
                    records_synced,
                    sync_status,
                    last_watermark_value,
                    json.dumps(details or {}, ensure_ascii=False),
                ],
            )

    def ingest_public_procurements(self, records: list[dict[str, Any]]) -> int:
        if not records:
            return 0
        rows = [
            (
                r.get("procurement_id"),
                r.get("source_system", "UNKNOWN"),
                r.get("country", "KR"),
                r.get("buyer_name", "Unknown Buyer"),
                r.get("title", ""),
                float(r.get("contract_amount", 0.0) or 0.0),
                r.get("currency", "KRW"),
                r.get("notice_date", "2026-01-01"),
                r.get("winner_name"),
                r.get("industry_category"),
                r.get("url"),
            )
            for r in records
        ]
        with self.connect() as connection:
            self._ensure_watermark_schema(connection)
            connection.executemany(
                """
                INSERT OR REPLACE INTO public_procurement(
                    procurement_id, source_system, country, buyer_name, title,
                    contract_amount, currency, notice_date, winner_name, industry_category, url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def incremental_sync_source(
        self,
        source_name: str,
        fetcher_fn: Any,
    ) -> dict[str, Any]:
        """Execute incremental ETL sync using watermarking to prevent duplicate full reloads."""
        watermark = self.get_watermark(source_name)
        since_val = watermark.get("last_watermark_value") if watermark else None
        
        try:
            records, next_watermark = fetcher_fn(since_val)
            ingested_count = len(records)
            if source_name == "KONEPS":
                ingested_count = self.ingest_public_procurements(records)
            
            self.update_watermark(
                source_name=source_name,
                records_synced=ingested_count,
                sync_status="SUCCESS",
                last_watermark_value=str(next_watermark) if next_watermark else since_val,
                details={"fetched": len(records), "ingested": ingested_count},
            )
            return {
                "source": source_name,
                "status": "SUCCESS",
                "records_synced": ingested_count,
                "watermark": next_watermark or since_val,
            }
        except Exception as exc:
            self.update_watermark(
                source_name=source_name,
                records_synced=0,
                sync_status="FAILED",
                last_watermark_value=since_val,
                details={"error": str(exc)},
            )
            raise

