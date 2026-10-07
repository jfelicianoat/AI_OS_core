# Decisión candidata — Eventos/replay
Estado: proposed

## Stream
- producer_id autenticado
- stream_id estable por dominio
- stream_epoch nuevo ante reset/reinstall/restore de secuencia
- source_sequence monotónica dentro del epoch

## Resource revision
Usar revisión nativa si existe.
Si no, adapter_revision durable y etiquetada como adapter_assigned.

## Varios eventos en misma revisión
Permitidos.

Conflictos:
1. mismo event_id + digest diferente => integridad conflict
2. eventos distintos misma revision => permitido
3. dos `full_state` mismo recurso/revision con state_digest diferente => contradiction/quarantine
4. delta/audit/notification no se comparan byte a byte con full_state

EventEnvelope declara `representation`: full_state | delta | audit | notification.

## Delivery
Productor persiste outbox con el cambio local cuando sea posible.
Core ACK sólo después de persistir.
Cursor por stream/epoch.

## Gap
Si secuencia no recuperable:
- REPLAY_GAP
- suspender proyección incremental
- obtener snapshot/reconcile
- reanudar desde base confirmada

## Idempotency
Namespace: principal + operation + key.
Estados: in_progress/completed/failed_retryable/failed_terminal.

## Restore
Comandos externos con operation_id estable.
Después de restore consultar receipt antes de reenviar.
