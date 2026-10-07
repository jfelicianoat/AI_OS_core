"""Repositorio SQLite para Autorizaciones y Usos de Aprobación (C06, C07).
Comentarios en español.
"""

import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.approvals import (
    ApprovalAuthorization,
    ApprovalUse,
    ApprovalRevocation,
    ApprovalEffectiveState,
    ApprovalStatus
)
from ai_os_core.domain.contracts import utc_now_iso, is_expired
from ai_os_core.domain.errors import ConflictError, NotFoundError


class ApprovalConflictError(Exception):
    """Lanzada cuando un operation_id se intenta reutilizar con un digest distinto (C07)."""
    pass


class ApprovalExecutionDeniedError(Exception):
    """Lanzada cuando la autorización ha expirado, ha sido revocada o sus usos están agotados (C06, C07)."""
    pass


class ApprovalsRepository:
    """Gestiona de forma atómica el ciclo de vida de autorizaciones y consumo de usos."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_authorization(self, auth: ApprovalAuthorization) -> None:
        """Persiste una autorización inmutable."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM approval_authorizations WHERE authorization_id = ?;", (auth.authorization_id,))
            if cursor.fetchone():
                raise ConflictError(f"La autorización '{auth.authorization_id}' ya existe y es inmutable.")
            cursor.execute(
                """
                INSERT INTO approval_authorizations (authorization_id, scope, max_uses, expires_at, expected_digest, granted_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (auth.authorization_id, auth.scope, auth.max_uses, auth.expires_at, auth.expected_digest, auth.granted_by, auth.created_at)
            )

    def get_authorization(self, auth_id: str) -> Optional[ApprovalAuthorization]:
        """Obtiene la autorización por ID."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approval_authorizations WHERE authorization_id = ?;", (auth_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ApprovalAuthorization(
                authorization_id=row["authorization_id"],
                scope=row["scope"],
                max_uses=row["max_uses"],
                expires_at=row["expires_at"],
                expected_digest=row["expected_digest"],
                granted_by=row["granted_by"],
                created_at=row["created_at"]
            )
        finally:
            conn.close()

    def revoke_authorization(self, revocation: ApprovalRevocation) -> None:
        """Registra la revocación formal de una autorización (revocar dos veces no añade nada)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM approval_authorizations WHERE authorization_id = ?;", (revocation.authorization_id,))
            if not cursor.fetchone():
                raise NotFoundError(f"Autorización '{revocation.authorization_id}' no encontrada.")
            cursor.execute("SELECT 1 FROM approval_revocations WHERE authorization_id = ?;", (revocation.authorization_id,))
            if cursor.fetchone():
                return
            cursor.execute(
                """
                INSERT INTO approval_revocations (revocation_id, authorization_id, revoked_by, reason, revoked_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (revocation.revocation_id, revocation.authorization_id, revocation.revoked_by, revocation.reason, revocation.revoked_at)
            )

    def commit_use(self, use: ApprovalUse, current_time_iso: Optional[str] = None) -> bool:
        """Compromete atómicamente un uso de la autorización aplicando las reglas C06 y C07."""
        now_str = current_time_iso or utc_now_iso()

        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()

            # 1. Obtener autorización
            cursor.execute("SELECT * FROM approval_authorizations WHERE authorization_id = ?;", (use.authorization_id,))
            auth_row = cursor.fetchone()
            if not auth_row:
                raise ApprovalExecutionDeniedError(f"Autorización '{use.authorization_id}' no encontrada.")

            max_uses = auth_row["max_uses"]
            expires_at = auth_row["expires_at"]

            # C06: Verificar expiración (comparando instantes, no texto)
            if is_expired(expires_at, now_str):
                raise ApprovalExecutionDeniedError(f"Autorización '{use.authorization_id}' ha expirado en {expires_at}.")

            # Verificar revocación
            cursor.execute("SELECT revocation_id FROM approval_revocations WHERE authorization_id = ?;", (use.authorization_id,))
            if cursor.fetchone():
                raise ApprovalExecutionDeniedError(f"Autorización '{use.authorization_id}' ha sido revocada.")

            # Aprobación exact_action: sólo vale para la operación cuyo digest se aprobó
            expected_digest = auth_row["expected_digest"]
            if expected_digest and use.operation_digest != expected_digest:
                raise ApprovalExecutionDeniedError(
                    f"La autorización '{use.authorization_id}' es exact_action y no cubre el digest '{use.operation_digest}'."
                )

            # 2. Consultar usos previos
            cursor.execute(
                "SELECT operation_id, operation_digest FROM approval_uses WHERE authorization_id = ?;",
                (use.authorization_id,)
            )
            uses = cursor.fetchall()

            # Caso C07: Reintento con mismo operation_id
            for u in uses:
                if u["operation_id"] == use.operation_id:
                    if u["operation_digest"] == use.operation_digest:
                        # Reintento idéntico legítimo: no consume uso extra
                        return True
                    else:
                        # Mismo operation_id con digest distinto -> Conflicto (C07)
                        raise ApprovalConflictError(
                            f"Conflicto C07: operation_id '{use.operation_id}' ya fue usado con un digest diferente."
                        )

            # Caso C07: Solo una operación consume el último uso
            if len(uses) >= max_uses:
                raise ApprovalExecutionDeniedError(
                    f"Autorización agotada: max_uses={max_uses}, usos actuales={len(uses)}."
                )

            # 3. Registrar el uso comprometido
            cursor.execute(
                """
                INSERT INTO approval_uses (use_id, authorization_id, operation_id, operation_digest, committed_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (use.use_id, use.authorization_id, use.operation_id, use.operation_digest, use.committed_at)
            )
            return True

    def get_effective_state(self, auth_id: str, current_time_iso: Optional[str] = None) -> Optional[ApprovalEffectiveState]:
        """Calcula el estado consolidado de la autorización."""
        now_str = current_time_iso or utc_now_iso()
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approval_authorizations WHERE authorization_id = ?;", (auth_id,))
            auth_row = cursor.fetchone()
            if not auth_row:
                return None

            max_uses = auth_row["max_uses"]
            expires_at = auth_row["expires_at"]

            cursor.execute("SELECT COUNT(*) FROM approval_revocations WHERE authorization_id = ?;", (auth_id,))
            is_revoked = cursor.fetchone()[0] > 0

            cursor.execute("SELECT COUNT(*) FROM approval_uses WHERE authorization_id = ?;", (auth_id,))
            used_count = cursor.fetchone()[0]

            expired = is_expired(expires_at, now_str)
            remaining_uses = max(0, max_uses - used_count)

            if is_revoked:
                status = ApprovalStatus.REVOKED
            elif expired:
                status = ApprovalStatus.EXPIRED
            elif remaining_uses == 0:
                status = ApprovalStatus.CONSUMED
            else:
                status = ApprovalStatus.ACTIVE

            return ApprovalEffectiveState(
                authorization_id=auth_id,
                status=status,
                max_uses=max_uses,
                used_count=used_count,
                remaining_uses=remaining_uses,
                is_revoked=is_revoked,
                is_expired=expired
            )
        finally:
            conn.close()
