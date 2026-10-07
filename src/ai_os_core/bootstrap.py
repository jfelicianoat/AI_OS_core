"""Módulo de inicio y bootstrap para AI OS Core.
Asegura la ejecución de migraciones y preparación de SQLite WAL antes de aceptar tráfico.
Comentarios en español.
"""

import logging
from .infrastructure.db.connection import db_manager, DatabaseManager
from .infrastructure.db.migrations.runner import MigrationRunner

logger = logging.getLogger("ai_os_core.bootstrap")


def bootstrap_database(db: DatabaseManager | None = None) -> list[int]:
    """Inicializa la persistencia y aplica las migraciones pendientes."""
    manager = db or db_manager
    runner = MigrationRunner(manager)
    applied = runner.run_migrations()
    if applied:
        logger.info("Migraciones aplicadas exitosamente: %s", applied)
    return applied
