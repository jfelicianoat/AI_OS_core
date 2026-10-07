"""Servicio de aplicación para Gestión de Approvals y Autorizaciones (C06, C07).
Comentarios en español.
"""

from dataclasses import replace
from typing import Optional
from ..domain.contracts import normalize_iso_utc
from ..domain.approvals import (
    ApprovalAuthorization,
    ApprovalUse,
    ApprovalRevocation,
    ApprovalEffectiveState
)
from ..infrastructure.db.repositories.approvals_repo import (
    ApprovalsRepository,
    ApprovalConflictError,
    ApprovalExecutionDeniedError
)


class ApprovalService:
    """Orquesta la emisión de autorizaciones, revocaciones y consumo atómico de usos."""

    def __init__(self, approvals_repo: ApprovalsRepository):
        self.approvals_repo = approvals_repo

    def create_authorization(self, auth: ApprovalAuthorization) -> ApprovalAuthorization:
        """Emite una nueva autorización inmutable."""
        if auth.max_uses < 1:
            raise ValueError("max_uses debe ser al menos 1.")
        if auth.expires_at:
            auth = replace(auth, expires_at=normalize_iso_utc(auth.expires_at))
        self.approvals_repo.save_authorization(auth)
        return auth

    def commit_use(self, use: ApprovalUse, current_time_iso: Optional[str] = None) -> bool:
        """Compromete un uso de la autorización de forma atómica aplicando reglas C06 y C07."""
        return self.approvals_repo.commit_use(use, current_time_iso)

    def revoke_authorization(self, revocation: ApprovalRevocation) -> None:
        """Revoca formalmente una autorización."""
        self.approvals_repo.revoke_authorization(revocation)

    def get_effective_state(self, auth_id: str, current_time_iso: Optional[str] = None) -> Optional[ApprovalEffectiveState]:
        """Obtiene el estado efectivo consolidado de una autorización."""
        return self.approvals_repo.get_effective_state(auth_id, current_time_iso)
