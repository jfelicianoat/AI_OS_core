# P10 — E2E manual

## Fase / hito
M2

## Repositorios afectados
Core, Broker, Model Drift, Athena, Agora, Gestión Tareas, ChatyGPT; KO si aplica

## Prerrequisitos versionados
P02-P08 según E2E_REQUIREMENTS_MATRIX

## Entradas
Servicios reales + contratos 0.3

## Decisiones normativas obligatorias
P10 verifica; no crea infraestructura nueva.

## Entregables exclusivos
Recorrido manual completo, trace, certification manual, approvals si aplica, recovery/replay.

## Fuera de alcance
Planner, auto-cert, autonomy.

## Pruebas con fixtures / aisladas
Reusar C01-C14.

## Pruebas reales
Duplicate dispatch, delayed event, outage/replay, candidate enforcement, multi-job, hybrid segments.

## Evidencia de aceptación
E2E report con IDs/revisions/model/artifact hash.

## Condición de cierre
M2 demostrado sin añadir funcionalidad nueva.

## Artefactos a reabrir si cambia una decisión
Cualquier contrato contradicho por real.
