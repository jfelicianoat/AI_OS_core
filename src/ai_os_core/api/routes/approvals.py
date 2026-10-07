"""Endpoints REST para Approvals y Consumo de Usos (C06, C07).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ai_os_core.api.schemas.common import CreateApprovalRequest, CommitApprovalUseRequest
import uuid
from pydantic import BaseModel
from ai_os_core.domain.approvals import (
    ApprovalAuthorization,
    ApprovalUse,
    ApprovalRevocation
)
from ai_os_core.application.approval_service import ApprovalService
from ai_os_core.infrastructure.db.repositories.approvals_repo import (
    ApprovalConflictError,
    ApprovalExecutionDeniedError
)
from ai_os_core.api.dependencies import get_approval_service

router = APIRouter(prefix="/api/v1/approvals", tags=["Approvals"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_authorization(
    req: CreateApprovalRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """Crea una autorización inmutable."""
    auth = ApprovalAuthorization(
        authorization_id=req.authorization_id,
        scope=req.scope,
        max_uses=req.max_uses,
        expires_at=req.expires_at,
        expected_digest=req.expected_digest,
        granted_by=req.granted_by
    )
    saved = service.create_authorization(auth)
    return saved.to_dict()


@router.post("/use")
def commit_use(
    req: CommitApprovalUseRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """Compromete un uso de la autorización de forma atómica aplicando reglas C06 y C07."""
    use = ApprovalUse(
        use_id=req.use_id,
        authorization_id=req.authorization_id,
        operation_id=req.operation_id,
        operation_digest=req.operation_digest
    )
    try:
        service.commit_use(use)
        return {"status": "committed", "use_id": use.use_id}
    except ApprovalConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ApprovalExecutionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{auth_id}/status")
def get_effective_state(
    auth_id: str,
    service: ApprovalService = Depends(get_approval_service)
):
    """Consulta el estado consolidado de la autorización."""
    state = service.get_effective_state(auth_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Autorización '{auth_id}' no encontrada.")
    return state.to_dict()


class RevokeApprovalRequest(BaseModel):
    revoked_by: str = "human"
    reason: str = "revocada manualmente"


@router.post("/{auth_id}/revoke")
def revoke_authorization(
    auth_id: str,
    req: RevokeApprovalRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """Revoca una autorización: ningún uso posterior se compromete (revocar dos veces es idempotente)."""
    service.revoke_authorization(
        ApprovalRevocation(
            revocation_id=f"rev_{uuid.uuid4().hex[:12]}",
            authorization_id=auth_id,
            revoked_by=req.revoked_by,
            reason=req.reason
        )
    )
    return service.get_effective_state(auth_id).to_dict()
