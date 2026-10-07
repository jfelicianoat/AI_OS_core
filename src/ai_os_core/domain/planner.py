"""Modelos de dominio para Typed Planner y Autonomía Condicional (P14, P15).
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from ai_os_core.domain.contracts import utc_now_iso


class AutonomyLevel(str, Enum):
    """Niveles canónicos de autonomía con orden estricto A0..A5 (Normativa 0.6.1 §3.4)."""
    A0 = "A0"  # Completamente supervisado / manual
    A1 = "A1"  # Asistido con confirmación en cada paso
    A2 = "A2"  # Semi-autónomo con aprobación de inicio
    A3 = "A3"  # Autónomo condicionado a políticas y budget
    A4 = "A4"  # Alta autonomía con auditoría posterior
    A5 = "A5"  # Totalmente autónomo dentro del sandbox


AUTONOMY_ORDER = {
    AutonomyLevel.A0: 0,
    AutonomyLevel.A1: 1,
    AutonomyLevel.A2: 2,
    AutonomyLevel.A3: 3,
    AutonomyLevel.A4: 4,
    AutonomyLevel.A5: 5,
}


def combine_autonomy_ceilings(levels: List[AutonomyLevel]) -> AutonomyLevel:
    """Calcula el techo de autonomía como el mínimo de los niveles dados (§3.4)."""
    if not levels:
        return AutonomyLevel.A0
    sorted_levels = sorted(levels, key=lambda l: AUTONOMY_ORDER[l])
    return sorted_levels[0]


@dataclass
class ProposedTask:
    """Propuesta de tarea tipada dentro de un plan."""
    task_id: str
    title: str
    description: str
    assigned_service: str
    requires_human_approval: bool = False
    estimated_duration_sec: int = 60

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TypedPlanProposal:
    """Propuesta estructurada emitida por el Typed Planner (P14)."""
    proposal_id: str
    goal_id: str
    proposed_tasks: List[ProposedTask]
    autonomy_level: AutonomyLevel = AutonomyLevel.A1
    policy_decision: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "goal_id": self.goal_id,
            "proposed_tasks": [t.to_dict() for t in self.proposed_tasks],
            "autonomy_level": self.autonomy_level.value,
            "policy_decision": self.policy_decision,
            "created_at": self.created_at
        }


@dataclass
class EffectiveExecutionDecision:
    """Decisión de ejecución efectiva tras evaluar autonomía y approvals (P15)."""
    proposal_id: str
    approved_for_dispatch: bool
    effective_autonomy: AutonomyLevel
    reasons: List[str] = field(default_factory=list)
    decided_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "approved_for_dispatch": self.approved_for_dispatch,
            "effective_autonomy": self.effective_autonomy.value,
            "reasons": self.reasons,
            "decided_at": self.decided_at
        }
