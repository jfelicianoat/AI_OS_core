# P14 — Planner tipado

## Fase / hito
M5

## Repositorios afectados
AI OS Core PlanningService + AI Broker + Gestión Tareas

## Prerrequisitos versionados
M3 Context; M4 Policy; M2 estable

## Entradas
Goal + Context + registry

## Decisiones normativas obligatorias
Planner owner Core; Broker infiere; Task Manager crea Tasks.

## Entregables exclusivos
TypedPlanProposal; Broker inference; schema/DAG/policy/capability/cert checks; human commit; request Task creation.

## Fuera de alcance
Autoexecute sin approval.

## Pruebas con fixtures / aisladas
invalid graph, unsupported capability, budget, assumptions.

## Pruebas reales
Real plan proposal sin auto commit.

## Evidencia de aceptación
proposal + validation trace.

## Condición de cierre
Planner no evita Task Manager/Policy.

## Artefactos a reabrir si cambia una decisión
Boundary si producto cambia.
