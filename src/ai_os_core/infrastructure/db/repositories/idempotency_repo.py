"""Repositorio de idempotencia atómica (Caso crítico C01).
Comentarios en español.
"""

import sqlite3
from typing import Optional, Tuple
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.contracts import utc_now_iso


# response_code = 0 marca una clave reservada cuya operación sigue en curso (§8 in_progress)
IN_PROGRESS_CODE = 0


class IdempotencyConflictError(Exception):
    """Excepción lanzada cuando una clave de idempotencia se reutiliza con un cuerpo distinto (HTTP 409)."""
    pass


class IdempotencyInProgressError(Exception):
    """La misma clave tiene una operación idéntica todavía en curso (HTTP 409, reintentar después)."""
    pass


class IdempotencyRepository:
    """Gestiona el registro durable de solicitudes para garantizar idempotencia exacta."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _check_same_request(key: str, row: sqlite3.Row, operation_id: str, request_digest: str) -> None:
        """Lanza conflicto si la clave ya se usó para otra operación o con otro cuerpo."""
        if row["request_digest"] != request_digest or row["operation_id"] != operation_id:
            raise IdempotencyConflictError(
                f"Conflicto de idempotencia en clave '{key}': la solicitud difiere del registro previo."
            )

    def claim(
        self,
        key: str,
        principal_id: str,
        operation_id: str,
        request_digest: str
    ) -> Optional[Tuple[int, str]]:
        """Reserva la clave de forma atómica antes de ejecutar la operación.

        Devuelve None si la clave queda reservada para quien llama (debe ejecutar y
        luego llamar a save_response o release), o (código, cuerpo) si la operación
        ya terminó y hay que repetir su respuesta. Dos peticiones concurrentes con la
        misma clave no pueden ejecutar ambas: la segunda ve la reserva (C01).
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT operation_id, request_digest, response_code, response_body FROM idempotency_keys WHERE key = ?;",
                (key,)
            )
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    """
                    INSERT INTO idempotency_keys
                    (key, principal_id, operation_id, request_digest, response_code, response_body, created_at)
                    VALUES (?, ?, ?, ?, ?, '', ?);
                    """,
                    (key, principal_id, operation_id, request_digest, IN_PROGRESS_CODE, utc_now_iso())
                )
                return None

            self._check_same_request(key, row, operation_id, request_digest)
            if row["response_code"] == IN_PROGRESS_CODE:
                raise IdempotencyInProgressError(
                    f"La operación con clave '{key}' sigue en curso; reintenta más tarde."
                )
            return row["response_code"], row["response_body"]

    def release(self, key: str) -> None:
        """Libera una reserva cuya operación falló sin respuesta definitiva (5xx), para permitir el reintento."""
        with self.db_manager.transaction() as conn:
            conn.execute(
                "DELETE FROM idempotency_keys WHERE key = ? AND response_code = ?;",
                (key, IN_PROGRESS_CODE)
            )

    def find_cached_response(
        self,
        key: str,
        principal_id: str,
        operation_id: str,
        request_digest: str
    ) -> Optional[Tuple[int, str]]:
        """Busca una respuesta previamente registrada.
        Si la clave existe pero el digest o la operación difieren, lanza IdempotencyConflictError.
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT principal_id, operation_id, request_digest, response_code, response_body FROM idempotency_keys WHERE key = ?;",
                (key,)
            )
            row = cursor.fetchone()
            if not row or row["response_code"] == IN_PROGRESS_CODE:
                return None

            self._check_same_request(key, row, operation_id, request_digest)
            return row["response_code"], row["response_body"]
        finally:
            conn.close()

    def save_response(
        self,
        key: str,
        principal_id: str,
        operation_id: str,
        request_digest: str,
        response_code: int,
        response_body: str
    ) -> None:
        """Guarda la respuesta generada de forma atómica, completando la reserva si existe."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            now_iso = utc_now_iso()
            cursor.execute(
                """
                INSERT INTO idempotency_keys
                (key, principal_id, operation_id, request_digest, response_code, response_body, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    response_code = excluded.response_code,
                    response_body = excluded.response_body
                WHERE idempotency_keys.response_code = 0;
                """,
                (key, principal_id, operation_id, request_digest, response_code, response_body, now_iso)
            )
