"""Servicio de aplicación para Typed Planner y Autonomía Condicional (P14, P15).
Comentarios en español.
"""

import uuid
from typing import List, Dict, Any, Optional
from ai_os_core.domain.planner import (
    TypedPlanProposal,
    ProposedTask,
    AutonomyLevel,
    EffectiveExecutionDecision,
    combine_autonomy_ceilings
)
from ai_os_core.domain.security import AuthorizationPrincipal
from ai_os_core.domain.policies import AuthorizationDecision
from ai_os_core.domain.errors import NotFoundError
from ai_os_core.infrastructure.db.repositories.planner_repo import PlannerRepository
from ai_os_core.infrastructure.db.repositories.goals_repo import GoalsRepository
from ai_os_core.infrastructure.db.repositories.audit_repo import AuditRepository
from ai_os_core.application.context_service import SecurityAccessDeniedError


class PlannerService:
    """Orquesta la emisión de propuestas tipadas de plan y la resolución de techos de autonomía (P14, P15)."""

    def __init__(
        self,
        planner_repo: PlannerRepository,
        goals_repo: Optional[GoalsRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        self.planner_repo = planner_repo
        self.goals_repo = goals_repo
        self.audit_repo = audit_repo

    def propose_typed_plan(
        self,
        goal_id: str,
        tasks: List[ProposedTask],
        requested_autonomy: AutonomyLevel,
        principal: AuthorizationPrincipal,
        policy_decision: Optional[Dict[str, Any]] = None,
        proposal_id: Optional[str] = None
    ) -> TypedPlanProposal:
        """Genera y persiste una propuesta de plan tipado (P14)."""
        # Validación de scope del principal
        if not principal.can_access_scope("planner:propose"):
            raise SecurityAccessDeniedError(
                f"El principal '{principal.principal_id}' no tiene el scope 'planner:propose'."
            )

        if self.goals_repo is not None and not self.goals_repo.get_goal(goal_id):
            raise NotFoundError(f"Goal '{goal_id}' no encontrado: un plan siempre cuelga de un Goal canónico.")
        if not tasks:
            raise ValueError("Un plan necesita al menos una tarea.")
        task_ids = [t.task_id for t in tasks]
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("Los task_id de un plan deben ser únicos.")
        authorization = (policy_decision or {}).get("authorization")
        if authorization is not None:
            # Se valida aquí para que la decisión posterior no tenga que adivinar
            AuthorizationDecision(authorization)
        if authorization == AuthorizationDecision.ALLOW.value:
            # Un ALLOW lo emite el Core, no quien propone: debe coincidir con una traza real.
            trace_id = policy_decision.get("trace_id")
            trace = self.audit_repo.get_decision_trace(trace_id) if (self.audit_repo and trace_id) else None
            if (
                trace is None
                or trace.decision_type != "policy_evaluation"
                or trace.decision_result != authorization
                or trace.metadata.get("executable") != policy_decision.get("executable")
            ):
                raise ValueError(
                    "La decisión ALLOW no corresponde a ninguna evaluación de políticas del Core "
                    "(falta o no coincide su trace_id)."
                )

        pid = proposal_id or f"plan_{uuid.uuid4().hex[:12]}"
        proposal = TypedPlanProposal(
            proposal_id=pid,
            goal_id=goal_id,
            proposed_tasks=tasks,
            autonomy_level=requested_autonomy,
            policy_decision=policy_decision or {}
        )
        self.planner_repo.save_proposal(proposal)
        return proposal

    def decide_effective_execution(
        self,
        proposal_id: str,
        applicable_ceilings: List[AutonomyLevel]
    ) -> EffectiveExecutionDecision:
        """Determina la autonomía efectiva consolidada combinando los techos aplicables (P15 §3.4)."""
        proposal = self.planner_repo.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Propuesta de plan '{proposal_id}' no encontrada.")

        # Regla §3.4: autonomy ceiling -> mínimo sólo A0..A5
        all_levels = [proposal.autonomy_level] + applicable_ceilings
        effective_autonomy = combine_autonomy_ceilings(all_levels)

        # Orden normativo (P15): authorization → autonomía. Ninguna capa eleva la
        # autonomía ni ignora una política que no sea ALLOW ejecutable.
        requires_approval = any(t.requires_human_approval for t in proposal.proposed_tasks)
        reasons = []

        policy = proposal.policy_decision or {}
        authorization = policy.get("authorization")
        if authorization is None:
            reasons.append("Sin decisión de política del Core: no se despacha.")
        elif authorization != AuthorizationDecision.ALLOW.value:
            reasons.append(f"La decisión de política es {authorization}: no se despacha.")
        if policy.get("executable") is False:
            reasons.append("La decisión de política no es ejecutable (unknowns de seguridad o restricciones).")
        if effective_autonomy == AutonomyLevel.A0:
            reasons.append("Autonomía efectiva A0: ejecución exclusivamente manual.")
        if requires_approval and effective_autonomy in (AutonomyLevel.A0, AutonomyLevel.A1):
            reasons.append("Requiere aprobación humana previa antes de ejecución.")

        approved = not reasons
        if approved:
            reasons.append(f"Aprobado para despacho con nivel efectivo {effective_autonomy.value}.")

        return EffectiveExecutionDecision(
            proposal_id=proposal_id,
            approved_for_dispatch=approved,
            effective_autonomy=effective_autonomy,
            reasons=reasons
        )

    def get_proposal(self, proposal_id: str) -> Optional[TypedPlanProposal]:
        """Obtiene una propuesta de plan por su identificador."""
        return self.planner_repo.get_proposal(proposal_id)
