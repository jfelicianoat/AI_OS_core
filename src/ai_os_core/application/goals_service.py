"""Servicio de aplicación para Goals y Objectives (M0-GOALS).
Comentarios en español.
"""

from typing import Optional, List
import uuid
from ..domain.goals import Goal, Objective, GoalStatus
from ..domain.audit import AuditRecord
from ..domain.contracts import utc_now_iso
from ..domain.errors import ConflictError, NotFoundError
from ..infrastructure.db.repositories.goals_repo import GoalsRepository
from ..infrastructure.db.repositories.audit_repo import AuditRepository


class GoalsService:
    """Orquesta la creación, actualización y consulta de metas y objetivos."""

    def __init__(self, goals_repo: GoalsRepository, audit_repo: AuditRepository):
        self.goals_repo = goals_repo
        self.audit_repo = audit_repo

    def create_goal(
        self,
        title: str,
        description: str,
        owner_service: str = "ai_os_core",
        parent_goal_id: Optional[str] = None,
        goal_id: Optional[str] = None
    ) -> Goal:
        """Crea un nuevo Goal y registra auditoría."""
        # Crear nunca sobrescribe: el estado y la revisión de un Goal existente
        # sólo cambian por update_goal_status.
        if goal_id and self.goals_repo.get_goal(goal_id):
            raise ConflictError(f"Goal '{goal_id}' ya existe.")
        if parent_goal_id and not self.goals_repo.get_goal(parent_goal_id):
            raise ValueError(f"Goal padre '{parent_goal_id}' no existe.")
        gid = goal_id or f"goal_{uuid.uuid4().hex[:12]}"
        now = utc_now_iso()
        goal = Goal(
            id=gid,
            title=title,
            description=description,
            owner_service=owner_service,
            status=GoalStatus.ACTIVE,
            revision=1,
            parent_goal_id=parent_goal_id,
            created_at=now,
            updated_at=now
        )
        self.goals_repo.save_goal(goal)

        # Registro append-only de auditoría
        self.audit_repo.record_audit(
            AuditRecord(
                record_id=f"aud_{uuid.uuid4().hex[:12]}",
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                principal_id=owner_service,
                action="create_goal",
                resource_type="goal",
                resource_id=goal.id,
                details={"title": title, "status": goal.status.value},
                created_at=now
            )
        )
        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Recupera un Goal."""
        return self.goals_repo.get_goal(goal_id)

    def list_goals(self, limit: int = 50, offset: int = 0) -> List[Goal]:
        """Lista metas con paginación determinista."""
        return self.goals_repo.list_goals(limit, offset)

    def update_goal_status(self, goal_id: str, new_status: GoalStatus, principal_id: str = "system") -> Goal:
        """Actualiza el estado de un Goal incrementando su revisión."""
        goal = self.goals_repo.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal '{goal_id}' no encontrado.")

        old_status = goal.status
        goal.update_status(new_status)
        self.goals_repo.save_goal(goal)

        self.audit_repo.record_audit(
            AuditRecord(
                record_id=f"aud_{uuid.uuid4().hex[:12]}",
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                principal_id=principal_id,
                action="update_goal_status",
                resource_type="goal",
                resource_id=goal.id,
                details={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "new_revision": goal.revision
                },
                created_at=utc_now_iso()
            )
        )
        return goal

    def create_objective(
        self,
        goal_id: str,
        title: str,
        description: str = "",
        objective_id: Optional[str] = None
    ) -> Objective:
        """Crea un nuevo Objective asociado a un Goal."""
        parent_goal = self.goals_repo.get_goal(goal_id)
        if not parent_goal:
            raise ValueError(f"Goal padre '{goal_id}' no existe.")

        if objective_id and self.goals_repo.get_objective(objective_id):
            raise ConflictError(f"Objective '{objective_id}' ya existe.")

        oid = objective_id or f"obj_{uuid.uuid4().hex[:12]}"
        now = utc_now_iso()
        obj = Objective(
            id=oid,
            goal_id=goal_id,
            title=title,
            description=description,
            status=GoalStatus.ACTIVE,
            revision=1,
            created_at=now,
            updated_at=now
        )
        self.goals_repo.save_objective(obj)
        return obj

    def get_objective(self, objective_id: str) -> Optional[Objective]:
        """Obtiene un objetivo por ID."""
        return self.goals_repo.get_objective(objective_id)

    def list_objectives(self, goal_id: str) -> List[Objective]:
        """Lista los objetivos de un Goal en orden de creación."""
        if not self.goals_repo.get_goal(goal_id):
            raise NotFoundError(f"Goal '{goal_id}' no encontrado.")
        return self.goals_repo.list_objectives(goal_id)

    def update_objective_status(self, objective_id: str, new_status: GoalStatus, principal_id: str = "system") -> Objective:
        """Actualiza el estado de un Objective incrementando su revisión y lo audita."""
        obj = self.goals_repo.get_objective(objective_id)
        if not obj:
            raise NotFoundError(f"Objective '{objective_id}' no encontrado.")

        old_status = obj.status
        obj.update_status(new_status)
        self.goals_repo.save_objective(obj)

        self.audit_repo.record_audit(
            AuditRecord(
                record_id=f"aud_{uuid.uuid4().hex[:12]}",
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                principal_id=principal_id,
                action="update_objective_status",
                resource_type="objective",
                resource_id=obj.id,
                details={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "new_revision": obj.revision
                },
                created_at=utc_now_iso()
            )
        )
        return obj

    def list_audit_records(self, resource_id: str):
        """Historial de auditoría append-only de un Goal u Objective."""
        return self.audit_repo.list_audit_records_for_resource(resource_id)
