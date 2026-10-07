"""Modelos de dominio para el registro de servicios y catálogo de capacidades.
Cumple con requisitos M0-REG y C23 (Seguridad de Servicios y Allowlist).
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from .contracts import utc_now_iso


class ServiceHealthStatus(str, Enum):
    """Estado de salud reportado u observado de un servicio."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class ServiceRegistration:
    """Registro de un servicio participante en el ecosistema AI OS."""
    service_id: str
    name: str
    base_url: str
    version: str = "1.0.0"
    health_status: ServiceHealthStatus = ServiceHealthStatus.HEALTHY
    capabilities: list[str] = field(default_factory=list)
    last_seen: str = field(default_factory=utc_now_iso)
    registered_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        res = asdict(self)
        res["health_status"] = self.health_status.value
        return res


@dataclass
class CapabilityManifest:
    """Manifiesto formal de una capacidad declarada por un servicio proveedor."""
    capability_id: str
    name: str
    description: str
    provider_service_id: str
    version: str = "1.0.0"
    schema_version: str = "1.0"
    is_available: bool = True
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass
class SkillManifest:
    """Referencia tipada a una habilidad ejecutable en un agente."""
    skill_id: str
    name: str
    provider_service_id: str
    version: str = "1.0.0"
    content_hash: str = ""
    is_certified: bool = False
    registered_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)
