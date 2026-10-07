"""Repositorio SQLite para Servicios y Capacidades (M0-REG).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.capabilities import ServiceRegistration, CapabilityManifest, ServiceHealthStatus


class ServicesRepository:
    """Acceso a datos persistente para el catálogo de servicios y capacidades federadas."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def register_service(self, service: ServiceRegistration) -> None:
        """Registra o actualiza un servicio federado."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO services (service_id, name, base_url, version, health_status, capabilities_json, last_seen, registered_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(service_id) DO UPDATE SET
                    name=excluded.name,
                    base_url=excluded.base_url,
                    version=excluded.version,
                    health_status=excluded.health_status,
                    capabilities_json=excluded.capabilities_json,
                    last_seen=excluded.last_seen,
                    metadata_json=excluded.metadata_json;
                """,
                (
                    service.service_id,
                    service.name,
                    service.base_url,
                    service.version,
                    service.health_status.value,
                    json.dumps(service.capabilities),
                    service.last_seen,
                    service.registered_at,
                    json.dumps(service.metadata)
                )
            )

    def get_service(self, service_id: str) -> Optional[ServiceRegistration]:
        """Obtiene un servicio por su identificador único."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services WHERE service_id = ?;", (service_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ServiceRegistration(
                service_id=row["service_id"],
                name=row["name"],
                base_url=row["base_url"],
                version=row["version"],
                health_status=ServiceHealthStatus(row["health_status"]),
                capabilities=json.loads(row["capabilities_json"]),
                last_seen=row["last_seen"],
                registered_at=row["registered_at"],
                metadata=json.loads(row["metadata_json"])
            )
        finally:
            conn.close()

    def list_services(self) -> List[ServiceRegistration]:
        """Devuelve todos los servicios registrados."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services ORDER BY name ASC;")
            rows = cursor.fetchall()
            return [
                ServiceRegistration(
                    service_id=row["service_id"],
                    name=row["name"],
                    base_url=row["base_url"],
                    version=row["version"],
                    health_status=ServiceHealthStatus(row["health_status"]),
                    capabilities=json.loads(row["capabilities_json"]),
                    last_seen=row["last_seen"],
                    registered_at=row["registered_at"],
                    metadata=json.loads(row["metadata_json"])
                )
                for row in rows
            ]
        finally:
            conn.close()

    def register_capability(self, capability: CapabilityManifest) -> None:
        """Registra una capacidad asegurando consistencia con el servicio proveedor."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            # Verificar existencia del proveedor
            cursor.execute("SELECT service_id FROM services WHERE service_id = ?;", (capability.provider_service_id,))
            if not cursor.fetchone():
                raise ValueError(f"El servicio proveedor '{capability.provider_service_id}' no está registrado.")

            cursor.execute(
                """
                INSERT INTO capabilities (capability_id, name, description, provider_service_id, version, schema_version, is_available, input_schema_json, output_schema_json, registered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(capability_id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    provider_service_id=excluded.provider_service_id,
                    version=excluded.version,
                    schema_version=excluded.schema_version,
                    is_available=excluded.is_available,
                    input_schema_json=excluded.input_schema_json,
                    output_schema_json=excluded.output_schema_json;
                """,
                (
                    capability.capability_id,
                    capability.name,
                    capability.description,
                    capability.provider_service_id,
                    capability.version,
                    capability.schema_version,
                    1 if capability.is_available else 0,
                    json.dumps(capability.input_schema),
                    json.dumps(capability.output_schema),
                    capability.registered_at
                )
            )

    def get_capability(self, capability_id: str) -> Optional[CapabilityManifest]:
        """Obtiene una capacidad por su ID."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM capabilities WHERE capability_id = ?;", (capability_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return CapabilityManifest(
                capability_id=row["capability_id"],
                name=row["name"],
                description=row["description"],
                provider_service_id=row["provider_service_id"],
                version=row["version"],
                schema_version=row["schema_version"],
                is_available=bool(row["is_available"]),
                input_schema=json.loads(row["input_schema_json"]),
                output_schema=json.loads(row["output_schema_json"]),
                registered_at=row["registered_at"]
            )
        finally:
            conn.close()
