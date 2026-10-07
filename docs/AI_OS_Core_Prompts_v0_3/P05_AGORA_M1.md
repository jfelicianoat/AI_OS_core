# P05 — Agora binding/Jobs/admission

## Fase / hito
M1→M2

## Repositorios afectados
Agora

## Prerrequisitos versionados
P03 + IdentityBinding/Job contracts

## Entradas
Job, IdentityBinding, JobDispatchRequest, ExecutionAdmission

## Decisiones normativas obligatorias
Conservar IDs nativos; adaptar extra=forbid; varios eventos misma revision permitidos.

## Entregables exclusivos
IdentityBinding durable; endpoint/adaptador versionado; job.blocked; source sequence/epoch; worker capabilities; worker admission; outbox/replay.

## Fuera de alcance
Calendario/model certification eval.

## Pruebas con fixtures / aisladas
retry dispatch, delayed ordering, binding persistence, C03.

## Pruebas reales
Smoke Board/API+Runner si posible.

## Evidencia de aceptación
contract tests + trace.

## Condición de cierre
Task Manager puede crear Job idempotente.

## Artefactos a reabrir si cambia una decisión
Binding semantics si difieren.
