"""Modelos de dominio para seguridad, principales y niveles de clasificación (C21, C22).
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Optional


class ClassificationLevel(str, Enum):
    """Niveles de clasificación de información con orden jerárquico estricto."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


# Mapa numérico para comparar techos de clasificación (C22)
CLASSIFICATION_ORDER = {
    ClassificationLevel.PUBLIC: 1,
    ClassificationLevel.INTERNAL: 2,
    ClassificationLevel.CONFIDENTIAL: 3,
    ClassificationLevel.RESTRICTED: 4,
}


@dataclass
class AuthorizationPrincipal:
    """Identidad de un principal autenticado con permisos y nivel de seguridad (C21, C22)."""
    principal_id: str
    role: str
    clearance_level: ClassificationLevel = ClassificationLevel.INTERNAL
    allowed_scopes: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def can_access_scope(self, required_scope: str) -> bool:
        """Verifica si el principal tiene concedido el scope (C21 Default DENY)."""
        if "*" in self.allowed_scopes:
            return True
        return required_scope in self.allowed_scopes

    def can_access_classification(self, requested_level: ClassificationLevel) -> bool:
        """Verifica que el nivel solicitado no exceda el techo del principal (C22)."""
        principal_rank = CLASSIFICATION_ORDER[self.clearance_level]
        requested_rank = CLASSIFICATION_ORDER[requested_level]
        return requested_rank <= principal_rank

    def to_dict(self) -> dict:
        res = asdict(self)
        res["clearance_level"] = self.clearance_level.value
        return res
