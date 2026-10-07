"""Servicio de aplicación para Gestión e Ingesta de Eventos (C02, C03, C05).
Comentarios en español.
"""

from typing import Tuple, Optional, List, Dict, Any
from ..domain.events import EventEnvelope, ReplayGap
from ..infrastructure.db.repositories.events_repo import EventsRepository


class EventService:
    """Orquesta la recepción, deduplicación, cuarentena y proyecciones canónicas de eventos."""

    def __init__(self, events_repo: EventsRepository):
        self.events_repo = events_repo

    def ingest_event(self, event: EventEnvelope) -> Tuple[bool, Optional[str]]:
        """Ingesta un evento aplicando reglas de secuencia y consistencia canónica.
        Devuelve (aceptado_en_proyeccion, motivo_cuarentena_o_gap).
        """
        return self.events_repo.ingest_event(event)

    def get_canonical_state(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Recupera la proyección canónica vigente del recurso."""
        return self.events_repo.get_latest_canonical_state(resource_id)

    def list_unresolved_gaps(self) -> List[ReplayGap]:
        """Obtiene la lista de saltos de secuencia pendientes de reconciliación."""
        return self.events_repo.list_unresolved_gaps()

    def list_quarantined_events(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista los eventos en cuarentena pendientes de revisión."""
        return self.events_repo.list_quarantined_events(limit, offset)
