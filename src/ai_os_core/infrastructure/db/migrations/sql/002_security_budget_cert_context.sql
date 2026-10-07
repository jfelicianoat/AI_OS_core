-- Migración 002: Tablas de seguridad, budget concurrente, certificaciones, outbox, context y planner
-- Cumple con P02, P07, P12, P14, P15

CREATE TABLE IF NOT EXISTS budget_accounts (
    account_id TEXT PRIMARY KEY,
    balance REAL NOT NULL DEFAULT 0.0,
    reserved REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS budget_reservations (
    reservation_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES budget_accounts(account_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certification_applicability (
    model_id TEXT NOT NULL,
    capability_id TEXT NOT NULL,
    version TEXT NOT NULL,
    source_system TEXT NOT NULL,
    evaluation_verdict TEXT NOT NULL,
    is_applicable INTEGER NOT NULL,
    last_verified_at TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(model_id, capability_id, version)
);

CREATE TABLE IF NOT EXISTS command_outbox (
    command_id TEXT PRIMARY KEY,
    operation_id TEXT NOT NULL,
    destination_service TEXT NOT NULL,
    command_payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    dispatched_at TEXT
);

CREATE TABLE IF NOT EXISTS context_packages (
    package_id TEXT PRIMARY KEY,
    goal_id TEXT,
    classification_level TEXT NOT NULL,
    snapshot_hash TEXT NOT NULL,
    package_data_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    valid_until TEXT
);

CREATE TABLE IF NOT EXISTS plan_proposals (
    proposal_id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    proposed_tasks_json TEXT NOT NULL,
    policy_decision_json TEXT NOT NULL,
    autonomy_level TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS principals (
    principal_id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    clearance_level TEXT NOT NULL,
    allowed_scopes_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
