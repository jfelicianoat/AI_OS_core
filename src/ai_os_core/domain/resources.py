"""Modelos de dominio para el Resource Graph ligero y relaciones.
Alineado con Normativa 0.6.1 (§1, §2) y caso M0-GRAPH.
Comentarios en español.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from .contracts import utc_now_iso


@dataclass
class ResourceNode:
    """Nodo del Resource Graph que representa un recurso federado."""
    resource_id: str
    resource_type: str
    owner_service: str
    revision: int = 1
    data: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class ResourceRelation:
    """Relación dirigida entre dos recursos en el grafo."""
    source_id: str
    target_id: str
    relation_type: str
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)
