"""Servicio de aplicación para el Protocolo Restore y comprobantes de operación (C15).
Comentarios en español.
"""

from typing import Optional
from ..domain.restore import (
    OperationReceipt,
    OperationExecutionStatus,
    OperationStatusQuery
)
from ..infrastructure.db.repositories.restore_repo import RestoreRepository


class RestoreService:
    """Orquesta la recuperación de estado de operaciones en subsistemas para evitar reenvíos duplicados (C15)."""

    def __init__(self, restore_repo: RestoreRepository):
        self.restore_repo = restore_repo

    def record_receipt(self, receipt: OperationReceipt) -> OperationReceipt:
        """Almacena o actualiza un comprobante de operación recibido."""
        self.restore_repo.save_receipt(receipt)
        return receipt

    def check_operation_status(self, query: OperationStatusQuery) -> OperationReceipt:
        """Consulta el estado conocido de una operación y devuelve el comprobante con la acción recomendada."""
        existing = self.restore_repo.get_receipt(query.operation_id)
        if existing:
            return existing

        # Si no se tiene registro previo, el estado es NOT_SEEN (reintento permitido)
        receipt = OperationReceipt(
            operation_id=query.operation_id,
            receiver_service=query.target_service_id,
            status=OperationExecutionStatus.NOT_SEEN,
            result_digest=None,
            evidence={"queried_target": query.target_service_id}
        )
        return receipt
