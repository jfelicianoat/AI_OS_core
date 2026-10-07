# P02 — Core approvals/policy/auth base

## Fase / hito
M0→M2

## Repositorios afectados
AI_OS_core

## Prerrequisitos versionados
P01; decisiones Policy/Approval aprobadas

## Entradas
Policy fixtures + auth matrix

## Decisiones normativas obligatorias
ApprovalAuthorization inmutable; usos/revocaciones separados; default deny.

## Entregables exclusivos
Policy evaluator base.
ApprovalRequest API.
ApprovalAuthorization.
ApprovalUse atómico.
ApprovalRevocation/EffectiveState.
principal/resource auth.
DecisionTrace.

## Fuera de alcance
Planner/autonomía.

## Pruebas con fixtures / aisladas
C06-C09, truth tables, concurrent consume.

## Pruebas reales
Smoke local con dos principals.

## Evidencia de aceptación
API contract + tests.

## Condición de cierre
ChatyGPT puede usar approvals sin ser security boundary.

## Artefactos a reabrir si cambia una decisión
Policy/Approval decision docs si cambian.
