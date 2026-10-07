# P11 — Auto-certification

## Fase / hito
M3

## Repositorios afectados
Core, AI Broker, Model Drift

## Prerrequisitos versionados
M2 cerrado; manual cert y gate existen

## Entradas
model/skill/runtime/tool/policy events

## Decisiones normativas obligatorias
Primero comparability; luego request; historia inmutable.

## Entregables exclusivos
trigger rules; CertificationRequest outbox; idempotent execution; Applicability update; outage/stale behavior.

## Fuera de alcance
Crear gate Broker básico.

## Pruebas con fixtures / aisladas
duplicate requests, identity enrichment, quantization change, outage.

## Pruebas reales
Cambio controlado si seguro.

## Evidencia de aceptación
cert timeline/report.

## Condición de cierre
Availability se actualiza sin reescribir historia.

## Artefactos a reabrir si cambia una decisión
No aplica
