# P08 — ChatyGPT UI/client

## Fase / hito
M1/M2

## Repositorios afectados
ChatyGPT

## Prerrequisitos versionados
P02 + trace endpoints

## Entradas
Goals/approvals/traces

## Decisiones normativas obligatorias
Servidor valida auth; UI muestra freshness.

## Entregables exclusivos
Goals/Decisions client; Approval Inbox; exact/scoped UX; expiry refresh; trace; exclusion privacy; degraded Core.

## Fuera de alcance
Planner/policy authoring.

## Pruebas con fixtures / aisladas
expired approval, mutated action, hidden excluded resource, stale projection.

## Pruebas reales
Desktop smoke con Core si posible.

## Evidencia de aceptación
UI tests + traces.

## Condición de cierre
Usuario inspecciona/aprueba M2 sin ser security boundary.

## Artefactos a reabrir si cambia una decisión
No aplica
