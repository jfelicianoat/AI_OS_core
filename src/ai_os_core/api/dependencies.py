"""Inyección de dependencias para FastAPI y controladores REST.
Comentarios en español.
"""

from functools import lru_cache
from ..infrastructure.db.connection import db_manager, DatabaseManager
from ..infrastructure.db.repositories.goals_repo import GoalsRepository
from ..infrastructure.db.repositories.services_repo import ServicesRepository
from ..infrastructure.db.repositories.events_repo import EventsRepository
from ..infrastructure.db.repositories.resources_repo import ResourcesRepository
from ..infrastructure.db.repositories.policies_repo import PoliciesRepository
from ..infrastructure.db.repositories.approvals_repo import ApprovalsRepository
from ..infrastructure.db.repositories.audit_repo import AuditRepository
from ..infrastructure.db.repositories.restore_repo import RestoreRepository
from ..infrastructure.db.repositories.idempotency_repo import IdempotencyRepository
from ..infrastructure.db.repositories.budget_repo import BudgetRepository
from ..infrastructure.db.repositories.certifications_repo import CertificationsRepository
from ..infrastructure.db.repositories.context_repo import ContextRepository
from ..infrastructure.db.repositories.planner_repo import PlannerRepository
from ..infrastructure.http.security_client import SecurityHttpClientValidator

from ..application.goals_service import GoalsService
from ..application.service_registry import ServiceRegistryService
from ..application.event_service import EventService
from ..application.policy_service import PolicyService
from ..application.approval_service import ApprovalService
from ..application.resource_service import ResourceService
from ..application.restore_service import RestoreService
from ..application.budget_service import BudgetService
from ..application.certification_service import CertificationService
from ..application.context_service import ContextService
from ..application.planner_service import PlannerService


@lru_cache()
def get_db_manager() -> DatabaseManager:
    """Provee el gestor de base de datos."""
    return db_manager


@lru_cache()
def get_goals_repo() -> GoalsRepository:
    return GoalsRepository(get_db_manager())


@lru_cache()
def get_services_repo() -> ServicesRepository:
    return ServicesRepository(get_db_manager())


@lru_cache()
def get_events_repo() -> EventsRepository:
    return EventsRepository(get_db_manager())


@lru_cache()
def get_resources_repo() -> ResourcesRepository:
    return ResourcesRepository(get_db_manager())


@lru_cache()
def get_policies_repo() -> PoliciesRepository:
    return PoliciesRepository(get_db_manager())


@lru_cache()
def get_approvals_repo() -> ApprovalsRepository:
    return ApprovalsRepository(get_db_manager())


@lru_cache()
def get_audit_repo() -> AuditRepository:
    return AuditRepository(get_db_manager())


@lru_cache()
def get_restore_repo() -> RestoreRepository:
    return RestoreRepository(get_db_manager())


@lru_cache()
def get_idempotency_repo() -> IdempotencyRepository:
    return IdempotencyRepository(get_db_manager())


@lru_cache()
def get_goals_service() -> GoalsService:
    return GoalsService(get_goals_repo(), get_audit_repo())


@lru_cache()
def get_service_registry() -> ServiceRegistryService:
    return ServiceRegistryService(get_services_repo(), SecurityHttpClientValidator())


@lru_cache()
def get_event_service() -> EventService:
    return EventService(get_events_repo())


@lru_cache()
def get_policy_service() -> PolicyService:
    return PolicyService(get_policies_repo(), get_audit_repo())


@lru_cache()
def get_approval_service() -> ApprovalService:
    return ApprovalService(get_approvals_repo())


@lru_cache()
def get_resource_service() -> ResourceService:
    return ResourceService(get_resources_repo())


@lru_cache()
def get_restore_service() -> RestoreService:
    return RestoreService(get_restore_repo())


@lru_cache()
def get_budget_repo() -> BudgetRepository:
    return BudgetRepository(get_db_manager())


@lru_cache()
def get_budget_service() -> BudgetService:
    return BudgetService(get_budget_repo())


@lru_cache()
def get_certifications_repo() -> CertificationsRepository:
    return CertificationsRepository(get_db_manager())


@lru_cache()
def get_certification_service() -> CertificationService:
    return CertificationService(get_certifications_repo())


@lru_cache()
def get_context_repo() -> ContextRepository:
    return ContextRepository(get_db_manager())


@lru_cache()
def get_context_service() -> ContextService:
    return ContextService(get_context_repo())


@lru_cache()
def get_planner_repo() -> PlannerRepository:
    return PlannerRepository(get_db_manager())


@lru_cache()
def get_planner_service() -> PlannerService:
    return PlannerService(get_planner_repo(), get_goals_repo())

