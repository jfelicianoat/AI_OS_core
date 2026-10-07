"""Ejecutor determinista de migraciones forward-only para AI OS Core.
Comentarios en español.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from ..connection import DatabaseManager


class MigrationRunner:
    """Aplica migraciones SQL forward-only de forma transaccional e incremental."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migrations_dir = Path(__file__).parent / "sql"

    def run_migrations(self) -> list[int]:
        """Ejecuta todas las migraciones pendientes en orden numérico."""
        applied_versions: list[int] = []

        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            # Asegurar tabla de versiones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    description TEXT NOT NULL
                );
            """)
            conn.commit()

            # Obtener versiones ya aplicadas
            cursor.execute("SELECT version FROM schema_versions ORDER BY version ASC;")
            existing_versions = {row[0] for row in cursor.fetchall()}

            # Buscar archivos .sql
            sql_files = sorted(self.migrations_dir.glob("*.sql"))

            for file_path in sql_files:
                filename = file_path.name
                # Ejemplo: 001_initial_schema.sql -> versión 1
                try:
                    version = int(filename.split("_")[0])
                except ValueError:
                    continue

                if version in existing_versions:
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()

                now_iso = datetime.now(timezone.utc).isoformat()
                description = filename.replace(".sql", "")
                # executescript hace COMMIT de lo pendiente antes de empezar, así que
                # la transacción va dentro del propio script: el DDL y el registro de
                # versión se aplican juntos o no se aplica nada. El INSERT condicional
                # cubre a dos procesos que arrancan a la vez (el DDL es IF NOT EXISTS).
                try:
                    cursor.executescript(
                        "BEGIN IMMEDIATE;\n"
                        f"{sql_script}\n"
                        "INSERT INTO schema_versions (version, applied_at, description) "
                        f"SELECT {version}, '{now_iso}', '{description}' "
                        f"WHERE NOT EXISTS (SELECT 1 FROM schema_versions WHERE version = {version});\n"
                        "COMMIT;"
                    )
                except Exception:
                    if conn.in_transaction:
                        conn.rollback()
                    raise
                applied_versions.append(version)
        finally:
            conn.close()

        return applied_versions
