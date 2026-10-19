CREATE SEQUENCE IF NOT EXISTS evidence_seq START 1;
CREATE SEQUENCE IF NOT EXISTS score_run_seq START 1;

CREATE TABLE IF NOT EXISTS entity (
    entity_id VARCHAR PRIMARY KEY,
    legal_name VARCHAR NOT NULL,
    country_code VARCHAR,
    entity_type VARCHAR,
    lei VARCHAR,
    cik VARCHAR,
    dart_corp_code VARCHAR,
    ico VARCHAR,
    industry_code VARCHAR,
    industry_system VARCHAR,
    valid_from DATE,
    valid_to DATE,
    source VARCHAR,
    collected_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS security (
    security_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    ticker VARCHAR,
    exchange VARCHAR,
    isin VARCHAR,
    currency VARCHAR,
    valid_from DATE,
    valid_to DATE,
    source VARCHAR
);

CREATE TABLE IF NOT EXISTS filing (
    filing_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    filing_type VARCHAR,
    period_end DATE,
    filing_date TIMESTAMP WITH TIME ZONE,
    available_at TIMESTAMP WITH TIME ZONE,
    revision_at TIMESTAMP WITH TIME ZONE,
    fiscal_year INTEGER,
    fiscal_period VARCHAR,
    accounting_standard VARCHAR,
    consolidated BOOLEAN,
    source_url VARCHAR,
    raw_sha256 VARCHAR
);

CREATE TABLE IF NOT EXISTS financial_fact (
    entity_id VARCHAR NOT NULL,
    filing_id VARCHAR,
    fact_key VARCHAR NOT NULL,
    concept_id VARCHAR NOT NULL,
    concept_name VARCHAR,
    statement_type VARCHAR,
    period_start DATE,
    period_end DATE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revision_at TIMESTAMP WITH TIME ZONE,
    value DOUBLE,
    unit VARCHAR,
    currency VARCHAR,
    segment_json JSON,
    source VARCHAR NOT NULL,
    evidence_id BIGINT,
    PRIMARY KEY(entity_id, fact_key, period_end, available_at, source)
);

CREATE TABLE IF NOT EXISTS market_price (
    security_id VARCHAR NOT NULL,
    price_date DATE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    adjusted_close DOUBLE,
    volume DOUBLE,
    dividend DOUBLE,
    split_factor DOUBLE,
    currency VARCHAR,
    source VARCHAR NOT NULL,
    evidence_id BIGINT,
    PRIMARY KEY(security_id, price_date, source)
);

CREATE TABLE IF NOT EXISTS macro_observation (
    series_id VARCHAR NOT NULL,
    country_code VARCHAR,
    industry_code VARCHAR,
    observation_date DATE NOT NULL,
    period_start DATE,
    period_end DATE,
    available_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revision_at TIMESTAMP WITH TIME ZONE,
    value DOUBLE,
    unit VARCHAR,
    frequency VARCHAR,
    source VARCHAR NOT NULL,
    evidence_id BIGINT,
    PRIMARY KEY(series_id, observation_date, available_at, source)
);

CREATE TABLE IF NOT EXISTS workforce_fact (
    entity_id VARCHAR NOT NULL,
    metric VARCHAR NOT NULL,
    period_end DATE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE,
    unit VARCHAR,
    scope VARCHAR,
    source VARCHAR NOT NULL,
    evidence_id BIGINT,
    PRIMARY KEY(entity_id, metric, period_end, available_at, source)
);

CREATE TABLE IF NOT EXISTS job_posting_snapshot (
    provider VARCHAR NOT NULL,
    job_id VARCHAR NOT NULL,
    entity_id VARCHAR,
    company_name VARCHAR,
    title VARCHAR,
    department VARCHAR,
    occupation_code VARCHAR,
    location VARCHAR,
    country_code VARCHAR,
    workplace_type VARCHAR,
    posted_at TIMESTAMP WITH TIME ZONE,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    snapshot_date DATE NOT NULL,
    is_active BOOLEAN,
    description_hash VARCHAR,
    evidence_id BIGINT,
    PRIMARY KEY(provider, job_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS company_event (
    event_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE NOT NULL,
    event_detail VARCHAR,
    exposure_score DOUBLE,
    confidence DOUBLE,
    evidence_url VARCHAR,
    evidence_id BIGINT
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id BIGINT DEFAULT nextval('evidence_seq') PRIMARY KEY,
    provider VARCHAR NOT NULL,
    request_id VARCHAR,
    source_url_redacted VARCHAR,
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE,
    raw_path VARCHAR,
    raw_sha256_before_redaction VARCHAR,
    stored_body_redacted BOOLEAN,
    http_status INTEGER,
    metadata_json JSON
);

CREATE TABLE IF NOT EXISTS score_run (
    score_run_id BIGINT DEFAULT nextval('score_run_seq') PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    model_version VARCHAR NOT NULL,
    as_of_date DATE NOT NULL,
    entity_id VARCHAR NOT NULL,
    peer_group VARCHAR,
    score_name VARCHAR NOT NULL,
    raw_value DOUBLE,
    percentile DOUBLE,
    robust_zscore DOUBLE,
    weighted_score DOUBLE,
    confidence DOUBLE,
    assumptions_json JSON,
    evidence_json JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS api_call_log (
    request_id VARCHAR PRIMARY KEY,
    provider VARCHAR NOT NULL,
    probe_id VARCHAR,
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    http_status INTEGER,
    elapsed_ms DOUBLE,
    attempts INTEGER,
    response_bytes BIGINT,
    quota_json JSON,
    error_type VARCHAR,
    error_message_redacted VARCHAR
);

CREATE TABLE IF NOT EXISTS identifier_mapping (
    identifier_type VARCHAR NOT NULL,
    identifier_value VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    confidence DOUBLE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(identifier_type, identifier_value, entity_id, source)
);

CREATE TABLE IF NOT EXISTS company_source_capability (
    entity_id VARCHAR NOT NULL,
    operation_id VARCHAR NOT NULL,
    capability VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    source_url VARCHAR,
    available_at TIMESTAMP WITH TIME ZONE,
    evidence_id BIGINT,
    PRIMARY KEY(entity_id, operation_id, capability, available_at)
);

CREATE TABLE IF NOT EXISTS field_availability (
    entity_id VARCHAR NOT NULL,
    operation_id VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    observation_date DATE,
    available_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY(entity_id, operation_id, field_name, available_at)
);

CREATE TABLE IF NOT EXISTS classification_history (
    entity_id VARCHAR NOT NULL,
    classified_at TIMESTAMP WITH TIME ZONE NOT NULL,
    capabilities_json JSON NOT NULL,
    correlation_ready BOOLEAN NOT NULL,
    causal_ready BOOLEAN NOT NULL,
    reasons_json JSON NOT NULL,
    PRIMARY KEY(entity_id, classified_at)
);

CREATE TABLE IF NOT EXISTS job_requirement (
    provider VARCHAR NOT NULL,
    job_id VARCHAR NOT NULL,
    requirement_id VARCHAR NOT NULL,
    text VARCHAR NOT NULL,
    requirement_status VARCHAR NOT NULL,
    evidence_scope VARCHAR NOT NULL,
    source_url VARCHAR,
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(provider, job_id, requirement_id, observed_at)
);

CREATE TABLE IF NOT EXISTS credential_evidence (
    requirement_id VARCHAR NOT NULL,
    source_url VARCHAR NOT NULL,
    source_kind VARCHAR NOT NULL,
    excerpt VARCHAR,
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(requirement_id, source_url)
);

CREATE TABLE IF NOT EXISTS requirement_verification (
    requirement_id VARCHAR NOT NULL,
    verification_status VARCHAR NOT NULL,
    verification_reason VARCHAR,
    verified_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(requirement_id, verified_at)
);

-- Atomic source lineage.  These records retain the meaning needed before any
-- DataFrame merge or company-level ranking.
CREATE TABLE IF NOT EXISTS source_snapshot (
    snapshot_id VARCHAR PRIMARY KEY,
    operation_id VARCHAR NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    source_url VARCHAR,
    raw_sha256 VARCHAR NOT NULL,
    coverage VARCHAR,
    disposition VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS atomic_fact (
    fact_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR,
    operation_id VARCHAR NOT NULL,
    fact_key VARCHAR NOT NULL,
    value_json JSON,
    unit VARCHAR,
    currency VARCHAR,
    period VARCHAR,
    concept VARCHAR,
    available_at TIMESTAMP WITH TIME ZONE,
    source_url VARCHAR,
    raw_record_id VARCHAR,
    snapshot_id VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS search_verdict (
    verdict_id VARCHAR PRIMARY KEY,
    subject_type VARCHAR NOT NULL,
    subject_id VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    verdict VARCHAR NOT NULL,
    reason VARCHAR,
    observed_value VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_revision (
    fact_id VARCHAR NOT NULL,
    revision_at TIMESTAMP WITH TIME ZONE NOT NULL,
    available_at TIMESTAMP WITH TIME ZONE,
    value_json JSON,
    source_snapshot_id VARCHAR NOT NULL,
    PRIMARY KEY(fact_id, revision_at)
);

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

