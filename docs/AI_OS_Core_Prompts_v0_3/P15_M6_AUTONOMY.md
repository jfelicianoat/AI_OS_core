# P15 — Autonomía condicional

## Fase / hito
M6

## Repositorios afectados
Core + executors

## Prerrequisitos versionados
M5 + DECISION_AUTONOMY

## Entradas
Policies, approvals, cert, admission, ceilings

## Decisiones normativas obligatorias
Blocked != A0; mínimo sólo A-levels después de gates.

## Entregables exclusivos
EffectiveExecutionDecision; promotion criteria; repair budgets; hard confirmations; revocation handling.

## Fuera de alcance
Self-modification ilimitada/irreversible autoactions.

## Pruebas con fixtures / aisladas
cert unknown, revoked approval, ceiling combos, repair max.

## Pruebas reales
Canary reversible low-risk.

## Evidencia de aceptación
decision traces + canary evidence.

## Condición de cierre
No irreversible autoexecutes.

## Artefactos a reabrir si cambia una decisión
No aplica
