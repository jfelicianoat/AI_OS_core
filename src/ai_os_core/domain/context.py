"""Modelos de dominio para ContextPackage y Context Engine (P07, P12, Caso C12).
Comentarios en español.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from ai_os_core.domain.contracts import ResourceReference, utc_now_iso
from ai_os_core.domain.security import ClassificationLevel


@dataclass(frozen=True)
class ContextPackage:
    """Paquete de contexto inmutable persistido bajo autoridad exclusiva de AI OS Core (C12)."""
    package_id: str
    goal_id: Optional[str]
    classification_level: ClassificationLevel
    snapshot_hash: str
    resources: List[ResourceReference] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    valid_until: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "package_id": self.package_id,
            "goal_id": self.goal_id,
            "classification_level": self.classification_level.value,
            "snapshot_hash": self.snapshot_hash,
            "resources": [r.to_dict() for r in self.resources],
            "payload": self.payload,
            "created_at": self.created_at,
            "valid_until": self.valid_until
        }
