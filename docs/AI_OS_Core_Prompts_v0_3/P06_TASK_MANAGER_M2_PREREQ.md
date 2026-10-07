# P06 — Gestión Tareas humano/IA + Task→Job

## Fase / hito
OS-4→M2

## Repositorios afectados
Gestion Tareas IA

## Prerrequisitos versionados
P05 dispatch + P03 forecast

## Entradas
Task, HumanWorkSegment, dependencies, forecast

## Decisiones normativas obligatorias
No hard GPU reservation futura en MVP; forecast provisional; admission runtime.

## Entregables exclusivos
actor; HumanWorkSegment; DAG; Task→Job idempotente; consume lifecycle; multi-job aggregation; ETA forecast; provisional/confirmed; TZ/DST.

## Fuera de alcance
Planner/hard reservations.

## Pruebas con fixtures / aisladas
C13-C14, cycles, no-history, duplicate dispatch.

## Pruebas reales
Smoke con Agora; Google Calendar read-only.

## Evidencia de aceptación
task/job trace.

## Condición de cierre
P10 no descubre puente nuevo.

## Artefactos a reabrir si cambia una decisión
Scheduling model si cambia.
