"""Fixtures y configuración de entorno para pruebas unitarias e integración.
Comentarios en español.
"""

import os
import tempfile
import pytest

from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.infrastructure.db.migrations.runner import MigrationRunner



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
