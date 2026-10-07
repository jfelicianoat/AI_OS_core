"""Endpoints REST para Goals y Objectives (M0-GOALS).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from ai_os_core.api.schemas.common import (
    CreateGoalRequest,
    UpdateGoalStatusRequest,
    CreateObjectiveRequest,
    PaginatedResponse
)
from ai_os_core.domain.goals import GoalStatus
from ai_os_core.application.goals_service import GoalsService
from ai_os_core.api.dependencies import get_goals_service

router = APIRouter(prefix="/api/v1", tags=["Goals & Objectives"])


@router.post("/goals", status_code=status.HTTP_201_CREATED)
def create_goal(req: CreateGoalRequest, service: GoalsService = Depends(get_goals_service)):
    """Crea una nueva meta canónica."""
    goal = service.create_goal(
        title=req.title,
        description=req.description,
        owner_service=req.owner_service,
        parent_goal_id=req.parent_goal_id,
        goal_id=req.goal_id
    )
    return goal.to_dict()


@router.get("/goals")
def list_goals(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: GoalsService = Depends(get_goals_service)
):
    """Lista metas con paginación determinista estable."""
    items = service.list_goals(limit=limit, offset=offset)
    return {
        "items": [g.to_dict() for g in items],
        "total_returned": len(items),
        "limit": limit,
        "offset": offset
    }


@router.get("/goals/{goal_id}")
def get_goal(goal_id: str, service: GoalsService = Depends(get_goals_service)):
    """Obtiene una meta por su ID."""
    goal = service.get_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal '{goal_id}' no encontrado.")
    return goal.to_dict()


@router.patch("/goals/{goal_id}/status")
def update_goal_status(
    goal_id: str,
    req: UpdateGoalStatusRequest,
    service: GoalsService = Depends(get_goals_service)
):
    """Actualiza el estado de una meta incrementando su revisión."""
    try:
        new_status = GoalStatus(req.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido '{req.status}'. Estados válidos: {[s.value for s in GoalStatus]}"
        )

    try:
        updated = service.update_goal_status(goal_id, new_status, req.principal_id)
        return updated.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/goals/{goal_id}/objectives")
def list_goal_objectives(goal_id: str, service: GoalsService = Depends(get_goals_service)):
    """Lista los objetivos asociados a un Goal."""
    return [o.to_dict() for o in service.list_objectives(goal_id)]


@router.get("/goals/{goal_id}/audit")
def get_goal_audit(goal_id: str, service: GoalsService = Depends(get_goals_service)):
    """Historial de auditoría append-only de un Goal (creación y cambios de estado)."""
    return [r.to_dict() for r in service.list_audit_records(goal_id)]


@router.post("/objectives", status_code=status.HTTP_201_CREATED)
def create_objective(req: CreateObjectiveRequest, service: GoalsService = Depends(get_goals_service)):
    """Crea un objetivo secundario asociado a un Goal."""
    try:
        obj = service.create_objective(
            goal_id=req.goal_id,
            title=req.title,
            description=req.description,
            objective_id=req.objective_id
        )
        return obj.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/objectives/{objective_id}")
def get_objective(objective_id: str, service: GoalsService = Depends(get_goals_service)):
    """Obtiene un objetivo por ID."""
    obj = service.get_objective(objective_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Objective '{objective_id}' no encontrado.")
    return obj.to_dict()


@router.patch("/objectives/{objective_id}/status")
def update_objective_status(
    objective_id: str,
    req: UpdateGoalStatusRequest,
    service: GoalsService = Depends(get_goals_service)
):
    """Actualiza el estado de un objetivo incrementando su revisión."""
    try:
        new_status = GoalStatus(req.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido '{req.status}'. Estados válidos: {[s.value for s in GoalStatus]}"
        )
    return service.update_objective_status(objective_id, new_status, req.principal_id).to_dict()
