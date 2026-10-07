"""Repositorio SQLite para Resource Graph e Identity Bindings (M0-GRAPH, C24).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.resources import ResourceNode, ResourceRelation
from ai_os_core.domain.contracts import IdentityBinding, utc_now_iso


class ResourcesRepository:
    """Gestiona el grafo de recursos federados y las vinculaciones de identidad nativa."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_resource(self, resource: ResourceNode) -> None:
        """Guarda o actualiza un nodo de recurso asegurando preservación del propietario canónico."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO resources (resource_id, resource_type, owner_service, revision, data_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id) DO UPDATE SET
                    revision = excluded.revision,
                    data_json = excluded.data_json,
                    updated_at = excluded.updated_at;
                """,
                (
                    resource.resource_id,
                    resource.resource_type,
                    resource.owner_service,
                    resource.revision,
                    json.dumps(resource.data),
                    resource.created_at,
                    resource.updated_at
                )
            )

    def get_resource(self, resource_id: str) -> Optional[ResourceNode]:
        """Obtiene un recurso por su ID."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources WHERE resource_id = ?;", (resource_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ResourceNode(
                resource_id=row["resource_id"],
                resource_type=row["resource_type"],
                owner_service=row["owner_service"],
                revision=row["revision"],
                data=json.loads(row["data_json"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        finally:
            conn.close()

    def add_relation(self, relation: ResourceRelation) -> None:
        """Añade una relación dirigida entre recursos."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO resource_relations (source_id, target_id, relation_type, created_at)
                VALUES (?, ?, ?, ?);
                """,
                (relation.source_id, relation.target_id, relation.relation_type, relation.created_at)
            )

    def get_relations_for(self, source_id: str) -> List[ResourceRelation]:
        """Obtiene las relaciones que parten del recurso dado."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resource_relations WHERE source_id = ? ORDER BY created_at ASC;",
                (source_id,)
            )
            rows = cursor.fetchall()
            return [
                ResourceRelation(
                    source_id=row["source_id"],
                    target_id=row["target_id"],
                    relation_type=row["relation_type"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]
        finally:
            conn.close()

    def save_identity_binding(self, binding: IdentityBinding) -> None:
        """Guarda una vinculación de identidad nativa preservando la revisión de adaptador (C24)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO identity_bindings (global_id, native_id, source_system, adapter_revision, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(global_id, source_system) DO UPDATE SET
                    native_id = excluded.native_id,
                    adapter_revision = excluded.adapter_revision;
                """,
                (
                    binding.global_id,
                    binding.native_id,
                    binding.source_system,
                    binding.adapter_revision,
                    binding.created_at
                )
            )

    def get_identity_binding(self, global_id: str, source_system: str) -> Optional[IdentityBinding]:
        """Recupera la vinculación de identidad nativa."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM identity_bindings WHERE global_id = ? AND source_system = ?;",
                (global_id, source_system)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return IdentityBinding(
                global_id=row["global_id"],
                native_id=row["native_id"],
                source_system=row["source_system"],
                adapter_revision=row["adapter_revision"],
                created_at=row["created_at"]
            )
        finally:
            conn.close()
