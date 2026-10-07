# Hitos

M0 Core aislado con fixtures.
M1 observación integrada sin dispatch.
M2 E2E manual Task→Job→Run→Broker→Artifact.
M3 auto-certification + Context.
M4 Policy Engine completo.
M5 Planner tipado.
M6 autonomía condicional.

Planner:
- reside en AI OS Core / PlanningService
- usa AI Broker para inferencia
- Core es owner de TypedPlanProposal
- solicita a Gestión Tareas crear Tasks
- no escribe calendario
- no crea Jobs directamente
