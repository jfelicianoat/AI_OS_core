"""Servicio de aplicación para Evaluación de Policies (C08, C18, C19, C20).
Comentarios en español.
"""

import uuid
import json
import hashlib
from typing import Dict, Any, List, Optional
from ..domain.policies import (
    Policy,
    PolicyDecision,
    AuthorizationDecision,
    TernaryResult,
    DECISION_PRECEDENCE
)
from ..domain.audit import DecisionTrace
from ..domain.contracts import utc_now_iso
from ..infrastructure.db.repositories.policies_repo import PoliciesRepository
from ..infrastructure.db.repositories.audit_repo import AuditRepository


class PolicyService:
    """Motor de evaluación y combinación de políticas deterministas."""

    def __init__(self, policies_repo: PoliciesRepository, audit_repo: AuditRepository):
        self.policies_repo = policies_repo
        self.audit_repo = audit_repo

    def evaluate_policies(
        self,
        scope: str,
        context: Dict[str, Any],
        principal_id: str = "system",
        resource_id: Optional[str] = None
    ) -> PolicyDecision:
        """Evalúa todas las políticas activas aplicables a un scope dado y consolida la decisión."""
        policies = self.policies_repo.list_active_policies_for_scope(scope)

        # Si no hay políticas activas, por defecto denegar o indeterminado
        if not policies:
            return PolicyDecision(
                authorization=AuthorizationDecision.DENY,
                obligations=[],
                constraints={},
                matched_policy_refs=[],
                unknown_inputs=[],
                executable=False
            )

        matched_decisions: List[AuthorizationDecision] = []
        matched_policy_refs: List[str] = []
        collected_obligations: set[str] = set()
        collected_constraints: Dict[str, Any] = {}
        unknown_inputs: set[str] = set()

        for policy in policies:
            eval_result = policy.evaluate(context)

            if eval_result == TernaryResult.TRUE:
                matched_decisions.append(policy.decision_if_matched)
                matched_policy_refs.append(policy.policy_id)

                # Consolidar obligaciones (Caso C08: la obligación positiva se conserva)
                for obl in policy.obligations:
                    collected_obligations.add(obl)

                # Consolidar restricciones
                for k, v in policy.constraints.items():
                    # Manejo de min/max (Caso C19)
                    if k.startswith("max_"):
                        if k in collected_constraints:
                            collected_constraints[k] = min(collected_constraints[k], v)
                        else:
                            collected_constraints[k] = v
                    elif k.startswith("min_"):
                        if k in collected_constraints:
                            collected_constraints[k] = max(collected_constraints[k], v)
                        else:
                            collected_constraints[k] = v
                    else:
                        collected_constraints[k] = v

            elif eval_result == TernaryResult.UNKNOWN:
                # Recoger campos que originaron UNKNOWN: ausentes, nulos o no comparables
                # (p. ej. un texto contra greater_than). Si sólo se miraran los ausentes,
                # una política indeterminable por tipo acabaría en ALLOW.
                for cond in policy.conditions:
                    if cond.evaluate(context) == TernaryResult.UNKNOWN:
                        unknown_inputs.add(cond.field)
                # Una política restrictiva que no se puede evaluar no desaparece: aporta
                # INDETERMINATE a la precedencia. Si no, un DENY "coste > 5" sin coste
                # quedaba tapado por cualquier ALLOW y la operación salía ejecutable.
                if policy.decision_if_matched != AuthorizationDecision.ALLOW:
                    matched_decisions.append(AuthorizationDecision.INDETERMINATE)

        # Caso C19: Restricción incompatible conocida (ej. min > max) => DENY
        # Si min y max del mismo concepto existen, verificar compatibilidad
        for min_k, min_v in list(collected_constraints.items()):
            if min_k.startswith("min_"):
                max_k = min_k.replace("min_", "max_")
                if max_k in collected_constraints:
                    max_v = collected_constraints[max_k]
                    if min_v > max_v:
                        matched_decisions.append(AuthorizationDecision.DENY)

        # Si no coincidió ninguna como TRUE pero hubo UNKNOWNs relevantes en políticas restrictivas
        if not matched_decisions and unknown_inputs:
            consolidated_auth = AuthorizationDecision.INDETERMINATE
        elif not matched_decisions:
            consolidated_auth = AuthorizationDecision.ALLOW
        else:
            # Precedencia estricta: DENY > REQUIRE_APPROVAL > INDETERMINATE > ALLOW
            sorted_decisions = sorted(matched_decisions, key=lambda d: DECISION_PRECEDENCE[d])
            consolidated_auth = sorted_decisions[0]

        # Caso C20: UNKNOWN de seguridad bloqueante no se resuelve con simple Approval
        has_security_unknown = any("security" in u.lower() or "auth" in u.lower() for u in unknown_inputs)
        executable = (consolidated_auth == AuthorizationDecision.ALLOW) and not has_security_unknown

        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        decision = PolicyDecision(
            trace_id=trace_id,
            authorization=consolidated_auth,
            constraints=collected_constraints,
            obligations=sorted(list(collected_obligations)),
            matched_policy_refs=matched_policy_refs,
            unknown_inputs=sorted(list(unknown_inputs)),
            executable=executable
        )

        # Registrar traza de decisión (M0-AUDIT)
        context_str = json.dumps(context, sort_keys=True)
        inputs_digest = hashlib.sha256(context_str.encode()).hexdigest()
        self.audit_repo.record_decision_trace(
            DecisionTrace(
                trace_id=trace_id,
                decision_type="policy_evaluation",
                principal_id=principal_id,
                resource_id=resource_id,
                inputs_digest=inputs_digest,
                decision_result=consolidated_auth.value,
                matched_rules=matched_policy_refs,
                metadata={"executable": executable, "scope": scope},
                created_at=utc_now_iso()
            )
        )

        return decision

    def list_policies(self, scope: Optional[str] = None) -> List[Policy]:
        """Lista las políticas registradas, opcionalmente filtradas por scope."""
        return self.policies_repo.list_policies(scope)
