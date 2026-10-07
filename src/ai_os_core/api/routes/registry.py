"""Endpoints REST para el Registro de Servicios y Capacidades (M0-REG, C23).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ai_os_core.api.schemas.common import (
    ServiceRegistrationRequest,
    CapabilityRegistrationRequest
)
from ai_os_core.domain.capabilities import (
    ServiceRegistration,
    CapabilityManifest,
    ServiceHealthStatus
)
from ai_os_core.application.service_registry import ServiceRegistryService
from ai_os_core.api.dependencies import get_service_registry

router = APIRouter(prefix="/api/v1", tags=["Service & Capability Registry"])


@router.post("/services", status_code=status.HTTP_201_CREATED)
def register_service(
    req: ServiceRegistrationRequest,
    registry: ServiceRegistryService = Depends(get_service_registry)
):
    """Registra un servicio federado tras validar allowlist y reglas SSRF."""
    try:
        health = ServiceHealthStatus(req.health_status)
    except ValueError:
        health = ServiceHealthStatus.HEALTHY

    service = ServiceRegistration(
        service_id=req.service_id,
        name=req.name,
        base_url=req.base_url,
        version=req.version,
        health_status=health,
        capabilities=req.capabilities,
        metadata=req.metadata
    )
    saved = registry.register_service(service)
    return saved.to_dict()


@router.get("/services")
def list_services(registry: ServiceRegistryService = Depends(get_service_registry)):
    """Lista todos los servicios federados registrados."""
    services = registry.list_services()
    return [s.to_dict() for s in services]


@router.get("/services/{service_id}")
def get_service(service_id: str, registry: ServiceRegistryService = Depends(get_service_registry)):
    """Obtiene el registro de un servicio por su ID."""
    service = registry.get_service(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Servicio '{service_id}' no encontrado.")
    return service.to_dict()


@router.post("/capabilities", status_code=status.HTTP_201_CREATED)
def register_capability(
    req: CapabilityRegistrationRequest,
    registry: ServiceRegistryService = Depends(get_service_registry)
):
    """Registra una capacidad declarada por un proveedor."""
    cap = CapabilityManifest(
        capability_id=req.capability_id,
        name=req.name,
        description=req.description,
        provider_service_id=req.provider_service_id,
        version=req.version,
        schema_version=req.schema_version,
        is_available=req.is_available,
        input_schema=req.input_schema,
        output_schema=req.output_schema
    )
    try:
        saved = registry.register_capability(cap)
        return saved.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/capabilities/{capability_id}")
def get_capability(capability_id: str, registry: ServiceRegistryService = Depends(get_service_registry)):
    """Obtiene una capacidad registrada por su ID."""
    cap = registry.get_capability(capability_id)
    if not cap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Capacidad '{capability_id}' no encontrada.")
    return cap.to_dict()
