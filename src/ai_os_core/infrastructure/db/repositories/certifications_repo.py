"""Repositorio SQLite para la Proyección de Certificaciones (M0-CERT-PROJ).
Comentarios en español.
"""

import sqlite3
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.certifications import CertificationApplicability, EvaluationVerdict
from ai_os_core.domain.contracts import utc_now_iso
from ai_os_core.domain.errors import ConflictError


class CertificationsRepository:
    """Gestiona la proyección local de certificaciones evaluadas originalmente por Model Drift."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_certification(self, cert: CertificationApplicability) -> None:
        """Guarda o actualiza la proyección de certificación con frescura y revisión (M0-CERT-PROJ)."""
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO certification_applicability (
                    model_id, capability_id, version, source_system, evaluation_verdict,
                    is_applicable, last_verified_at, revision
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(model_id, capability_id, version) DO UPDATE SET
                    source_system = excluded.source_system,
                    evaluation_verdict = excluded.evaluation_verdict,
                    is_applicable = excluded.is_applicable,
                    last_verified_at = excluded.last_verified_at,
                    revision = excluded.revision
                WHERE excluded.revision >= certification_applicability.revision;
                """,
                (
                    cert.model_id,
                    cert.capability_id,
                    cert.version,
                    cert.source_system,
                    cert.evaluation_verdict.value,
                    1 if cert.is_applicable else 0,
                    cert.last_verified_at,
                    cert.revision
                )
            )
            # La proyección es monótona: una revisión anterior que llega tarde
            # (reintento, reenvío desordenado) no puede deshacer una posterior.
            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT revision FROM certification_applicability WHERE model_id = ? AND capability_id = ? AND version = ?;",
                    (cert.model_id, cert.capability_id, cert.version)
                )
                current = cursor.fetchone()["revision"]
                raise ConflictError(
                    f"Revisión obsoleta {cert.revision} para '{cert.model_id}:{cert.capability_id}:{cert.version}': "
                    f"la proyección ya está en la revisión {current}."
                )

    def get_certification(self, model_id: str, capability_id: str, version: str) -> Optional[CertificationApplicability]:
        """Consulta la aplicabilidad de una combinación modelo/capacidad."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM certification_applicability
                WHERE model_id = ? AND capability_id = ? AND version = ?;
                """,
                (model_id, capability_id, version)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return CertificationApplicability(
                model_id=row["model_id"],
                capability_id=row["capability_id"],
                version=row["version"],
                source_system=row["source_system"],
                evaluation_verdict=EvaluationVerdict(row["evaluation_verdict"]),
                is_applicable=bool(row["is_applicable"]),
                last_verified_at=row["last_verified_at"],
                revision=row["revision"]
            )
        finally:
            conn.close()

    def list_certifications(self) -> List[CertificationApplicability]:
        """Lista todas las certificaciones proyectadas."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM certification_applicability ORDER BY last_verified_at DESC;")
            rows = cursor.fetchall()
            return [
                CertificationApplicability(
                    model_id=row["model_id"],
                    capability_id=row["capability_id"],
                    version=row["version"],
                    source_system=row["source_system"],
                    evaluation_verdict=EvaluationVerdict(row["evaluation_verdict"]),
                    is_applicable=bool(row["is_applicable"]),
                    last_verified_at=row["last_verified_at"],
                    revision=row["revision"]
                )
                for row in rows
            ]
        finally:
            conn.close()
