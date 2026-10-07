# Prompt 14 — OS-9 Planner tipado

## PRERREQUISITOS
Policy Engine estable; E2E manual validado; Context Engine disponible.

## OBJETIVO
Introducir razonamiento de planificación sin permitir ejecución de texto libre.

## FLUJO
Goal + ContextPackage
→ AI Broker inference
→ `TypedPlanProposal`
→ schema validation
→ cycle detection
→ policy evaluation
→ capability availability
→ certification applicability
→ human review
→ creación de Tasks.

## EL PLANNER NO
- ejecuta tools directamente;
- crea Jobs;
- modifica calendario por sí mismo;
- amplía permisos;
- decide que una certificación desconocida equivale a válida.

## PLAN
Debe declarar:
- Objectives;
- Tasks;
- actor;
- dependency graph;
- human intervals;
- capabilities;
- artifacts expected;
- acceptance criteria;
- unresolved assumptions.

## VERIFICACIÓN
- invalid graph rejected;
- unsupported capability surfaced;
- human approval before commit in initial deployment;
- every assumption explicit.
