"""Modelos de dominio para la Proyección de Certificaciones (M0-CERT-PROJ, C11).
Comentarios en español.
"""

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

    def to_dict(self) -> dict:
        res = asdict(self)
        res["evaluation_verdict"] = self.evaluation_verdict.value
        return res
