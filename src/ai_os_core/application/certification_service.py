"""Servicio de aplicación para Proyección de Certificaciones (M0-CERT-PROJ).
Comentarios en español.
"""

from typing import Optional, List
from ai_os_core.domain.certifications import CertificationApplicability
from ai_os_core.infrastructure.db.repositories.certifications_repo import CertificationsRepository


class CertificationService:
    """Gestiona el catálogo proyectado de certificaciones de modelos y capacidades (M0-CERT-PROJ)."""

    def __init__(self, cert_repo: CertificationsRepository):
        self.cert_repo = cert_repo

    def register_certification(self, cert: CertificationApplicability) -> CertificationApplicability:
        """Almacena o actualiza la aplicabilidad de una certificación."""
        self.cert_repo.save_certification(cert)
        return cert

    def query_applicability(self, model_id: str, capability_id: str, version: str) -> Optional[CertificationApplicability]:
        """Consulta la proyección de aplicabilidad para una combinación concreta."""
        return self.cert_repo.get_certification(model_id, capability_id, version)

    def list_certifications(self) -> List[CertificationApplicability]:
        """Lista todas las certificaciones registradas."""
        return self.cert_repo.list_certifications()
