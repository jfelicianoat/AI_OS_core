"""Modelos de dominio para la Proyección de Certificaciones (M0-CERT-PROJ, C11).
Comentarios en español.
"""

from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Optional
from ai_os_core.domain.contracts import utc_now_iso


class EvaluationVerdict(str, Enum):
    """Veredicto emitido originalmente por Model Drift."""
    CERTIFIED = "CERTIFIED"
    REJECTED = "REJECTED"
    INDETERMINATE = "INDETERMINATE"
    EXPIRED = "EXPIRED"


@dataclass
class CertificationApplicability:
    """Proyección en AI OS Core de la aplicabilidad de certificación de un modelo/capacidad."""
    model_id: str
    capability_id: str
    version: str
    source_system: str
    evaluation_verdict: EvaluationVerdict
    is_applicable: bool
    last_verified_at: str = field(default_factory=utc_now_iso)
    revision: int = 1
    #: SHA-256 (hex en minúsculas) de la evidencia que respalda el veredicto.
    evidence_sha256: Optional[str] = None
    #: ISO 8601 UTC. Pasada esta hora, la certificación se lee como EXPIRED.
    expires_at: Optional[str] = None

    def as_of(self, now: Optional[datetime] = None) -> "CertificationApplicability":
        """La certificación tal como vale ahora: caducada, EXPIRED y no aplicable.

        No modifica lo guardado: la caducidad se decide al leer, no la pone nadie a mano.
        """
        if self.expires_at is None:
            return self
        now = now or datetime.now(timezone.utc)
        if datetime.fromisoformat(self.expires_at) > now:
            return self
        return CertificationApplicability(**{**asdict(self), "evaluation_verdict": EvaluationVerdict.EXPIRED,
                                             "is_applicable": False})

    def to_dict(self) -> dict:
        res = asdict(self)
        res["evaluation_verdict"] = self.evaluation_verdict.value
        return res
