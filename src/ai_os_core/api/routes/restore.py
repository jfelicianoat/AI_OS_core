"""Endpoints REST para el Protocolo Restore y deduplicación de reenvíos (C15).
Comentarios en español.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from ai_os_core.api.schemas.common import OperationStatusQueryRequest, OperationReceiptDTO
from ai_os_core.domain.restore import OperationStatusQuery, OperationReceipt, OperationExecutionStatus
from ai_os_core.application.restore_service import RestoreService
from ai_os_core.api.dependencies import get_restore_service, get_flows_repo
from ai_os_core.api.routes.flows import flow_id_from, record_safely, reporter
from ai_os_core.infrastructure.db.repositories.flows_repo import FlowsRepository

router = APIRouter(prefix="/api/v1/operations", tags=["Restore"])


@router.post("/status", response_model=OperationReceiptDTO)
def query_operation_status(
    req: OperationStatusQueryRequest,
    service: RestoreService = Depends(get_restore_service)
):
    """Consulta el comprobante de ejecución de una operación para aplicar reglas de recuperación C15."""
    query = OperationStatusQuery(
        operation_id=req.operation_id,
        target_service_id=req.target_service_id
    )
    receipt = service.check_operation_status(query)
    return receipt.to_dict()


class RecordReceiptRequest(BaseModel):
    operation_id: str
    receiver_service: str
    status: str
    result_digest: Optional[str] = None
    evidence: Dict[str, Any] = {}


@router.post("/receipts", response_model=OperationReceiptDTO, status_code=status.HTTP_201_CREATED)
def record_operation_receipt(
    req: RecordReceiptRequest,
    request: Request,
    service: RestoreService = Depends(get_restore_service),
    flows: FlowsRepository = Depends(get_flows_repo)
):
    """Registra (o actualiza) el comprobante que un receptor emite sobre una operación (§7)."""
    try:
        op_status = OperationExecutionStatus(req.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido '{req.status}'. Válidos: {[s.value for s in OperationExecutionStatus]}"
        )
    receipt = OperationReceipt(
        operation_id=req.operation_id,
        receiver_service=req.receiver_service,
        status=op_status,
        result_digest=req.result_digest,
        evidence=req.evidence
    )
    saved = service.record_receipt(receipt).to_dict()
    # Monitor: el recibo cierra el paso en el flujo de la petición (evidence.flow_id) o en el suyo propio
    record_safely(flows, flow_id=flow_id_from(req.evidence, req.operation_id), kind="receipt",
                  source=reporter(request, "desconocida"), target="core", summary=req.status,
                  details={"operation_id": req.operation_id, "status": req.status,
                           "receiver_service": req.receiver_service})
    return saved
