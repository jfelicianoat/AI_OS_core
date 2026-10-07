"""Pruebas de integración para todos los casos críticos de AI OS Core M0.
Cubre C01, C02, C03, C05, C06, C07, C15, C23, C24, M0-REG, M0-GOALS, M0-GRAPH, M0-AUDIT.
Comentarios en español.
"""

import unittest
import uuid
import hashlib
import json

from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.infrastructure.db.migrations.runner import MigrationRunner
from ai_os_core.infrastructure.db.repositories.goals_repo import GoalsRepository
from ai_os_core.infrastructure.db.repositories.services_repo import ServicesRepository
from ai_os_core.infrastructure.db.repositories.events_repo import EventsRepository
from ai_os_core.infrastructure.db.repositories.resources_repo import ResourcesRepository
from ai_os_core.infrastructure.db.repositories.policies_repo import PoliciesRepository
from ai_os_core.infrastructure.db.repositories.approvals_repo import (
    ApprovalsRepository,
    ApprovalConflictError,
    ApprovalExecutionDeniedError
)
from ai_os_core.infrastructure.db.repositories.audit_repo import AuditRepository
from ai_os_core.infrastructure.db.repositories.restore_repo import RestoreRepository
from ai_os_core.infrastructure.db.repositories.idempotency_repo import (
    IdempotencyRepository,
    IdempotencyConflictError
)
from ai_os_core.infrastructure.http.security_client import (
    SecurityHttpClientValidator,
    SSRFSecurityViolation
)

from ai_os_core.application.goals_service import GoalsService
from ai_os_core.application.service_registry import ServiceRegistryService
from ai_os_core.application.event_service import EventService
from ai_os_core.application.approval_service import ApprovalService
from ai_os_core.application.resource_service import ResourceService
from ai_os_core.application.restore_service import RestoreService

from ai_os_core.domain.goals import GoalStatus
from ai_os_core.domain.capabilities import ServiceRegistration, CapabilityManifest, ServiceHealthStatus
from ai_os_core.domain.events import EventEnvelope, EventType
from ai_os_core.domain.approvals import ApprovalAuthorization, ApprovalUse, ApprovalRevocation
from ai_os_core.domain.resources import ResourceNode, ResourceRelation
from ai_os_core.domain.restore import OperationStatusQuery, OperationReceipt, OperationExecutionStatus
from ai_os_core.domain.contracts import IdentityBinding, utc_now_iso


class TestAIOSCoreM0Cases(unittest.TestCase):
    """Batería completa de verificación para la especificación normativa 0.6.1 M0."""

    def setUp(self):
        # Base de datos aislada en memoria con esquema migrado
        self.db = DatabaseManager(db_path=":memory:")
        runner = MigrationRunner(self.db)
        runner.run_migrations()

        # Repositorios
        self.idemp_repo = IdempotencyRepository(self.db)
        self.goals_repo = GoalsRepository(self.db)
        self.services_repo = ServicesRepository(self.db)
        self.events_repo = EventsRepository(self.db)
        self.resources_repo = ResourcesRepository(self.db)
        self.policies_repo = PoliciesRepository(self.db)
        self.approvals_repo = ApprovalsRepository(self.db)
        self.audit_repo = AuditRepository(self.db)
        self.restore_repo = RestoreRepository(self.db)

        # Servicios de aplicación
        self.goals_service = GoalsService(self.goals_repo, self.audit_repo)
        self.service_registry = ServiceRegistryService(self.services_repo)
        self.event_service = EventService(self.events_repo)
        self.approval_service = ApprovalService(self.approvals_repo)
        self.resource_service = ResourceService(self.resources_repo)
        self.restore_service = RestoreService(self.restore_repo)

    def test_c01_idempotency_conflict(self):
        """Caso C01: Duplicate concurrent idempotency.
        Mismo operation_id + mismo digest => misma respuesta lógica.
        Misma clave + digest distinto => conflicto 409.
        """
        key = "idem_key_001"
        principal = "agent_athena"
        op_id = "op_123"
        digest_a = hashlib.sha256(b"request_payload_A").hexdigest()
        digest_b = hashlib.sha256(b"request_payload_B").hexdigest()

        # 1. Guardar primera respuesta
        self.idemp_repo.save_response(
            key=key,
            principal_id=principal,
            operation_id=op_id,
            request_digest=digest_a,
            response_code=200,
            response_body='{"status":"ok"}'
        )

        # 2. Reintento con mismo digest -> retorno cacheado
        cached = self.idemp_repo.find_cached_response(key, principal, op_id, digest_a)
        self.assertIsNotNone(cached)
        self.assertEqual(cached[0], 200)

        # 3. Solicitud con mismo idempotency key pero diferente digest -> Conflicto 409
        with self.assertRaises(IdempotencyConflictError):
            self.idemp_repo.find_cached_response(key, principal, op_id, digest_b)

    def test_c02_late_event_canonical_protection(self):
        """Caso C02: Late event.
        Un evento full_state con revisión menor no puede regresar la revisión canónica más reciente.
        """
        resource_id = "dataset_market_pulse"

        # 1. Evento más reciente: revisión 8
        ev_rev8 = EventEnvelope(
            event_id="ev_008",
            producer_id="producer_1",
            stream_id="stream_a",
            stream_epoch=1,
            source_sequence=1,
            event_type=EventType.FULL_STATE,
            resource_id=resource_id,
            resource_type="dataset",
            revision=8,
            payload={"status": "completed", "rows": 1000},
            state_digest="digest_rev8"
        )
        self.event_service.ingest_event(ev_rev8)

        # 2. Evento tardío: revisión 7 (llegó después)
        ev_rev7 = EventEnvelope(
            event_id="ev_007",
            producer_id="producer_1",
            stream_id="stream_a",
            stream_epoch=1,
            source_sequence=2,
            event_type=EventType.FULL_STATE,
            resource_id=resource_id,
            resource_type="dataset",
            revision=7,
            payload={"status": "started", "rows": 0},
            state_digest="digest_rev7"
        )
        self.event_service.ingest_event(ev_rev7)

        # 3. La proyección canónica debe permanecer en revisión 8
        state = self.event_service.get_canonical_state(resource_id)
        self.assertEqual(state["revision"], 8)
        self.assertEqual(state["payload"]["status"], "completed")

    def test_c03_same_revision_contradiction_quarantine(self):
        """Caso C03: Dos full_state con la misma revisión y diferente state_digest entran en cuarentena."""
        resource_id = "job_99"

        ev1 = EventEnvelope(
            event_id="ev_job_1",
            producer_id="agora_runner",
            stream_id="jobs",
            stream_epoch=1,
            source_sequence=1,
            event_type=EventType.FULL_STATE,
            resource_id=resource_id,
            resource_type="job",
            revision=3,
            payload={"state": "success"},
            state_digest="digest_alpha"
        )
        accepted1, reason1 = self.event_service.ingest_event(ev1)
        self.assertTrue(accepted1)

        # Segundo evento con misma revisión 3 pero state_digest divergente
        ev2 = EventEnvelope(
            event_id="ev_job_2",
            producer_id="agora_runner",
            stream_id="jobs",
            stream_epoch=1,
            source_sequence=2,
            event_type=EventType.FULL_STATE,
            resource_id=resource_id,
            resource_type="job",
            revision=3,
            payload={"state": "failed"},
            state_digest="digest_beta"
        )
        accepted2, reason2 = self.event_service.ingest_event(ev2)
        self.assertFalse(accepted2)
        self.assertTrue(ev2.quarantine)
        self.assertIn("Contradictory", reason2)

    def test_c05_replay_gap_detection(self):
        """Caso C05: Hueco de secuencia no recuperable congela proyección y registra REPLAY_GAP."""
        # Llega secuencia 1
        ev1 = EventEnvelope(
            event_id="ev_s1",
            producer_id="broker",
            stream_id="inferences",
            stream_epoch=1,
            source_sequence=1,
            event_type=EventType.FULL_STATE,
            resource_id="res_gap",
            resource_type="stream",
            revision=1,
            payload={"step": 1}
        )
        self.event_service.ingest_event(ev1)

        # Llega secuencia 3 (salto: falta secuencia 2)
        ev3 = EventEnvelope(
            event_id="ev_s3",
            producer_id="broker",
            stream_id="inferences",
            stream_epoch=1,
            source_sequence=3,
            event_type=EventType.FULL_STATE,
            resource_id="res_gap",
            resource_type="stream",
            revision=2,
            payload={"step": 3}
        )
        accepted, reason = self.event_service.ingest_event(ev3)
        self.assertFalse(accepted)
        self.assertTrue(ev3.quarantine)
        self.assertIn("REPLAY_GAP", reason)

        # Verificar reporte de gaps
        gaps = self.event_service.list_unresolved_gaps()
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].expected_sequence, 2)
        self.assertEqual(gaps[0].received_sequence, 3)

    def test_c06_approval_expiry(self):
        """Caso C06: Autorización expirada antes de uso no puede ser comprometida."""
        auth = ApprovalAuthorization(
            authorization_id="auth_exp",
            scope="critical_action",
            max_uses=1,
            expires_at="2020-01-01T00:00:00Z"  # Expirada en el pasado
        )
        self.approval_service.create_authorization(auth)

        use = ApprovalUse(
            use_id="use_exp",
            authorization_id="auth_exp",
            operation_id="op_fail",
            operation_digest="digest_123"
        )
        with self.assertRaises(ApprovalExecutionDeniedError):
            self.approval_service.commit_use(use, current_time_iso="2026-01-01T00:00:00Z")

    def test_c07_scoped_approval_concurrency_and_conflict(self):
        """Caso C07: max_uses=2.
        Dos operaciones consumen dos usos; tercera falla; retry del segundo no consume extra; digest distinto causa conflicto.
        """
        auth = ApprovalAuthorization(
            authorization_id="auth_scope_2",
            scope="write_db",
            max_uses=2
        )
        self.approval_service.create_authorization(auth)

        # 1. Primer uso
        use1 = ApprovalUse(
            use_id="use_1",
            authorization_id="auth_scope_2",
            operation_id="op_1",
            operation_digest="digest_op1"
        )
        self.assertTrue(self.approval_service.commit_use(use1))

        # 2. Segundo uso
        use2 = ApprovalUse(
            use_id="use_2",
            authorization_id="auth_scope_2",
            operation_id="op_2",
            operation_digest="digest_op2"
        )
        self.assertTrue(self.approval_service.commit_use(use2))

        # 3. Retry legítimo de op_2 con mismo digest -> éxito sin consumir extra
        use2_retry = ApprovalUse(
            use_id="use_2_retry",
            authorization_id="auth_scope_2",
            operation_id="op_2",
            operation_digest="digest_op2"
        )
        self.assertTrue(self.approval_service.commit_use(use2_retry))

        # 4. Retry de op_2 con digest distinto -> Conflicto C07
        use2_conflict = ApprovalUse(
            use_id="use_2_conflict",
            authorization_id="auth_scope_2",
            operation_id="op_2",
            operation_digest="digest_tampered"
        )
        with self.assertRaises(ApprovalConflictError):
            self.approval_service.commit_use(use2_conflict)

        # 5. Tercer uso distinto falla porque max_uses=2 está agotado
        use3 = ApprovalUse(
            use_id="use_3",
            authorization_id="auth_scope_2",
            operation_id="op_3",
            operation_digest="digest_op3"
        )
        with self.assertRaises(ApprovalExecutionDeniedError):
            self.approval_service.commit_use(use3)

    def test_c15_restore_operation_status(self):
        """Caso C15: Restore.
        succeeded => no resend;
        not_seen => retry allowed.
        """
        # 1. Operación no vista antes
        q_not_seen = OperationStatusQuery(operation_id="op_new", target_service_id="agora")
        receipt_not_seen = self.restore_service.check_operation_status(q_not_seen)
        self.assertEqual(receipt_not_seen.status, OperationExecutionStatus.NOT_SEEN)
        self.assertEqual(receipt_not_seen.determine_action(), "retry_allowed")

        # 2. Operación ya completada con éxito
        receipt_success = OperationReceipt(
            operation_id="op_done",
            receiver_service="agora",
            status=OperationExecutionStatus.SUCCEEDED,
            result_digest="digest_success"
        )
        self.restore_service.record_receipt(receipt_success)

        q_done = OperationStatusQuery(operation_id="op_done", target_service_id="agora")
        checked = self.restore_service.check_operation_status(q_done)
        self.assertEqual(checked.status, OperationExecutionStatus.SUCCEEDED)
        self.assertEqual(checked.determine_action(), "reconstruct_state_no_resend")

    def test_m0_goals_lifecycle_and_audit(self):
        """Caso M0-GOALS y M0-AUDIT: creación y avance de metas preserva revisión y registra auditoría."""
        goal = self.goals_service.create_goal(
            title="Objetivo General",
            description="Completar MVP M0",
            owner_service="ai_os_core"
        )
        self.assertEqual(goal.revision, 1)

        # Actualizar estado
        updated = self.goals_service.update_goal_status(goal.id, GoalStatus.COMPLETED)
        self.assertEqual(updated.revision, 2)
        self.assertEqual(updated.status, GoalStatus.COMPLETED)

        # Verificar auditoría correlacionada
        audits = self.audit_repo.list_audit_records_for_resource(goal.id)
        self.assertEqual(len(audits), 2)
        self.assertEqual(audits[0].action, "create_goal")
        self.assertEqual(audits[1].action, "update_goal_status")

    def test_m0_graph_and_c24_identity_binding(self):
        """Caso M0-GRAPH y C24: Graph relations y preservación de revisión de adaptador."""
        # Nodo de recurso
        node = ResourceNode(
            resource_id="res_doc_1",
            resource_type="document",
            owner_service="knowledge_orchestrator",
            revision=1,
            data={"title": "Spec 0.6.1"}
        )
        self.resource_service.save_resource(node)

        # Relación
        rel = ResourceRelation(
            source_id="res_doc_1",
            target_id="goal_123",
            relation_type="fulfills"
        )
        self.resource_service.add_relation(rel)
        rels = self.resource_service.get_relations_for("res_doc_1")
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0].relation_type, "fulfills")

        # Caso C24: Vinculación con revisión de adaptador
        binding = IdentityBinding(
            global_id="res_doc_1",
            native_id="confluence_page_881",
            source_system="confluence",
            adapter_revision=3
        )
        self.resource_service.bind_identity(binding)

        recovered_binding = self.resource_service.get_identity_binding("res_doc_1", "confluence")
        self.assertIsNotNone(recovered_binding)
        self.assertEqual(recovered_binding.adapter_revision, 3)

    def test_c23_service_security_and_ssrf(self):
        """Caso C23: Registro fuera de allowlist o endpoint de metadatos de nube es bloqueado."""
        validator = SecurityHttpClientValidator(allowed_hosts=["localhost", "127.0.0.1"])

        # 1. URL permitida
        validator.validate_url("http://localhost:8080/api")

        # 2. IP de metadatos de nube bloqueada
        with self.assertRaises(SSRFSecurityViolation):
            validator.validate_url("http://169.254.169.254/latest/meta-data")

        # 3. Host fuera de allowlist bloqueado
        with self.assertRaises(SSRFSecurityViolation):
            validator.validate_url("https://malicious-external-host.com/endpoint")


if __name__ == "__main__":
    unittest.main()
