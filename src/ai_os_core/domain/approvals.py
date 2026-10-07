"""Modelos de dominio para el sistema de Approvals (Autorizaciones y Usos).
Alineado con Normativa 0.6.1 (§5) y casos C06, C07.
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from .contracts import utc_now_iso


class ApprovalStatus(str, Enum):
    """Estado efectivo de una autorización."""
    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class ApprovalAuthorization:
    """Autorización concedida inmutable (§5)."""
    authorization_id: str
    scope: str
    max_uses: int = 1
    expires_at: Optional[str] = None
    expected_digest: Optional[str] = None
    granted_by: str = "human"
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class ApprovalUse:
    """Registro de uso comprometido de una autorización."""
    use_id: str
    authorization_id: str
    operation_id: str
    operation_digest: str
    committed_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class ApprovalRevocation:
    """Revocación formal de una autorización."""
    revocation_id: str
    authorization_id: str
    revoked_by: str
    reason: str
    revoked_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass
class ApprovalEffectiveState:
    """Estado consolidado y calculado de una autorización."""
    authorization_id: str
    status: ApprovalStatus
    max_uses: int
    used_count: int
    remaining_uses: int
    is_revoked: bool = False
    is_expired: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        res = asdict(self)
        res["status"] = self.status.value
        return res
