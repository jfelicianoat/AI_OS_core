"""Endpoints REST para Ingesta de Eventos e Inbox (C02, C03, C05).
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from ai_os_core.api.schemas.common import EventIngestRequest, EventIngestResponse
from ai_os_core.domain.events import EventEnvelope, EventType
from ai_os_core.application.event_service import EventService
from ai_os_core.infrastructure.db.repositories.events_repo import DUPLICATE_EVENT_REASON
from ai_os_core.api.dependencies import get_event_service

router = APIRouter(prefix="/api/v1/events", tags=["Events & Inbox"])


@router.post("/inbox", response_model=EventIngestResponse)
def ingest_event(req: EventIngestRequest, service: EventService = Depends(get_event_service)):
    """Ingesta un evento en el inbox canónico con verificación de secuencia y cuarentena."""
    try:
        ev_type = EventType(req.event_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de evento inválido '{req.event_type}'. Tipos soportados: {[e.value for e in EventType]}"
        )

    envelope = EventEnvelope(
        event_id=req.event_id,
        producer_id=req.producer_id,
        stream_id=req.stream_id,
        stream_epoch=req.stream_epoch,
        source_sequence=req.source_sequence,
        event_type=ev_type,
        resource_id=req.resource_id,
        resource_type=req.resource_type,
        revision=req.revision,
        payload=req.payload,
        state_digest=req.state_digest
    )

    accepted, reason = service.ingest_event(envelope)

    return EventIngestResponse(
        event_id=envelope.event_id,
        accepted_in_canonical_projection=accepted,
        quarantine=envelope.quarantine,
        duplicate=bool(reason and reason.startswith(DUPLICATE_EVENT_REASON)),
        reason=reason
    )


@router.get("/canonical/{resource_id}")
def get_canonical_state(resource_id: str, service: EventService = Depends(get_event_service)):
    """Obtiene la proyección canónica vigente de un recurso."""
    state = service.get_canonical_state(resource_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No hay proyección canónica para el recurso '{resource_id}'.")
    return state


@router.get("/gaps")
def list_replay_gaps(service: EventService = Depends(get_event_service)):
    """Lista todos los saltos de secuencia pendientes de reconciliación (C05)."""
    gaps = service.list_unresolved_gaps()
    return [g.to_dict() for g in gaps]


@router.get("/quarantine")
def list_quarantined_events(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: EventService = Depends(get_event_service)
):
    """Lista los eventos retenidos en cuarentena (REPLAY_GAP, full_state contradictorio)."""
    items = service.list_quarantined_events(limit=limit, offset=offset)
    return {"items": items, "total_returned": len(items), "limit": limit, "offset": offset}
