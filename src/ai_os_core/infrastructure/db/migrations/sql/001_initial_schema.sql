-- Esquema inicial AI OS Core M0
-- Cumple con durabilidad SQLite WAL y aislamiento de control plane

CREATE TABLE IF NOT EXISTS schema_versions (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key TEXT PRIMARY KEY,
    principal_id TEXT NOT NULL,
    operation_id TEXT NOT NULL,
    request_digest TEXT NOT NULL,
    response_code INTEGER NOT NULL,
    response_body TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    parent_goal_id TEXT,
    owner_service TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(parent_goal_id) REFERENCES goals(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS objectives (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS services (
    service_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    version TEXT NOT NULL,
    health_status TEXT NOT NULL,
    capabilities_json TEXT NOT NULL DEFAULT '[]',
    last_seen TEXT NOT NULL,
    registered_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS capabilities (
    capability_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    provider_service_id TEXT NOT NULL,
    version TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1,
    input_schema_json TEXT NOT NULL DEFAULT '{}',
    output_schema_json TEXT NOT NULL DEFAULT '{}',
    registered_at TEXT NOT NULL,
    FOREIGN KEY(provider_service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resources (
    resource_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    owner_service TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_relations (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(source_id, target_id, relation_type)
);

CREATE TABLE IF NOT EXISTS identity_bindings (
    global_id TEXT NOT NULL,
    native_id TEXT NOT NULL,
    source_system TEXT NOT NULL,
    adapter_revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    PRIMARY KEY(global_id, source_system)
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    producer_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    stream_epoch INTEGER NOT NULL,
    source_sequence INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    revision INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    state_digest TEXT,
    quarantine INTEGER NOT NULL DEFAULT 0,
    quarantine_reason TEXT,
    created_at TEXT NOT NULL,
    received_at TEXT NOT NULL,
    UNIQUE(producer_id, stream_id, stream_epoch, source_sequence)
);

CREATE TABLE IF NOT EXISTS replay_cursors (
    consumer_id TEXT NOT NULL,
    producer_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    stream_epoch INTEGER NOT NULL,
    last_processed_sequence INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(consumer_id, producer_id, stream_id, stream_epoch)
);

CREATE TABLE IF NOT EXISTS replay_gaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producer_id TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    stream_epoch INTEGER NOT NULL,
    expected_sequence INTEGER NOT NULL,
    received_sequence INTEGER NOT NULL,
    detected_at TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    policy_key TEXT NOT NULL,
    scope TEXT NOT NULL,
    decision_if_matched TEXT NOT NULL,
    condition_mode TEXT NOT NULL,
    conditions_json TEXT NOT NULL,
    unconditional INTEGER NOT NULL DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1,
    revision INTEGER NOT NULL DEFAULT 1,
    constraints_json TEXT NOT NULL DEFAULT '{}',
    obligations_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_authorizations (
    authorization_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL,
    max_uses INTEGER NOT NULL DEFAULT 1,
    expires_at TEXT,
    expected_digest TEXT,
    granted_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_uses (
    use_id TEXT PRIMARY KEY,
    authorization_id TEXT NOT NULL,
    operation_id TEXT NOT NULL,
    operation_digest TEXT NOT NULL,
    committed_at TEXT NOT NULL,
    FOREIGN KEY(authorization_id) REFERENCES approval_authorizations(authorization_id)
);

CREATE TABLE IF NOT EXISTS approval_revocations (
    revocation_id TEXT PRIMARY KEY,
    authorization_id TEXT NOT NULL,
    revoked_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    revoked_at TEXT NOT NULL,
    FOREIGN KEY(authorization_id) REFERENCES approval_authorizations(authorization_id)
);

CREATE TABLE IF NOT EXISTS operation_receipts (
    operation_id TEXT PRIMARY KEY,
    receiver_service TEXT NOT NULL,
    status TEXT NOT NULL,
    result_digest TEXT,
    evidence_json TEXT NOT NULL DEFAULT '{}',
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_traces (
    trace_id TEXT PRIMARY KEY,
    decision_type TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    resource_id TEXT,
    inputs_digest TEXT NOT NULL,
    decision_result TEXT NOT NULL,
    matched_rules_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_records (
    record_id TEXT PRIMARY KEY,
    operation_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
