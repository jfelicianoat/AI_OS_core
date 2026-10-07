"""Fixtures y configuración de entorno para pruebas unitarias e integración.
Comentarios en español.
"""

import os
import tempfile
import pytest
from pathlib import Path

from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.infrastructure.db.migrations.runner import MigrationRunner
from ai_os_core.infrastructure.db.repositories.goals_repo import GoalsRepository
from ai_os_core.infrastructure.db.repositories.services_repo import ServicesRepository
from ai_os_core.infrastructure.db.repositories.events_repo import EventsRepository
from ai_os_core.infrastructure.db.repositories.resources_repo import ResourcesRepository
from ai_os_core.infrastructure.db.repositories.policies_repo import PoliciesRepository
from ai_os_core.infrastructure.db.repositories.approvals_repo import ApprovalsRepository
from ai_os_core.infrastructure.db.repositories.audit_repo import AuditRepository
from ai_os_core.infrastructure.db.repositories.restore_repo import RestoreRepository
from ai_os_core.infrastructure.db.repositories.idempotency_repo import IdempotencyRepository
from ai_os_core.infrastructure.http.security_client import SecurityHttpClientValidator

from ai_os_core.application.goals_service import GoalsService
from ai_os_core.application.service_registry import ServiceRegistryService
from ai_os_core.application.event_service import EventService
from ai_os_core.application.policy_service import PolicyService
from ai_os_core.application.approval_service import ApprovalService
from ai_os_core.application.resource_service import ResourceService
from ai_os_core.application.restore_service import RestoreService


@pytest.fixture
def temp_db():
    """Crea una base de datos SQLite temporal y aplica todas las migraciones."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DatabaseManager(db_path=db_path, synchronous="NORMAL", busy_timeout=5000)
    runner = MigrationRunner(db)
    runner.run_migrations()

    yield db

    # Limpieza
    try:
        os.remove(db_path)
        for ext in ["-wal", "-shm"]:
            if os.path.exists(db_path + ext):
                os.remove(db_path + ext)
    except OSError:
        pass
