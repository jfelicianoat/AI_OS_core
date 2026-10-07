"""Endpoints REST para Budget y Reservas Concurrentes (C09).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from ai_os_core.application.budget_service import BudgetService, InsufficientBudgetError
from ai_os_core.api.dependencies import get_budget_service

router = APIRouter(prefix="/api/v1/budget", tags=["Budget"])


class CreateReservationRequest(BaseModel):
    account_id: str
    amount: float = Field(..., gt=0.0)
    reservation_id: Optional[str] = None
    expires_at: Optional[str] = None


class ActionReservationRequest(BaseModel):
    reservation_id: str


class CreateAccountRequest(BaseModel):
    account_id: str = Field(..., min_length=1)
    balance: float = Field(..., ge=0.0)


@router.post("/accounts", status_code=status.HTTP_201_CREATED)
def create_account(
    req: CreateAccountRequest,
    service: BudgetService = Depends(get_budget_service)
):
    """Da de alta una cuenta de presupuesto con su saldo inicial (409 si ya existe)."""
    return service.create_account(req.account_id, req.balance).to_dict()


@router.post("/reserve", status_code=status.HTTP_201_CREATED)
def create_reservation(
    req: CreateReservationRequest,
    service: BudgetService = Depends(get_budget_service)
):
    """Crea una reserva de saldo atómica garantizando prevención de sobregiros (C09)."""
    try:
        res = service.reserve_budget(
            account_id=req.account_id,
            amount=req.amount,
            reservation_id=req.reservation_id,
            expires_at=req.expires_at
        )
        return res.to_dict()
    except InsufficientBudgetError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/consume")
def consume_reservation(
    req: ActionReservationRequest,
    service: BudgetService = Depends(get_budget_service)
):
    """Confirma el consumo del saldo previamente reservado (409 si ya no está reservada)."""
    service.consume_budget(req.reservation_id)
    return {"status": "consumed", "reservation_id": req.reservation_id}


@router.post("/release")
def release_reservation(
    req: ActionReservationRequest,
    service: BudgetService = Depends(get_budget_service)
):
    """Libera una reserva reintegrando el disponible."""
    service.release_budget(req.reservation_id)
    return {"status": "released", "reservation_id": req.reservation_id}


@router.get("/accounts/{account_id}")
def get_account_balance(
    account_id: str,
    service: BudgetService = Depends(get_budget_service)
):
    """Consulta el saldo y monto reservado de una cuenta (sin crearla)."""
    account = service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cuenta de presupuesto '{account_id}' no encontrada.")
    return account.to_dict()


@router.get("/reservations/{reservation_id}")
def get_reservation(
    reservation_id: str,
    service: BudgetService = Depends(get_budget_service)
):
    """Consulta el estado de una reserva (reserved, consumed, released, expired)."""
    res = service.get_reservation(reservation_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reserva '{reservation_id}' no encontrada.")
    return res.to_dict()
