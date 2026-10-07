"""Repositorio SQLite para TypedPlanProposal y decisiones de Planner (P14, P15).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.planner import TypedPlanProposal, ProposedTask, AutonomyLevel


class PlannerRepository:
    """Gestiona la persistencia de propuestas tipadas de planes y decisiones de autonomía."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_proposal(self, proposal: TypedPlanProposal) -> None:
        """Guarda una propuesta estructurada generada por el Planner (P14)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            tasks_data = [t.to_dict() for t in proposal.proposed_tasks]
            cursor.execute(
                """
                INSERT INTO plan_proposals (proposal_id, goal_id, proposed_tasks_json, policy_decision_json, autonomy_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    proposal.proposal_id,
                    proposal.goal_id,
                    json.dumps(tasks_data),
                    json.dumps(proposal.policy_decision),
                    proposal.autonomy_level.value,
                    proposal.created_at
                )
            )

    def get_proposal(self, proposal_id: str) -> Optional[TypedPlanProposal]:
        """Recupera una propuesta de plan por su identificador."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plan_proposals WHERE proposal_id = ?;", (proposal_id,))
            row = cursor.fetchone()
            if not row:
                return None

            tasks_raw = json.loads(row["proposed_tasks_json"])
            tasks = [
                ProposedTask(
                    task_id=t["task_id"],
                    title=t["title"],
                    description=t["description"],
                    assigned_service=t["assigned_service"],
                    requires_human_approval=t.get("requires_human_approval", False),
                    estimated_duration_sec=t.get("estimated_duration_sec", 60)
                )
                for t in tasks_raw
            ]

            return TypedPlanProposal(
                proposal_id=row["proposal_id"],
                goal_id=row["goal_id"],
                proposed_tasks=tasks,
                autonomy_level=AutonomyLevel(row["autonomy_level"]),
                policy_decision=json.loads(row["policy_decision_json"]),
                created_at=row["created_at"]
            )
        finally:
            conn.close()
