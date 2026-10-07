"""Pruebas de integración para las fases P02, P07, P12, P14 y P15.
Cubre:
- C09: Budget concurrency (dos reservas de 80 sobre 100 no pueden triunfar ambas).
- C21: Default DENY en autorización de scopes.
- C22: Techo de clasificación (clearance ceiling).
- M0-CERT-PROJ: Almacenamiento y consulta de proyecciones de certificación.
- C12: ContextPackage inmutable y recuperación exacta de snapshot.
- P14/P15: Typed Planner y combinación de techos de autonomía (mínimo A0..A5).
Comentarios en español.
"""

import unittest
import uuid
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.infrastructure.db.migrations.runner import MigrationRunner
from ai_os_core.infrastructure.db.repositories.budget_repo import (
    BudgetRepository,
    InsufficientBudgetError
)
from ai_os_core.infrastructure.db.repositories.certifications_repo import CertificationsRepository
from ai_os_core.infrastructure.db.repositories.context_repo import ContextRepository
from ai_os_core.infrastructure.db.repositories.planner_repo import PlannerRepository

from ai_os_core.application.budget_service import BudgetService
from ai_os_core.application.certification_service import CertificationService
from ai_os_core.application.context_service import ContextService, SecurityAccessDeniedError
from ai_os_core.application.planner_service import PlannerService

from ai_os_core.domain.security import ClassificationLevel, AuthorizationPrincipal
from ai_os_core.domain.budget import BudgetStatus
from ai_os_core.domain.certifications import CertificationApplicability, EvaluationVerdict
from ai_os_core.domain.contracts import ResourceReference
from ai_os_core.domain.planner import ProposedTask, AutonomyLevel, combine_autonomy_ceilings


class TestAdvancedPhases(unittest.TestCase):
    """Verificación de seguridad, budget, certificación, contexto y planner."""

    def setUp(self):
        # Base de datos aislada con migraciones 001 y 002 aplicadas
        self.db = DatabaseManager(db_path=":memory:")
        runner = MigrationRunner(self.db)
        runner.run_migrations()

        self.budget_repo = BudgetRepository(self.db)
        self.cert_repo = CertificationsRepository(self.db)
        self.context_repo = ContextRepository(self.db)
        self.planner_repo = PlannerRepository(self.db)

        self.budget_service = BudgetService(self.budget_repo)
        self.cert_service = CertificationService(self.cert_repo)
        self.context_service = ContextService(self.context_repo)
        self.planner_service = PlannerService(self.planner_repo)

    def test_c09_budget_concurrency_race(self):
        """Caso C09: dos reservas de 80 contra saldo de 100 => sólo una tiene éxito."""
        account_id = "acc_marketing_01"
        self.budget_service.get_or_create_account(account_id, initial_balance=100.0)

        # 1. Primera reserva de 80: debe triunfar
        res1 = self.budget_service.reserve_budget(account_id, amount=80.0, reservation_id="res_1")
        self.assertEqual(res1.status, BudgetStatus.RESERVED)

        # 2. Segunda reserva de 80: debe fallar por saldo insuficiente (queda 20 disponible)
        with self.assertRaises(InsufficientBudgetError):
            self.budget_service.reserve_budget(account_id, amount=80.0, reservation_id="res_2")

        # 3. Consumo de la primera reserva
        self.budget_service.consume_budget("res_1")
        acc = self.budget_service.get_or_create_account(account_id)
        self.assertEqual(acc.balance, 20.0)
        self.assertEqual(acc.reserved, 0.0)
        self.assertEqual(acc.available, 20.0)

    def test_c21_default_deny_scope_authorization(self):
        """Caso C21: mutación o lectura sin scope autorizado es rechazada."""
        principal_unauthorized = AuthorizationPrincipal(
            principal_id="untrusted_agent",
            role="guest",
            clearance_level=ClassificationLevel.INTERNAL,
            allowed_scopes=["other:scope"]  # No tiene 'context:build'
        )

        with self.assertRaises(SecurityAccessDeniedError):
            self.context_service.build_context_package(
                goal_id="g_1",
                classification_level=ClassificationLevel.INTERNAL,
                resources=[],
                payload={"data": 123},
                principal=principal_unauthorized
            )

    def test_c22_classification_ceiling_enforcement(self):
        """Caso C22: techo de clasificación no puede superar el clearance del principal."""
        principal_internal = AuthorizationPrincipal(
            principal_id="internal_agent",
            role="developer",
            clearance_level=ClassificationLevel.INTERNAL,  # Nivel 2
            allowed_scopes=["context:build"]
        )

        # Intentar crear un paquete clasificado como RESTRICTED (Nivel 4) debe fallar
        with self.assertRaises(SecurityAccessDeniedError):
            self.context_service.build_context_package(
                goal_id="g_confidential",
                classification_level=ClassificationLevel.RESTRICTED,
                resources=[],
                payload={"secret": "top_secret_intel"},
                principal=principal_internal
            )

        # Crear paquete PUBLIC o INTERNAL debe tener éxito
        pkg = self.context_service.build_context_package(
            goal_id="g_ok",
            classification_level=ClassificationLevel.INTERNAL,
            resources=[],
            payload={"info": "standard"},
            principal=principal_internal
        )
        self.assertIsNotNone(pkg.package_id)
        self.assertEqual(pkg.classification_level, ClassificationLevel.INTERNAL)

    def test_m0_cert_proj_lifecycle(self):
        """Caso M0-CERT-PROJ: Almacenamiento y consulta de aplicabilidad de certificación."""
        cert = CertificationApplicability(
            model_id="qwen-2.5-coder-32b",
            capability_id="code_synthesis",
            version="v2.1",
            source_system="model_drift_evaluator",
            evaluation_verdict=EvaluationVerdict.CERTIFIED,
            is_applicable=True,
            revision=1
        )
        self.cert_service.register_certification(cert)

        # Consultar combinación exacta
        found = self.cert_service.query_applicability("qwen-2.5-coder-32b", "code_synthesis", "v2.1")
        self.assertIsNotNone(found)
        self.assertEqual(found.evaluation_verdict, EvaluationVerdict.CERTIFIED)
        self.assertTrue(found.is_applicable)

    def test_c12_historical_context_reproducibility(self):
        """Caso C12: Un run histórico recupera el snapshot exacto inmutable a partir de su hash."""
        principal = AuthorizationPrincipal(
            principal_id="ko_connector",
            role="service",
            clearance_level=ClassificationLevel.CONFIDENTIAL,
            allowed_scopes=["context:build"]
        )
        ref = ResourceReference(
            resource_id="doc_financial_q3",
            resource_type="document",
            owner_service="knowledge_orchestrator",
            revision=4
        )

        pkg = self.context_service.build_context_package(
            goal_id="goal_audit",
            classification_level=ClassificationLevel.CONFIDENTIAL,
            resources=[ref],
            payload={"quarter": "Q3", "revenue": 5000000},
            principal=principal
        )

        snapshot_hash = pkg.snapshot_hash
        self.assertIsNotNone(snapshot_hash)

        # Recuperar posteriormente por hash histórico
        recovered = self.context_service.recover_historical_snapshot(snapshot_hash)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.package_id, pkg.package_id)
        self.assertEqual(recovered.payload["revenue"], 5000000)

    def test_p14_p15_typed_planner_and_autonomy_ceilings(self):
        """Casos P14 y P15: Typed Plan Proposal y combinación estricta de autonomía (mínimo A0..A5)."""
        principal = AuthorizationPrincipal(
            principal_id="planner_core",
            role="planner",
            allowed_scopes=["planner:propose"]
        )

        task1 = ProposedTask(
            task_id="t1",
            title="Recolectar datos",
            description="Llamada a API",
            assigned_service="athena",
            requires_human_approval=False
        )
        task2 = ProposedTask(
            task_id="t2",
            title="Publicar en producción",
            description="Despliegue crítico",
            assigned_service="agora",
            requires_human_approval=True
        )

        proposal = self.planner_service.propose_typed_plan(
            goal_id="goal_deploy",
            tasks=[task1, task2],
            requested_autonomy=AutonomyLevel.A4,
            principal=principal
        )
        self.assertEqual(proposal.autonomy_level, AutonomyLevel.A4)

        # P15: Autonomy ceiling combination:
        # Si la política o sistema impone un techo A1, el mínimo entre A4 y A1 es A1
        effective_decision = self.planner_service.decide_effective_execution(
            proposal.proposal_id,
            applicable_ceilings=[AutonomyLevel.A1, AutonomyLevel.A3]
        )
        self.assertEqual(effective_decision.effective_autonomy, AutonomyLevel.A1)
        # Como task2 requiere aprobación y la autonomía es A1, no se aprueba automáticamente
        self.assertFalse(effective_decision.approved_for_dispatch)


if __name__ == "__main__":
    unittest.main()
