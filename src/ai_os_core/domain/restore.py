"""Modelos de dominio para el protocolo de Restore y estado de operaciones.
Alineado con Normativa 0.6.1 (§7) y caso crítico C15.
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from .contracts import utc_now_iso


class OperationExecutionStatus(str, Enum):
    """Estados canónicos de ejecución de una operación externa o interna (§7)."""
    NOT_SEEN = "not_seen"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED_TERMINAL = "failed_terminal"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OperationStatusQuery:
    """Consulta de estado enviada a un receptor o subsistema."""
    operation_id: str
    target_service_id: str
    queried_at: str = field(default_factory=utc_now_iso)


@dataclass
class OperationReceipt:
    """Evidencia durable del resultado de una operación para deduplicación y recuperación."""
    operation_id: str
    receiver_service: str
    status: OperationExecutionStatus
    result_digest: Optional[str] = None
    evidence: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=utc_now_iso)

    def determine_action(self) -> str:
        """Determina la acción a seguir según las reglas normativas de §7."""
        if self.status == OperationExecutionStatus.SUCCEEDED:
            return "reconstruct_state_no_resend"
        if self.status in (OperationExecutionStatus.ACCEPTED, OperationExecutionStatus.IN_PROGRESS):
            return "follow_up_no_resend"
        if self.status == OperationExecutionStatus.NOT_SEEN:
            return "retry_allowed"
        if self.status in (OperationExecutionStatus.FAILED_TERMINAL, OperationExecutionStatus.CANCELLED):
            return "do_not_resend_without_new_decision"
        return "manual_reconciliation_required"

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        res = asdict(self)
        res["status"] = self.status.value
        res["recommended_action"] = self.determine_action()
        return res
