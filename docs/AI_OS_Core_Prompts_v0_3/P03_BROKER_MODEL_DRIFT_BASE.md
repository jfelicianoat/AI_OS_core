# P03 — Broker + Model Drift base

## Fase / hito
M1→M2

## Repositorios afectados
AI Broker servidor real + Model_Drift

## Prerrequisitos versionados
P00-P02; repo Broker real identificado

## Entradas
ModelIdentityEvidence, Certification, ModelExecutionConstraint

## Decisiones normativas obligatorias
Enforcement del candidate set antes de M2; cert histórica separada de applicability.

## Entregables exclusivos
Broker: identity evidence, capacity forecast, allowed candidate set/no-fallback, effective model/fallback evidence, execution admission, event outbox.
Model Drift: comparability assessment, manual certification, provenance.

## Fuera de alcance
Auto-trigger certification.

## Pruebas con fixtures / aisladas
C10-C11, partial identity, forbidden fallback.

## Pruebas reales
Smoke con Broker real/modelo local si posible.

## Evidencia de aceptación
contract diff + traces + report.

## Condición de cierre
M2 puede imponer set certificado.

## Artefactos a reabrir si cambia una decisión
Contratos si API real obliga.
