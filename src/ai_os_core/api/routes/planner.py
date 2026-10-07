"""Endpoints REST para Typed Planner y Autonomía Condicional (P14, P15).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ai_os_core.domain.planner import (
    TypedPlanProposal,
    ProposedTask,
    AutonomyLevel
)
from ai_os_core.domain.security import AuthorizationPrincipal, ClassificationLevel
from ai_os_core.application.planner_service import PlannerService
from ai_os_core.application.context_service import SecurityAccessDeniedError
from ai_os_core.api.dependencies import get_planner_service

router = APIRouter(prefix="/api/v1/planner", tags=["Typed Planner"])


class ProposedTaskDTO(BaseModel):
    task_id: str
    title: str
    description: str
    assigned_service: str
    requires_human_approval: bool = False
    estimated_duration_sec: int = 60


class CreatePlanProposalRequest(BaseModel):
    goal_id: str
    tasks: List[ProposedTaskDTO]
    requested_autonomy: str = "A1"
    policy_decision: Dict[str, Any] = {}
    principal_id: str = "system"
    principal_role: str = "planner"
    principal_scopes: List[str] = ["planner:propose"]


class DecideExecutionRequest(BaseModel):
    applicable_ceilings: List[str] = ["A3"]


@router.post("/proposals", status_code=status.HTTP_201_CREATED)
def propose_typed_plan(
    req: CreatePlanProposalRequest,
    service: PlannerService = Depends(get_planner_service)
):
    """Genera y persiste una propuesta estructurada de plan (P14)."""
    try:
        autonomy = AutonomyLevel(req.requested_autonomy)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Autonomía inválida '{req.requested_autonomy}'.")

    principal = AuthorizationPrincipal(
        principal_id=req.principal_id,
        role=req.principal_role,
        allowed_scopes=req.principal_scopes
    )

    tasks = [
        ProposedTask(
            task_id=t.task_id,
            title=t.title,
            description=t.description,
            assigned_service=t.assigned_service,
            requires_human_approval=t.requires_human_approval,
            estimated_duration_sec=t.estimated_duration_sec
        )
        for t in req.tasks
    ]

    try:
        proposal = service.propose_typed_plan(
            goal_id=req.goal_id,
            tasks=tasks,
            requested_autonomy=autonomy,
            principal=principal,
            policy_decision=req.policy_decision
        )
        return proposal.to_dict()
    except SecurityAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/proposals/{proposal_id}")
def get_proposal(
    proposal_id: str,
    service: PlannerService = Depends(get_planner_service)
):
    """Consulta una propuesta de plan por su identificador."""
    prop = service.get_proposal(proposal_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Propuesta '{proposal_id}' no encontrada.")
    return prop.to_dict()


@router.post("/proposals/{proposal_id}/decision")
def decide_execution(
    proposal_id: str,
    req: DecideExecutionRequest,
    service: PlannerService = Depends(get_planner_service)
):
    """Evalúa la autonomía efectiva consolidada combinando los techos aplicables (P15)."""
    ceilings = []
    for c in req.applicable_ceilings:
        try:
            ceilings.append(AutonomyLevel(c))
        except ValueError:
            # Ignorar un techo ilegible subiría la autonomía efectiva: se rechaza
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Techo de autonomía inválido '{c}'. Válidos: {[a.value for a in AutonomyLevel]}"
            )

    try:
        decision = service.decide_effective_execution(proposal_id, ceilings)
        return decision.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
