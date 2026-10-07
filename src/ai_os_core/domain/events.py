"""Modelos de dominio para el sistema de eventos, outbox/inbox y garantías de secuencia.
Alineado con Normativa 0.6.1 (§6) y casos críticos C02, C03, C05.
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from .contracts import utc_now_iso


class EventType(str, Enum):
    """Tipos canónicos de eventos según la especificación."""
    FULL_STATE = "full_state"
    DELTA = "delta"
    AUDIT = "audit"
    NOTIFICATION = "notification"


@dataclass
class EventEnvelope:
    """Sobre canónico inmutable para todo evento en el sistema."""
    event_id: str
    producer_id: str
    stream_id: str
    stream_epoch: int
    source_sequence: int
    event_type: EventType
    resource_id: str
    resource_type: str
    revision: int
    payload: dict[str, Any]
    state_digest: Optional[str] = None
    quarantine: bool = False
    quarantine_reason: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)
    received_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa el evento a diccionario."""
        res = asdict(self)
        res["event_type"] = self.event_type.value
        return res


@dataclass
class ReplayCursor:
    """Cursor que indica el progreso de lectura/procesamiento de un consumidor."""
    consumer_id: str
    producer_id: str
    stream_id: str
    stream_epoch: int
    last_processed_sequence: int
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)


@dataclass
class ReplayGap:
    """Representa un salto irrecuperable en la secuencia de eventos (Caso C05)."""
    producer_id: str
    stream_id: str
    stream_epoch: int
    expected_sequence: int
    received_sequence: int
    detected_at: str = field(default_factory=utc_now_iso)
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        return asdict(self)
