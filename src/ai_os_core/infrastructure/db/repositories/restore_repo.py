"""Repositorio SQLite para OperationReceipts y protocolo Restore (C15).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.restore import OperationReceipt, OperationExecutionStatus
from ai_os_core.domain.errors import ConflictError

_S = OperationExecutionStatus
_TERMINAL = {_S.SUCCEEDED, _S.FAILED_TERMINAL, _S.CANCELLED}
# Orden de avance de los estados no terminales; 'unknown' y los terminales quedan fuera (siempre avanzan).
_PROGRESS = {_S.NOT_SEEN: 0, _S.ACCEPTED: 1, _S.IN_PROGRESS: 2}


class RestoreRepository:
    """Gestiona la persistencia de comprobantes de operación (OperationReceipt)."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_receipt(self, receipt: OperationReceipt) -> None:
        """Guarda o actualiza el comprobante de operación durablemente.

        El estado sólo avanza: un recibo terminal no se reescribe y uno en curso no vuelve
        atrás; si no, un 'not_seen' tardío convertiría un 'succeeded' en 'retry_allowed'.
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT receiver_service, status FROM operation_receipts WHERE operation_id = ?;",
                (receipt.operation_id,)
            )
            row = cursor.fetchone()
            if row:
                old = OperationExecutionStatus(row["status"])
                new = receipt.status
                if row["receiver_service"] != receipt.receiver_service:
                    raise ConflictError(
                        f"La operación '{receipt.operation_id}' pertenece a '{row['receiver_service']}'; "
                        f"'{receipt.receiver_service}' no puede emitir su recibo."
                    )
                if old != new and (
                    old in _TERMINAL or _PROGRESS.get(new, len(_PROGRESS)) < _PROGRESS.get(old, 0)
                ):
                    raise ConflictError(
                        f"Transición de recibo no permitida para '{receipt.operation_id}': {old.value} -> {new.value}."
                    )
            cursor.execute(
                """
                INSERT INTO operation_receipts (operation_id, receiver_service, status, result_digest, evidence_json, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(operation_id) DO UPDATE SET
                    status = excluded.status,
                    result_digest = excluded.result_digest,
                    evidence_json = excluded.evidence_json,
                    recorded_at = excluded.recorded_at;
                """,
                (
                    receipt.operation_id,
                    receipt.receiver_service,
                    receipt.status.value,
                    receipt.result_digest,
                    json.dumps(receipt.evidence),
                    receipt.recorded_at
                )
            )

    def get_receipt(self, operation_id: str) -> Optional[OperationReceipt]:
        """Obtiene un comprobante por ID de operación."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operation_receipts WHERE operation_id = ?;", (operation_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return OperationReceipt(
                operation_id=row["operation_id"],
                receiver_service=row["receiver_service"],
                status=OperationExecutionStatus(row["status"]),
                result_digest=row["result_digest"],
                evidence=json.loads(row["evidence_json"]),
                recorded_at=row["recorded_at"]
            )
        finally:
            conn.close()
