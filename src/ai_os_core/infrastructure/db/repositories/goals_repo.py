"""Repositorio SQLite para Goals y Objectives (M0-GOALS).
Comentarios en español.
"""

import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.goals import Goal, Objective, GoalStatus


class GoalsRepository:
    """Acceso a datos persistente para metas y objetivos de AI OS Core."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_goal(self, goal: Goal) -> None:
        """Inserta o actualiza un Goal de forma atómica."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO goals (id, title, description, status, revision, parent_goal_id, owner_service, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    status=excluded.status,
                    revision=excluded.revision,
                    parent_goal_id=excluded.parent_goal_id,
                    updated_at=excluded.updated_at;
                """,
                (
                    goal.id,
                    goal.title,
                    goal.description,
                    goal.status.value,
                    goal.revision,
                    goal.parent_goal_id,
                    goal.owner_service,
                    goal.created_at,
                    goal.updated_at
                )
            )

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Recupera un Goal por su identificador."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM goals WHERE id = ?;", (goal_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Goal(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                status=GoalStatus(row["status"]),
                revision=row["revision"],
                parent_goal_id=row["parent_goal_id"],
                owner_service=row["owner_service"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        finally:
            conn.close()

    def list_goals(self, limit: int = 50, offset: int = 0) -> List[Goal]:
        """Paginación determinista estable para listado de Goals."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM goals ORDER BY created_at ASC, id ASC LIMIT ? OFFSET ?;",
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [
                Goal(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    status=GoalStatus(row["status"]),
                    revision=row["revision"],
                    parent_goal_id=row["parent_goal_id"],
                    owner_service=row["owner_service"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                for row in rows
            ]
        finally:
            conn.close()

    def save_objective(self, objective: Objective) -> None:
        """Inserta o actualiza un Objective."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO objectives (id, goal_id, title, description, status, revision, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    status=excluded.status,
                    revision=excluded.revision,
                    updated_at=excluded.updated_at;
                """,
                (
                    objective.id,
                    objective.goal_id,
                    objective.title,
                    objective.description,
                    objective.status.value,
                    objective.revision,
                    objective.created_at,
                    objective.updated_at
                )
            )

    def get_objective(self, objective_id: str) -> Optional[Objective]:
        """Recupera un objetivo por ID."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM objectives WHERE id = ?;", (objective_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Objective(
                id=row["id"],
                goal_id=row["goal_id"],
                title=row["title"],
                description=row["description"],
                status=GoalStatus(row["status"]),
                revision=row["revision"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        finally:
            conn.close()

    def list_objectives(self, goal_id: str) -> List[Objective]:
        """Lista los objetivos de un Goal con orden estable."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM objectives WHERE goal_id = ? ORDER BY created_at ASC, id ASC;",
                (goal_id,)
            )
            return [
                Objective(
                    id=row["id"],
                    goal_id=row["goal_id"],
                    title=row["title"],
                    description=row["description"],
                    status=GoalStatus(row["status"]),
                    revision=row["revision"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
