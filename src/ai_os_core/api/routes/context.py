"""Endpoints REST para Context Engine y ContextPackage (P07, P12, C12, C21, C22).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ai_os_core.domain.contracts import ResourceReference
from ai_os_core.domain.security import ClassificationLevel, AuthorizationPrincipal
from ai_os_core.application.context_service import ContextService, SecurityAccessDeniedError
from ai_os_core.api.dependencies import get_context_service, enforce_token_grant

router = APIRouter(prefix="/api/v1/context", tags=["Context Engine"])


class ResourceReferenceDTO(BaseModel):
    resource_id: str
    resource_type: str
    owner_service: str
    revision: int = 1
    uri: Optional[str] = None


class CreateContextPackageRequest(BaseModel):
    goal_id: Optional[str] = None
    classification_level: str = "INTERNAL"
    resources: List[ResourceReferenceDTO] = []
    payload: Dict[str, Any] = {}
    principal_id: str = "system"
    principal_role: str = "agent"
    principal_clearance: str = "INTERNAL"
    principal_scopes: List[str] = ["context:build"]


@router.post("/packages", status_code=status.HTTP_201_CREATED)
def build_context_package(
    request: Request,
    req: CreateContextPackageRequest,
    service: ContextService = Depends(get_context_service)
):
    """Construye y persiste un paquete de contexto inmutable (C12, C21, C22)."""
    try:
        class_level = ClassificationLevel(req.classification_level)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel de clasificación inválido '{req.classification_level}'."
        )

    try:
        p_clearance = ClassificationLevel(req.principal_clearance)
    except ValueError:
        # Un clearance ilegible no se sustituye por uno por defecto: se rechaza
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clearance inválido '{req.principal_clearance}'. Válidos: {[c.value for c in ClassificationLevel]}"
        )

    # Lo que declara la petición no puede superar lo que concede su token
    enforce_token_grant(request, req.principal_scopes, req.principal_clearance)

    principal = AuthorizationPrincipal(
        principal_id=req.principal_id,
        role=req.principal_role,
        clearance_level=p_clearance,
        allowed_scopes=req.principal_scopes
    )

    resources = [
        ResourceReference(
            resource_id=r.resource_id,
            resource_type=r.resource_type,
            owner_service=r.owner_service,
            revision=r.revision,
            uri=r.uri
        )
        for r in req.resources
    ]

    try:
        pkg = service.build_context_package(
            goal_id=req.goal_id,
            classification_level=class_level,
            resources=resources,
            payload=req.payload,
            principal=principal
        )
        return pkg.to_dict()
    except SecurityAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/packages/{package_id}")
def get_context_package(
    package_id: str,
    service: ContextService = Depends(get_context_service)
):
    """Recupera un paquete de contexto por su identificador."""
    pkg = service.get_context_package(package_id)
    if not pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ContextPackage '{package_id}' no encontrado.")
    return pkg.to_dict()


@router.get("/snapshots/{snapshot_hash}")
def recover_historical_snapshot(
    snapshot_hash: str,
    service: ContextService = Depends(get_context_service)
):
    """Recupera la revisión exacta inmutable a partir de su hash histórico (C12)."""
    pkg = service.recover_historical_snapshot(snapshot_hash)
    if not pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Snapshot '{snapshot_hash}' no encontrado.")
    return pkg.to_dict()
