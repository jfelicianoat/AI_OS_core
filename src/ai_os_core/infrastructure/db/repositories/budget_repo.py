"""Repositorio SQLite para Budget y concurrencia de reservas (Caso C09).
Comentarios en español.
"""

import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.budget import (
    BudgetReservation,
    BudgetAccount,
    BudgetStatus
)
from ai_os_core.domain.contracts import utc_now_iso, is_expired
from ai_os_core.domain.errors import ConflictError, NotFoundError


class InsufficientBudgetError(Exception):
    """Lanzada cuando el saldo disponible no permite cubrir la reserva solicitada."""
    pass


class BudgetRepository:
    """Gestiona de forma atómica el saldo, reservas y consumo de presupuestos (C09)."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_or_create_account(self, account_id: str, initial_balance: float = 100.0) -> BudgetAccount:
        """Obtiene la cuenta de presupuesto o la crea si no existe."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance, reserved FROM budget_accounts WHERE account_id = ?;", (account_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO budget_accounts (account_id, balance, reserved) VALUES (?, ?, 0.0);",
                    (account_id, initial_balance)
                )
                return BudgetAccount(account_id=account_id, balance=initial_balance, reserved=0.0)
            return BudgetAccount(account_id=account_id, balance=row["balance"], reserved=row["reserved"])

    def create_account(self, account_id: str, balance: float) -> BudgetAccount:
        """Da de alta una cuenta con su saldo inicial; no sobrescribe una existente."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM budget_accounts WHERE account_id = ?;", (account_id,))
            if cursor.fetchone():
                raise ConflictError(f"La cuenta de presupuesto '{account_id}' ya existe.")
            cursor.execute(
                "INSERT INTO budget_accounts (account_id, balance, reserved) VALUES (?, ?, 0.0);",
                (account_id, balance)
            )
            return BudgetAccount(account_id=account_id, balance=balance, reserved=0.0)

    def get_account(self, account_id: str) -> Optional[BudgetAccount]:
        """Consulta una cuenta (sin crearla); antes devuelve al disponible lo ya caducado."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            self._expire_stale_reservations(cursor, account_id)
            cursor.execute("SELECT balance, reserved FROM budget_accounts WHERE account_id = ?;", (account_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return BudgetAccount(account_id=account_id, balance=row["balance"], reserved=row["reserved"])

    @staticmethod
    def _expire_stale_reservations(cursor: sqlite3.Cursor, account_id: str) -> None:
        """Devuelve al disponible las reservas caducadas que nadie consumió."""
        cursor.execute(
            "SELECT reservation_id, amount, expires_at FROM budget_reservations "
            "WHERE account_id = ? AND status = ? AND expires_at IS NOT NULL;",
            (account_id, BudgetStatus.RESERVED.value)
        )
        for row in cursor.fetchall():
            if is_expired(row["expires_at"]):
                cursor.execute(
                    "UPDATE budget_accounts SET reserved = reserved - ? WHERE account_id = ?;",
                    (row["amount"], account_id)
                )
                cursor.execute(
                    "UPDATE budget_reservations SET status = ? WHERE reservation_id = ?;",
                    (BudgetStatus.EXPIRED.value, row["reservation_id"])
                )

    def create_reservation(
        self,
        reservation_id: str,
        account_id: str,
        amount: float,
        expires_at: Optional[str] = None
    ) -> BudgetReservation:
        """Crea una reserva de saldo garantizando atomicidad y prevención de carreras (C09)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()

            # Asegurar existencia de cuenta
            cursor.execute("SELECT 1 FROM budget_accounts WHERE account_id = ?;", (account_id,))
            if not cursor.fetchone():
                raise NotFoundError(f"Cuenta de presupuesto '{account_id}' no encontrada.")

            cursor.execute("SELECT 1 FROM budget_reservations WHERE reservation_id = ?;", (reservation_id,))
            if cursor.fetchone():
                raise ConflictError(f"La reserva '{reservation_id}' ya existe.")

            self._expire_stale_reservations(cursor, account_id)
            cursor.execute("SELECT balance, reserved FROM budget_accounts WHERE account_id = ?;", (account_id,))
            row = cursor.fetchone()

            balance = row["balance"]
            reserved = row["reserved"]
            available = balance - reserved

            # Caso C09: Dos reservas concurrentes de 80 sobre 100 no pueden tener éxito ambas
            if available < amount:
                raise InsufficientBudgetError(
                    f"Saldo insuficiente: disponible={available}, solicitado={amount}."
                )

            # Incrementar saldo reservado
            cursor.execute(
                "UPDATE budget_accounts SET reserved = reserved + ? WHERE account_id = ?;",
                (amount, account_id)
            )

            # Insertar registro de reserva
            now = utc_now_iso()
            res = BudgetReservation(
                reservation_id=reservation_id,
                account_id=account_id,
                amount=amount,
                status=BudgetStatus.RESERVED,
                expires_at=expires_at,
                created_at=now
            )
            cursor.execute(
                """
                INSERT INTO budget_reservations (reservation_id, account_id, amount, status, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (res.reservation_id, res.account_id, res.amount, res.status.value, res.expires_at, res.created_at)
            )
            return res

    def consume_reservation(self, reservation_id: str) -> None:
        """Convierte una reserva en consumo definitivo deduciendo del balance principal."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_id, amount, status FROM budget_reservations WHERE reservation_id = ?;",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundError(f"Reserva '{reservation_id}' no encontrada.")

            self._expire_stale_reservations(cursor, row["account_id"])
            cursor.execute("SELECT status FROM budget_reservations WHERE reservation_id = ?;", (reservation_id,))
            current_status = cursor.fetchone()["status"]
            if current_status != BudgetStatus.RESERVED.value:
                raise ConflictError(f"La reserva '{reservation_id}' ya no está en estado reservado ({current_status}).")

            account_id = row["account_id"]
            amount = row["amount"]

            # Deducir tanto del balance como del reservado
            cursor.execute(
                "UPDATE budget_accounts SET balance = balance - ?, reserved = reserved - ? WHERE account_id = ?;",
                (amount, amount, account_id)
            )
            cursor.execute(
                "UPDATE budget_reservations SET status = ? WHERE reservation_id = ?;",
                (BudgetStatus.CONSUMED.value, reservation_id)
            )

    def release_reservation(self, reservation_id: str) -> None:
        """Libera una reserva no utilizada devolviendo el saldo al disponible."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_id, amount, status FROM budget_reservations WHERE reservation_id = ?;",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundError(f"Reserva '{reservation_id}' no encontrada.")

            if row["status"] == BudgetStatus.CONSUMED.value:
                raise ConflictError(f"La reserva '{reservation_id}' ya fue consumida y no puede liberarse.")

            # Liberar dos veces es idempotente: una reserva ya liberada o caducada no cambia
            if row["status"] == BudgetStatus.RESERVED.value:
                account_id = row["account_id"]
                amount = row["amount"]
                cursor.execute(
                    "UPDATE budget_accounts SET reserved = reserved - ? WHERE account_id = ?;",
                    (amount, account_id)
                )
                cursor.execute(
                    "UPDATE budget_reservations SET status = ? WHERE reservation_id = ?;",
                    (BudgetStatus.RELEASED.value, reservation_id)
                )

    def get_reservation(self, reservation_id: str) -> Optional[BudgetReservation]:
        """Obtiene una reserva por su ID, con la caducidad ya aplicada."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT account_id FROM budget_reservations WHERE reservation_id = ?;", (reservation_id,))
            row = cursor.fetchone()
            if not row:
                return None
            self._expire_stale_reservations(cursor, row["account_id"])
            cursor.execute("SELECT * FROM budget_reservations WHERE reservation_id = ?;", (reservation_id,))
            row = cursor.fetchone()
            return BudgetReservation(
                reservation_id=row["reservation_id"],
                account_id=row["account_id"],
                amount=row["amount"],
                status=BudgetStatus(row["status"]),
                expires_at=row["expires_at"],
                created_at=row["created_at"]
            )
