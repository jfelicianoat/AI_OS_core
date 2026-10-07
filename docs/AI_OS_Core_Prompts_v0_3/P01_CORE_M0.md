# P01 — AI OS Core M0

## Fase / hito
M0

## Repositorios afectados
AI_OS_core

## Prerrequisitos versionados
P00 cerrado

## Entradas
Contratos 0.3/fixtures/state tables

## Decisiones normativas obligatorias
DECISION_SQLITE_DURABILITY y DECISION_EVENT_DELIVERY.

## Entregables exclusivos
FastAPI + SQLite WAL/FULL.
Registry de servicios/capabilities.
Goals/Decisions/Resources.
Event inbox/store/replay cursor.
Idempotency, audit, health, paginación estable.

## Fuera de alcance
Integraciones reales, Planner, dispatch, KO federado.

## Pruebas con fixtures / aisladas
C01-C03, restart, migrations, auth scope.

## Pruebas reales
No aplica.

## Evidencia de aceptación
test report + OpenAPI snapshot.

## Condición de cierre
Core aislado arranca y supera M0.

## Artefactos a reabrir si cambia una decisión
Contratos si aparece ambigüedad.
