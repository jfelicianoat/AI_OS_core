"""Servicio de aplicación para Gestión y Concurrencia de Presupuestos (C09).
Comentarios en español.
"""

import uuid
from typing import Optional
from ai_os_core.domain.budget import BudgetReservation, BudgetAccount
from ai_os_core.domain.contracts import normalize_iso_utc, is_expired
from ai_os_core.infrastructure.db.repositories.budget_repo import (
    BudgetRepository,
    InsufficientBudgetError
)


class BudgetService:
    """Orquesta la asignación, reserva atómica y consumo de presupuestos (C09)."""

    def __init__(self, budget_repo: BudgetRepository):
        self.budget_repo = budget_repo

    def get_or_create_account(self, account_id: str, initial_balance: float = 100.0) -> BudgetAccount:
        """Obtiene o inicializa una cuenta de presupuesto."""
        return self.budget_repo.get_or_create_account(account_id, initial_balance)

    def create_account(self, account_id: str, balance: float) -> BudgetAccount:
        """Da de alta una cuenta de presupuesto con su saldo inicial."""
        return self.budget_repo.create_account(account_id, balance)

    def get_account(self, account_id: str) -> Optional[BudgetAccount]:
        """Consulta una cuenta sin crearla."""
        return self.budget_repo.get_account(account_id)

    def reserve_budget(
        self,
        account_id: str,
        amount: float,
        reservation_id: Optional[str] = None,
        expires_at: Optional[str] = None
    ) -> BudgetReservation:
        """Reserva saldo atómicamente garantizando prevención de sobregiros concurrentes (C09)."""
        rid = reservation_id or f"resv_{uuid.uuid4().hex[:12]}"
        normalized_expiry = normalize_iso_utc(expires_at) if expires_at else None
        if is_expired(normalized_expiry):
            raise ValueError(f"La reserva caducaría al nacer (expires_at={normalized_expiry}).")
        return self.budget_repo.create_reservation(rid, account_id, amount, normalized_expiry)

    def consume_budget(self, reservation_id: str) -> None:
        """Confirma el consumo del saldo reservado."""
        self.budget_repo.consume_reservation(reservation_id)

    def release_budget(self, reservation_id: str) -> None:
        """Libera la reserva reintegrando el disponible."""
        self.budget_repo.release_reservation(reservation_id)

    def get_reservation(self, reservation_id: str) -> Optional[BudgetReservation]:
        """Consulta el estado de una reserva."""
        return self.budget_repo.get_reservation(reservation_id)
