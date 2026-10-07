"""Modelos de dominio para Budget y Reservas concurrentes (Normativa 0.6.1 §4, Caso C09).
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Optional
from ai_os_core.domain.contracts import utc_now_iso


class BudgetStatus(str, Enum):
    """Estados del ciclo de vida de una reserva de presupuesto."""
    RESERVED = "reserved"
    CONSUMED = "consumed"
    RELEASED = "released"
    EXPIRED = "expired"


@dataclass
class BudgetReservation:
    """Reserva de saldo atómica previa a operaciones con coste."""
    reservation_id: str
    account_id: str
    amount: float
    status: BudgetStatus = BudgetStatus.RESERVED
    expires_at: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        res = asdict(self)
        res["status"] = self.status.value
        return res


@dataclass
class BudgetAccount:
    """Cuenta de presupuesto para imputación de costes."""
    account_id: str
    balance: float
    reserved: float

    @property
    def available(self) -> float:
        """Saldo disponible para nuevas reservas."""
        return max(0.0, self.balance - self.reserved)

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "balance": self.balance,
            "reserved": self.reserved,
            "available": self.available
        }
