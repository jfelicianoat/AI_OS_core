"""Modelos de dominio para Auditoría y Trazas de Decisión (DecisionTrace).
Alineado con Normativa 0.6.1 (§1, §2) y caso M0-AUDIT.
Comentarios en español.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from .contracts import utc_now_iso


@dataclass(frozen=True)
class DecisionTrace:
    """Traza inmutable de una decisión adoptada por el control plane."""
    trace_id: str
    decision_type: str
    principal_id: str
    resource_id: Optional[str]
    inputs_digest: str
    decision_result: str
    matched_rules: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class AuditRecord:
    """Registro inmutable de auditoría para operaciones y mutaciones."""
    record_id: str
    operation_id: str
    principal_id: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)
