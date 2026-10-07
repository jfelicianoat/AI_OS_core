"""Servicio de aplicación para Registro de Servicios y Capacidades (M0-REG, C23).
Comentarios en español.
"""

from typing import Optional, List
from ..domain.capabilities import ServiceRegistration, CapabilityManifest, ServiceHealthStatus
from ..infrastructure.db.repositories.services_repo import ServicesRepository
from ..infrastructure.http.security_client import SecurityHttpClientValidator


class ServiceRegistryService:
    """Orquesta el registro seguro de servicios y catálogo de capacidades."""

    def __init__(self, services_repo: ServicesRepository, security_validator: Optional[SecurityHttpClientValidator] = None):
        self.services_repo = services_repo
        self.security_validator = security_validator or SecurityHttpClientValidator()

    def register_service(self, service: ServiceRegistration) -> ServiceRegistration:
        """Registra un servicio tras validar que su endpoint no infringe políticas SSRF (C23)."""
        self.security_validator.validate_url(service.base_url)
        self.services_repo.register_service(service)
        return service

    def get_service(self, service_id: str) -> Optional[ServiceRegistration]:
        """Obtiene un servicio registrado."""
        return self.services_repo.get_service(service_id)

    def list_services(self) -> List[ServiceRegistration]:
        """Lista todos los servicios."""
        return self.services_repo.list_services()

    def register_capability(self, capability: CapabilityManifest) -> CapabilityManifest:
        """Registra una capacidad asegurando consistencia con el proveedor."""
        self.services_repo.register_capability(capability)
        return capability

    def get_capability(self, capability_id: str) -> Optional[CapabilityManifest]:
        """Obtiene una capacidad por ID."""
        return self.services_repo.get_capability(capability_id)
