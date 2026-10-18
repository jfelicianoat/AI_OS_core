"""Endpoints REST para Proyección de Certificaciones (M0-CERT-PROJ).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from ai_os_core.domain.certifications import CertificationApplicability, EvaluationVerdict
from ai_os_core.application.certification_service import CertificationService
from ai_os_core.api.dependencies import get_certification_service

router = APIRouter(prefix="/api/v1/certifications", tags=["Certifications"])


class CertificationRegisterRequest(BaseModel):
    model_id: str
    capability_id: str
    version: str
    source_system: str
    evaluation_verdict: str
    is_applicable: bool
    revision: int = 1


@router.post("", status_code=status.HTTP_201_CREATED)
def register_certification(
    req: CertificationRegisterRequest,
    service: CertificationService = Depends(get_certification_service)
):
    """Registra la proyección de certificación con frescura y revisión (M0-CERT-PROJ)."""
    try:
        verdict = EvaluationVerdict(req.evaluation_verdict)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Veredicto inválido '{req.evaluation_verdict}'. Válidos: {[v.value for v in EvaluationVerdict]}"
        )

    cert = CertificationApplicability(
        model_id=req.model_id,
        capability_id=req.capability_id,
        version=req.version,
        source_system=req.source_system,
        evaluation_verdict=verdict,
        is_applicable=req.is_applicable,
        revision=req.revision
    )
    saved = service.register_certification(cert)
    return saved.to_dict()


@router.get("")
def list_certifications(service: CertificationService = Depends(get_certification_service)):
    """Lista todas las certificaciones proyectadas."""
    certs = service.list_certifications()
    return [c.to_dict() for c in certs]


@router.get("/{model_id:path}/{capability_id}/{version}")
def get_certification(
    model_id: str,
    capability_id: str,
    version: str,
    service: CertificationService = Depends(get_certification_service)
):
    """Consulta la aplicabilidad de una certificación específica."""
    cert = service.query_applicability(model_id, capability_id, version)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificación para '{model_id}:{capability_id}:{version}' no encontrada."
        )
    return cert.to_dict()
