"""Endpoints REST para el Resource Graph e Identity Bindings (M0-GRAPH, C24).
Comentarios en español.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from ai_os_core.domain.resources import ResourceNode, ResourceRelation
from ai_os_core.domain.contracts import IdentityBinding
from ai_os_core.domain.errors import ConflictError
from ai_os_core.application.resource_service import ResourceService
from ai_os_core.api.dependencies import get_resource_service

router = APIRouter(prefix="/api/v1", tags=["Resource Graph & Identity"])


class ResourceRequest(BaseModel):
    resource_id: str = Field(..., min_length=1)
    resource_type: str
    owner_service: str
    revision: int = Field(default=1, ge=1)
    data: Dict[str, Any] = {}


class RelationRequest(BaseModel):
    source_id: str
    target_id: str
    relation_type: str


class IdentityBindingRequest(BaseModel):
    global_id: str
    native_id: str
    source_system: str
    adapter_revision: int = Field(default=1, ge=1)


@router.put("/resources")
def upsert_resource(req: ResourceRequest, service: ResourceService = Depends(get_resource_service)):
    """Proyecta un recurso federado. El propietario no cambia y la revisión no retrocede."""
    existing = service.get_resource(req.resource_id)
    if existing:
        if existing.owner_service != req.owner_service:
            raise ConflictError(
                f"El recurso '{req.resource_id}' pertenece a '{existing.owner_service}'; "
                f"'{req.owner_service}' no puede reescribirlo."
            )
        if req.revision < existing.revision:
            raise ConflictError(
                f"Revisión obsoleta {req.revision} para '{req.resource_id}' (actual {existing.revision})."
            )
    node = ResourceNode(
        resource_id=req.resource_id,
        resource_type=req.resource_type,
        owner_service=req.owner_service,
        revision=req.revision,
        data=req.data
    )
    if existing:
        node.created_at = existing.created_at
    service.save_resource(node)
    return service.get_resource(req.resource_id).to_dict()


@router.get("/resources/{resource_id}")
def get_resource(resource_id: str, service: ResourceService = Depends(get_resource_service)):
    """Obtiene un recurso del grafo con sus relaciones salientes."""
    node = service.get_resource(resource_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recurso '{resource_id}' no encontrado.")
    result = node.to_dict()
    result["relations"] = [r.to_dict() for r in service.get_relations_for(resource_id)]
    return result


@router.post("/resources/relations", status_code=status.HTTP_201_CREATED)
def add_relation(req: RelationRequest, service: ResourceService = Depends(get_resource_service)):
    """Añade una relación dirigida entre dos recursos existentes (repetirla no la duplica)."""
    for rid in (req.source_id, req.target_id):
        if not service.get_resource(rid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recurso '{rid}' no encontrado.")
    rel = ResourceRelation(source_id=req.source_id, target_id=req.target_id, relation_type=req.relation_type)
    return service.add_relation(rel).to_dict()


@router.put("/identity-bindings")
def bind_identity(req: IdentityBindingRequest, service: ResourceService = Depends(get_resource_service)):
    """Vincula una identidad global con el id nativo de un sistema (C24). La revisión de adaptador no retrocede."""
    existing = service.get_identity_binding(req.global_id, req.source_system)
    if existing and req.adapter_revision < existing.adapter_revision:
        raise ConflictError(
            f"adapter_revision {req.adapter_revision} obsoleta para '{req.global_id}@{req.source_system}' "
            f"(actual {existing.adapter_revision})."
        )
    binding = IdentityBinding(
        global_id=req.global_id,
        native_id=req.native_id,
        source_system=req.source_system,
        adapter_revision=req.adapter_revision
    )
    service.bind_identity(binding)
    return service.get_identity_binding(req.global_id, req.source_system).to_dict()


@router.get("/identity-bindings/{global_id}/{source_system}")
def get_identity_binding(global_id: str, source_system: str, service: ResourceService = Depends(get_resource_service)):
    """Resuelve el id nativo de una identidad global en un sistema concreto."""
    binding = service.get_identity_binding(global_id, source_system)
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay vinculación para '{global_id}' en '{source_system}'."
        )
    return binding.to_dict()
