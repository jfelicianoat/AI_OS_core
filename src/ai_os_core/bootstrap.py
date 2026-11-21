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
    conn = manager.get_connection()
    try:
        # Spec 0.6.1 §3.3: una sola política habilitada por (policy_key, scope). Desde 0.4.6 no se pueden crear
        # gemelas, pero una base anterior puede traerlas: se avisa (no se tocan, decide quien administra)
        for row in conn.execute("SELECT policy_key, scope, GROUP_CONCAT(policy_id) AS ids FROM policies "
                                "WHERE enabled = 1 GROUP BY policy_key, scope HAVING COUNT(*) > 1;"):
            logger.warning("Políticas gemelas habilitadas para (%s, %s): %s. Deshabilita las que sobren.",
                           row["policy_key"], row["scope"], row["ids"])
    finally:
        conn.close()
    from .infrastructure.db.repositories.flows_repo import FlowsRepository
    pruned = FlowsRepository(manager).prune()
    if pruned:
        logger.info("Monitor: %s pasos más viejos que la retención borrados", pruned)
    return applied
