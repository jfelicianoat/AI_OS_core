"""Endpoints REST para Evaluación de Policies (C08, C18, C19, C20).
Comentarios en español.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from ai_os_core.api.schemas.common import CreatePolicyRequest, PolicyEvaluateRequest
from ai_os_core.domain.policies import (
    Policy,
    PolicyCondition,
    AuthorizationDecision,
    ConditionMode
)
from ai_os_core.application.policy_service import PolicyService
from ai_os_core.infrastructure.db.repositories.policies_repo import PoliciesRepository
from ai_os_core.api.dependencies import get_policy_service, get_policies_repo, get_flows_repo
from ai_os_core.api.routes.flows import flow_id_from, record_safely, reporter
from ai_os_core.infrastructure.db.repositories.flows_repo import FlowsRepository

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_policy(
    req: CreatePolicyRequest,
    repo: PoliciesRepository = Depends(get_policies_repo)
):
    """Registra una nueva política determinista en el control plane."""
    try:
        decision = AuthorizationDecision(req.decision_if_matched)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decisión inválida '{req.decision_if_matched}'. Válidas: {[d.value for d in AuthorizationDecision]}"
        )

    try:
        cond_mode = ConditionMode(req.condition_mode)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"condition_mode inválido '{req.condition_mode}'. Válidos: {[m.value for m in ConditionMode]}"
        )

    conditions = [
        PolicyCondition(field=c.field, operator=c.operator, value=c.value)
        for c in req.conditions
    ]

    policy = Policy(
        policy_id=req.policy_id,
        policy_key=req.policy_key,
        scope=req.scope,
        decision_if_matched=decision,
        conditions=conditions,
        condition_mode=cond_mode,
        unconditional=req.unconditional,
        enabled=req.enabled,
        revision=req.revision,
        constraints=req.constraints,
        obligations=req.obligations
    )

    try:
        repo.save_policy(policy)
        return {
            "policy_id": policy.policy_id,
            "policy_key": policy.policy_key,
            "status": "created"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/evaluate")
def evaluate_policies(
    req: PolicyEvaluateRequest,
    request: Request,
    service: PolicyService = Depends(get_policy_service),
    flows: FlowsRepository = Depends(get_flows_repo)
):
    """Evalúa las políticas para un scope y contexto dados."""
    decision = service.evaluate_policies(
        scope=req.scope,
        context=req.context,
        principal_id=req.principal_id,
        resource_id=req.resource_id
    )
    result = decision.to_dict()
    if req.scope.endswith(":broker"):
        # La app manda esto como `priority` al Broker; None = no mandarla (100 por defecto)
        result["broker_priority"] = flows.priorities().get(req.scope.split(":", 1)[0])
    # Monitor: la decisión entra en el flujo de la petición (context.flow_id) o abre uno propio
    asker = req.principal_id if req.principal_id != "system" else req.scope.split(":", 1)[0]
    record_safely(flows, flow_id=flow_id_from(req.context, result["trace_id"] or f"flow_{uuid.uuid4().hex[:12]}"), kind="decision",
                  source=reporter(request, asker), target="core",
                  summary=f"{result['authorization']} · {req.scope}",
                  details={"scope": req.scope, "authorization": result["authorization"],
                           "executable": result["executable"], "trace_id": result["trace_id"],
                           "data_classification": req.context.get("data_classification"),
                           "matched_policies": result["matched_policy_refs"],
                           "unknown_inputs": result["unknown_inputs"],
                           "broker_priority": result.get("broker_priority"),
                           "destination": req.scope.split(":", 1)[1] if ":" in req.scope else None})
    return result


@router.get("")
def list_policies(
    scope: Optional[str] = Query(None),
    service: PolicyService = Depends(get_policy_service)
):
    """Lista las políticas registradas (todas o las de un scope)."""
    result = []
    for p in service.list_policies(scope):
        item = {
            "policy_id": p.policy_id,
            "policy_key": p.policy_key,
            "scope": p.scope,
            "decision_if_matched": p.decision_if_matched.value,
            "condition_mode": p.condition_mode.value,
            "conditions": [{"field": c.field, "operator": c.operator, "value": c.value} for c in p.conditions],
            "unconditional": p.unconditional,
            "enabled": p.enabled,
            "revision": p.revision,
            "constraints": p.constraints,
            "obligations": p.obligations,
            "created_at": p.created_at,
        }
        result.append(item)
    return result
