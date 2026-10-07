# Prompt 00D — Eventos, idempotencia, replay y durabilidad

## FASE ARQUITECTÓNICA
OS-0.

## PRERREQUISITOS
00B y 00C.

## OBJETIVO REAL
Definir efectos correctos bajo duplicados, caídas, eventos tardíos y Core desconectado.

## EVENTO

Añadir:
- `source_sequence` monotónica por productor o stream;
- `resource_revision` cuando el evento representa cambio de recurso;
- `event_id`;
- `occurred_at`;
- `recorded_at`;
- `correlation_id`;
- `causation_id`.

ULID no sustituye `resource_revision` ni `source_sequence`.

## ENTREGA DESDE PRODUCTORES
Elegir un patrón interoperable:
- outbox durable del productor + POST al Core + ACK;
- replay por cursor/sequence;
- retención mínima configurable.

Definir:
- ACK sólo después de persistir evento;
- reintentos;
- duplicados;
- huecos;
- productor offline mientras Core está apagado;
- poison events / dead-letter durable y reproceso manual.

## ORDEN
Para una proyección de recurso:
- nunca retroceder `resource_revision`;
- evento más antiguo queda registrado pero no revierte proyección;
- evento con misma revisión y payload incompatible => conflict/audit;
- reconciliación también debe comparar revisión, no sólo owner.

## TRANSACCIONES INTERNAS
Especificar:
1. escritura de negocio + evento local/outbox en la misma transacción;
2. `(event_id, handler)` UNIQUE;
3. efecto local del handler + marcado procesado en una misma transacción cuando ambos son DB local;
4. para efectos externos futuros: internal outbox + idempotency del receptor.

## IDEMPOTENCY
Clave con namespace:
`principal + operation + idempotency_key`.

Guardar:
- request hash canónico;
- estado `in_progress/completed/failed_retryable`;
- response reference/body reproducible;
- expiry policy.

Dos requests concurrentes con misma key:
- mismo body => una operación;
- body distinto => 409.

## DURABILIDAD SQLITE
No llamar “durable frente a power loss” a WAL + NORMAL.
Documentar dos perfiles:
- `standard`: WAL + NORMAL, tolera crash de proceso y preserva consistencia;
- `critical`: WAL + FULL (o decisión equivalente validada) para approvals/events/idempotency si se exige no perder commits recientes ante corte eléctrico.

Elegir perfil por tabla/operación y justificarlo.
Definir RPO/RTO objetivo como requisitos, no como hechos medidos.

## ACEPTACIÓN
Resolver inequívocamente:
- Core apagado 2h;
- duplicate simultaneous command;
- crash tras Goal antes de event;
- crash tras handler effect antes de mark;
- completed llega antes que delayed started;
- replay después de restart.
