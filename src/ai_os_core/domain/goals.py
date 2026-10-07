"""Modelos de dominio para Goals y Objectives.
AI OS Core es la autoridad canónica para Goals y Objectives (Normativa 0.6.1 §1).
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Optional, Any
from .contracts import utc_now_iso


class GoalStatus(str, Enum):
    """Estados del ciclo de vida de un Goal u Objective."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """Entidad Goal (Objetivo de alto nivel)."""
    id: str
    title: str
    description: str
    owner_service: str = "ai_os_core"
    status: GoalStatus = GoalStatus.ACTIVE
    revision: int = 1
    parent_goal_id: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def update_status(self, new_status: GoalStatus) -> None:
        """Actualiza el estado incrementando la revisión de forma monótona."""
        self.status = new_status
        self.revision += 1
        self.updated_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        res = asdict(self)
        res["status"] = self.status.value
        return res


@dataclass
class Objective:
    """Entidad Objective (Objetivo intermedio o subtarea vinculada a un Goal)."""
    id: str
    goal_id: str
    title: str
    description: str = ""
    status: GoalStatus = GoalStatus.ACTIVE
    revision: int = 1
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def update_status(self, new_status: GoalStatus) -> None:
        """Actualiza el estado e incrementa la revisión."""
        self.status = new_status
        self.revision += 1
        self.updated_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        res = asdict(self)
        res["status"] = self.status.value
        return res
