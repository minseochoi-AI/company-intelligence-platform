CREATE TABLE IF NOT EXISTS entity (
    entity_id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, country_code CHAR(2), entity_type TEXT,
    lei TEXT, cik TEXT, dart_corp_code TEXT, ico TEXT, industry_code TEXT, industry_system TEXT,
    valid_from DATE, valid_to DATE, source TEXT, collected_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS entity_lei_uq ON entity(lei) WHERE lei IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS entity_cik_uq ON entity(cik) WHERE cik IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS entity_dart_uq ON entity(dart_corp_code) WHERE dart_corp_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS security (
    security_id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entity(entity_id), ticker TEXT,
    exchange TEXT, isin TEXT, currency TEXT, valid_from DATE, valid_to DATE, source TEXT
);
CREATE TABLE IF NOT EXISTS filing (
    filing_id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entity(entity_id), filing_type TEXT,
    period_end DATE, filing_date TIMESTAMPTZ, available_at TIMESTAMPTZ NOT NULL, revision_at TIMESTAMPTZ,
    fiscal_year INTEGER, fiscal_period TEXT, accounting_standard TEXT, consolidated BOOLEAN,
    source_url TEXT, raw_sha256 TEXT
);
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id BIGSERIAL PRIMARY KEY, provider TEXT NOT NULL, request_id TEXT, source_url_redacted TEXT,
    collected_at TIMESTAMPTZ NOT NULL, available_at TIMESTAMPTZ, raw_path TEXT,
    raw_sha256_before_redaction TEXT, stored_body_redacted BOOLEAN, http_status INTEGER, metadata_json JSONB
);
CREATE TABLE IF NOT EXISTS financial_fact (
    entity_id TEXT NOT NULL REFERENCES entity(entity_id), filing_id TEXT REFERENCES filing(filing_id),
    fact_key TEXT NOT NULL, concept_id TEXT NOT NULL, concept_name TEXT, statement_type TEXT, period_start DATE, period_end DATE NOT NULL,
    available_at TIMESTAMPTZ NOT NULL, revision_at TIMESTAMPTZ, value DOUBLE PRECISION, unit TEXT, currency TEXT,
    segment_json JSONB, source TEXT NOT NULL, evidence_id BIGINT REFERENCES evidence(evidence_id),
    PRIMARY KEY(entity_id, fact_key, period_end, available_at, source)
);
CREATE TABLE IF NOT EXISTS market_price (
    security_id TEXT NOT NULL REFERENCES security(security_id), price_date DATE NOT NULL,
    available_at TIMESTAMPTZ NOT NULL, open DOUBLE PRECISION, high DOUBLE PRECISION, low DOUBLE PRECISION,
    close DOUBLE PRECISION, adjusted_close DOUBLE PRECISION, volume DOUBLE PRECISION, dividend DOUBLE PRECISION,
    split_factor DOUBLE PRECISION, currency TEXT, source TEXT NOT NULL,
    evidence_id BIGINT REFERENCES evidence(evidence_id), PRIMARY KEY(security_id, price_date, source)
);
CREATE TABLE IF NOT EXISTS macro_observation (
    series_id TEXT NOT NULL, country_code CHAR(2), industry_code TEXT, observation_date DATE NOT NULL,
    period_start DATE, period_end DATE, available_at TIMESTAMPTZ NOT NULL, revision_at TIMESTAMPTZ,
    value DOUBLE PRECISION, unit TEXT, frequency TEXT, source TEXT NOT NULL,
    evidence_id BIGINT REFERENCES evidence(evidence_id), PRIMARY KEY(series_id, observation_date, available_at, source)
);
CREATE TABLE IF NOT EXISTS workforce_fact (
    entity_id TEXT NOT NULL REFERENCES entity(entity_id), metric TEXT NOT NULL, period_end DATE NOT NULL,
    available_at TIMESTAMPTZ NOT NULL, value DOUBLE PRECISION, unit TEXT, scope TEXT, source TEXT NOT NULL,
    evidence_id BIGINT REFERENCES evidence(evidence_id), PRIMARY KEY(entity_id, metric, period_end, available_at, source)
);
CREATE TABLE IF NOT EXISTS job_posting_snapshot (
    provider TEXT NOT NULL, job_id TEXT NOT NULL, entity_id TEXT REFERENCES entity(entity_id), company_name TEXT,
    title TEXT, department TEXT, occupation_code TEXT, location TEXT, country_code CHAR(2), workplace_type TEXT,
    posted_at TIMESTAMPTZ, first_seen_at TIMESTAMPTZ NOT NULL, last_seen_at TIMESTAMPTZ NOT NULL,
    snapshot_date DATE NOT NULL, is_active BOOLEAN, description_hash TEXT,
    evidence_id BIGINT REFERENCES evidence(evidence_id), PRIMARY KEY(provider, job_id, snapshot_date)
);
CREATE TABLE IF NOT EXISTS company_event (
    event_id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entity(entity_id), event_type TEXT NOT NULL,
    event_date TIMESTAMPTZ NOT NULL, available_at TIMESTAMPTZ NOT NULL, event_detail TEXT,
    exposure_score DOUBLE PRECISION, confidence DOUBLE PRECISION, evidence_url TEXT,
    evidence_id BIGINT REFERENCES evidence(evidence_id)
);
CREATE TABLE IF NOT EXISTS score_run (
    score_run_id BIGSERIAL PRIMARY KEY, model_name TEXT NOT NULL, model_version TEXT NOT NULL,
    as_of_date DATE NOT NULL, entity_id TEXT NOT NULL REFERENCES entity(entity_id), peer_group TEXT,
    score_name TEXT NOT NULL, raw_value DOUBLE PRECISION, percentile DOUBLE PRECISION,
    robust_zscore DOUBLE PRECISION, weighted_score DOUBLE PRECISION, confidence DOUBLE PRECISION,
    assumptions_json JSONB, evidence_json JSONB, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS api_call_log (
    request_id TEXT PRIMARY KEY, provider TEXT NOT NULL, probe_id TEXT, requested_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ, http_status INTEGER, elapsed_ms DOUBLE PRECISION, attempts INTEGER,
    response_bytes BIGINT, quota_json JSONB, error_type TEXT, error_message_redacted TEXT
);
