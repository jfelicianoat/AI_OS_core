"""Contratos canónicos fundamentales y de identidad para AI OS Core.
Alineados con la especificación normativa 0.6.1 (§2).
Comentarios en español.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Any
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Devuelve la marca de tiempo actual en formato ISO 8601 UTC."""
    return datetime.now(timezone.utc).isoformat()


def normalize_iso_utc(value: str) -> str:
    """Valida una fecha ISO 8601 y la devuelve en UTC con el formato de utc_now_iso.

    Comparar caducidades como texto sólo es correcto si todas las fechas tienen el
    mismo formato y zona: "2099-01-01T00:00:00+01:00" o "mañana" comparados como
    cadenas daban resultados arbitrarios. Una fecha sin zona se interpreta en UTC.
    """
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValueError(f"Fecha ISO 8601 inválida: '{value}'.")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def is_expired(expires_at: str | None, now_iso: str | None = None) -> bool:
    """Indica si una fecha de caducidad ya ha pasado, comparando instantes y no texto."""
    if not expires_at:
        return False
    now = datetime.fromisoformat(normalize_iso_utc(now_iso)) if now_iso else datetime.now(timezone.utc)
    return datetime.fromisoformat(normalize_iso_utc(expires_at)) < now


@dataclass(frozen=True)
class ResourceReference:
    """Referencia federada canónica hacia un recurso gestionado."""
    resource_id: str
    resource_type: str
    owner_service: str
    revision: int = 1
    uri: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convierte la referencia a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class IdentityBinding:
    """Vinculación entre una identidad canónica global y un identificador nativo externo."""
    global_id: str
    native_id: str
    source_system: str
    adapter_revision: int = 1
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa la vinculación a diccionario."""
        return asdict(self)


@dataclass(frozen=True)
class ProducerStreamIdentity:
    """Identidad declarada de un flujo productor de eventos."""
    producer_id: str
    stream_id: str
    stream_epoch: int = 1

    def to_key(self) -> str:
        """Genera una clave única compuesta."""
        return f"{self.producer_id}:{self.stream_id}:{self.stream_epoch}"
