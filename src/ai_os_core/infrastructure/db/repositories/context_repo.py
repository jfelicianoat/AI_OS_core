"""Repositorio SQLite para ContextPackage y reproducción histórica (C12, P07, P12).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.context import ContextPackage
from ai_os_core.domain.security import ClassificationLevel
from ai_os_core.domain.contracts import ResourceReference


class ContextRepository:
    """Gestiona el almacenamiento inmutable de paquetes de contexto preparados por el Core."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_package(self, pkg: ContextPackage) -> None:
        """Persiste un paquete de contexto inmutable (C12)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            package_data = {
                "resources": [r.to_dict() for r in pkg.resources],
                "payload": pkg.payload
            }
            cursor.execute(
                """
                INSERT INTO context_packages (package_id, goal_id, classification_level, snapshot_hash, package_data_json, created_at, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    pkg.package_id,
                    pkg.goal_id,
                    pkg.classification_level.value,
                    pkg.snapshot_hash,
                    json.dumps(package_data),
                    pkg.created_at,
                    pkg.valid_until
                )
            )

    def get_package(self, package_id: str) -> Optional[ContextPackage]:
        """Obtiene un paquete de contexto por su identificador único."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM context_packages WHERE package_id = ?;", (package_id,))
            row = cursor.fetchone()
            if not row:
                return None

            data = json.loads(row["package_data_json"])
            resources = [
                ResourceReference(
                    resource_id=r["resource_id"],
                    resource_type=r["resource_type"],
                    owner_service=r["owner_service"],
                    revision=r["revision"],
                    uri=r.get("uri")
                )
                for r in data.get("resources", [])
            ]

            return ContextPackage(
                package_id=row["package_id"],
                goal_id=row["goal_id"],
                classification_level=ClassificationLevel(row["classification_level"]),
                snapshot_hash=row["snapshot_hash"],
                resources=resources,
                payload=data.get("payload", {}),
                created_at=row["created_at"],
                valid_until=row["valid_until"]
            )
        finally:
            conn.close()

    def get_by_snapshot_hash(self, snapshot_hash: str) -> Optional[ContextPackage]:
        """Recupera la revisión exacta consumida a partir del hash de snapshot (C12)."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT package_id FROM context_packages WHERE snapshot_hash = ? LIMIT 1;", (snapshot_hash,))
            row = cursor.fetchone()
            if not row:
                return None
            return self.get_package(row["package_id"])
        finally:
            conn.close()
