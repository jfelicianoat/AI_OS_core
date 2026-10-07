"""Repositorio SQLite para DecisionTraces y Auditoría append-only (M0-AUDIT).
Comentarios en español.
"""

import json
import sqlite3
from typing import List, Optional
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.audit import DecisionTrace, AuditRecord


class AuditRepository:
    """Gestiona el almacenamiento append-only de evidencias y decisiones del sistema."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def record_decision_trace(self, trace: DecisionTrace) -> None:
        """Almacena una traza de decisión inmutable."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO decision_traces (trace_id, decision_type, principal_id, resource_id, inputs_digest, decision_result, matched_rules_json, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    trace.trace_id,
                    trace.decision_type,
                    trace.principal_id,
                    trace.resource_id,
                    trace.inputs_digest,
                    trace.decision_result,
                    json.dumps(trace.matched_rules),
                    json.dumps(trace.metadata),
                    trace.created_at
                )
            )

    def record_audit(self, audit: AuditRecord) -> None:
        """Almacena un registro de auditoría append-only correlacionando operación y recursos."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_records (record_id, operation_id, principal_id, action, resource_type, resource_id, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    audit.record_id,
                    audit.operation_id,
                    audit.principal_id,
                    audit.action,
                    audit.resource_type,
                    audit.resource_id,
                    json.dumps(audit.details),
                    audit.created_at
                )
            )

    def list_audit_records_for_resource(self, resource_id: str) -> List[AuditRecord]:
        """Recupera el historial de auditoría para un recurso dado."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM audit_records WHERE resource_id = ? ORDER BY created_at ASC;",
                (resource_id,)
            )
            rows = cursor.fetchall()
            return [
                AuditRecord(
                    record_id=row["record_id"],
                    operation_id=row["operation_id"],
                    principal_id=row["principal_id"],
                    action=row["action"],
                    resource_type=row["resource_type"],
                    resource_id=row["resource_id"],
                    details=json.loads(row["details_json"]),
                    created_at=row["created_at"]
                )
                for row in rows
            ]
        finally:
            conn.close()
