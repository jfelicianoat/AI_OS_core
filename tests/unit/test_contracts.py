"""Pruebas unitarias para contratos canónicos e inmutabilidad (Normativa 0.6.1 §2, C24).
Comentarios en español.
"""

import unittest
from ai_os_core.domain.contracts import (
    ResourceReference,
    IdentityBinding,
    ProducerStreamIdentity
)
from ai_os_core.domain.goals import Goal, Objective, GoalStatus
from ai_os_core.domain.events import EventEnvelope, EventType


class TestContracts(unittest.TestCase):
    """Verifica la integridad y serialización de los contratos canónicos."""

    def test_resource_reference_immutability(self):
        ref = ResourceReference(
            resource_id="res_123",
            resource_type="dataset",
            owner_service="knowledge_orchestrator",
            revision=2
        )
        self.assertEqual(ref.resource_id, "res_123")
        self.assertEqual(ref.revision, 2)
        # Es inmutable
        with self.assertRaises(AttributeError):
            ref.revision = 3  # type: ignore

    def test_identity_binding_preservation(self):
        """Caso C24: IdentityBinding conserva revisión de adaptador."""
        binding = IdentityBinding(
            global_id="global_task_001",
            native_id="jira_task_442",
            source_system="jira_connector",
            adapter_revision=5
        )
        data = binding.to_dict()
        self.assertEqual(data["global_id"], "global_task_001")
        self.assertEqual(data["native_id"], "jira_task_442")
        self.assertEqual(data["adapter_revision"], 5)

    def test_goal_monotonic_revision(self):
        goal = Goal(
            id="goal_test",
            title="Objetivo Test",
            description="Descripción",
            revision=1
        )
        self.assertEqual(goal.revision, 1)
        goal.update_status(GoalStatus.COMPLETED)
        self.assertEqual(goal.revision, 2)
        self.assertEqual(goal.status, GoalStatus.COMPLETED)


if __name__ == "__main__":
    unittest.main()
