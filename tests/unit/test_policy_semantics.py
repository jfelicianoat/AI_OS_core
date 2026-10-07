"""Pruebas unitarias para la semántica ternaria y reglas de Policies (C08, C18, C19, C20).
Comentarios en español.
"""

import unittest
from ai_os_core.domain.policies import (
    Policy,
    PolicyCondition,
    AuthorizationDecision,
    TernaryResult,
    ConditionMode
)
from ai_os_core.application.policy_service import PolicyService
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.infrastructure.db.migrations.runner import MigrationRunner
from ai_os_core.infrastructure.db.repositories.policies_repo import PoliciesRepository
from ai_os_core.infrastructure.db.repositories.audit_repo import AuditRepository


class TestPolicySemantics(unittest.TestCase):
    """Verifica el cumplimiento estricto de las reglas normativas de políticas."""

    def setUp(self):
        self.db = DatabaseManager(db_path=":memory:")
        runner = MigrationRunner(self.db)
        runner.run_migrations()
        self.policies_repo = PoliciesRepository(self.db)
        self.audit_repo = AuditRepository(self.db)
        self.service = PolicyService(self.policies_repo, self.audit_repo)

    def test_c18_unconditional_policies(self):
        """Caso C18: empty conditions require unconditional=true and evaluate TRUE; unconditional plus non-empty conditions invalid."""
        # 1. Política incondicional válida
        valid_unconditional = Policy(
            policy_id="pol_uncond_valid",
            policy_key="uncond_key",
            scope="global",
            decision_if_matched=AuthorizationDecision.ALLOW,
            conditions=[],
            unconditional=True
        )
        self.assertEqual(valid_unconditional.evaluate({}), TernaryResult.TRUE)

        # 2. Condiciones vacías sin unconditional=True debe fallar
        invalid_empty = Policy(
            policy_id="pol_invalid_1",
            policy_key="key1",
            scope="global",
            decision_if_matched=AuthorizationDecision.ALLOW,
            conditions=[],
            unconditional=False
        )
        with self.assertRaises(ValueError):
            invalid_empty.evaluate({})

        # 3. unconditional=True con condiciones no vacías debe fallar
        invalid_nonempty = Policy(
            policy_id="pol_invalid_2",
            policy_key="key2",
            scope="global",
            decision_if_matched=AuthorizationDecision.ALLOW,
            conditions=[PolicyCondition(field="tier", operator="equals", value="gold")],
            unconditional=True
        )
        with self.assertRaises(ValueError):
            invalid_nonempty.evaluate({"tier": "gold"})

    def test_ternary_missing_and_null_logic(self):
        """Verifica la semántica ternaria para campos ausentes o null (§3.2)."""
        # exists(field): presente incluso null -> TRUE; ausente -> FALSE
        cond_exists = PolicyCondition(field="param", operator="exists")
        self.assertEqual(cond_exists.evaluate({"param": None}), TernaryResult.TRUE)
        self.assertEqual(cond_exists.evaluate({"param": 123}), TernaryResult.TRUE)
        self.assertEqual(cond_exists.evaluate({}), TernaryResult.FALSE)

        # equals(field, null): presente null -> TRUE; presente no-null -> FALSE; ausente -> UNKNOWN
        cond_null = PolicyCondition(field="param", operator="equals", value=None)
        self.assertEqual(cond_null.evaluate({"param": None}), TernaryResult.TRUE)
        self.assertEqual(cond_null.evaluate({"param": "foo"}), TernaryResult.FALSE)
        self.assertEqual(cond_null.evaluate({}), TernaryResult.UNKNOWN)

        # Rango/comparación con null o ausente -> UNKNOWN
        cond_gt = PolicyCondition(field="score", operator="greater_than", value=50)
        self.assertEqual(cond_gt.evaluate({}), TernaryResult.UNKNOWN)
        self.assertEqual(cond_gt.evaluate({"score": None}), TernaryResult.UNKNOWN)
        self.assertEqual(cond_gt.evaluate({"score": 80}), TernaryResult.TRUE)
        self.assertEqual(cond_gt.evaluate({"score": 20}), TernaryResult.FALSE)

    def test_c08_policy_obligation_preservation(self):
        """Caso C08: requires_approval true + false => la obligación de aprobación se preserva."""
        # Política 1: Exige aprobación y añade obligación
        p1 = Policy(
            policy_id="pol_p1",
            policy_key="key_approval",
            scope="deploy",
            decision_if_matched=AuthorizationDecision.REQUIRE_APPROVAL,
            conditions=[PolicyCondition(field="env", operator="equals", value="prod")],
            obligations=["human_approval_required"]
        )
        # Política 2: Concede permiso sin exigir obligación
        p2 = Policy(
            policy_id="pol_p2",
            policy_key="key_allow",
            scope="deploy",
            decision_if_matched=AuthorizationDecision.ALLOW,
            conditions=[PolicyCondition(field="service", operator="equals", value="api")],
            obligations=[]
        )
        self.policies_repo.save_policy(p1)
        self.policies_repo.save_policy(p2)

        decision = self.service.evaluate_policies(
            scope="deploy",
            context={"env": "prod", "service": "api"}
        )
        # Precedencia REQUIRE_APPROVAL > ALLOW
        self.assertEqual(decision.authorization, AuthorizationDecision.REQUIRE_APPROVAL)
        self.assertIn("human_approval_required", decision.obligations)

    def test_c19_incompatible_constraints(self):
        """Caso C19: known min > max => DENY; UNKNOWN-dependent incompatibility => INDETERMINATE."""
        # Política con min_replicas = 10 y max_replicas = 5
        incompatible_policy = Policy(
            policy_id="pol_incompatible",
            policy_key="scale_policy",
            scope="scale",
            decision_if_matched=AuthorizationDecision.ALLOW,
            conditions=[],
            unconditional=True,
            constraints={"min_replicas": 10, "max_replicas": 5}
        )
        self.policies_repo.save_policy(incompatible_policy)

        decision = self.service.evaluate_policies(scope="scale", context={})
        self.assertEqual(decision.authorization, AuthorizationDecision.DENY)

    def test_c20_security_unknown_not_resolved_by_approval(self):
        """Caso C20: UNKNOWN de seguridad no se resuelve con approval y executable permanece False."""
        policy_sec = Policy(
            policy_id="pol_sec",
            policy_key="sec_gate",
            scope="execute_command",
            decision_if_matched=AuthorizationDecision.REQUIRE_APPROVAL,
            conditions=[PolicyCondition(field="security_clearance", operator="equals", value="level_4")]
        )
        self.policies_repo.save_policy(policy_sec)

        # El contexto carece de 'security_clearance' -> UNKNOWN
        decision = self.service.evaluate_policies(
            scope="execute_command",
            context={"command": "restart"}
        )
        self.assertFalse(decision.executable)
        self.assertIn("security_clearance", decision.unknown_inputs)


if __name__ == "__main__":
    unittest.main()
