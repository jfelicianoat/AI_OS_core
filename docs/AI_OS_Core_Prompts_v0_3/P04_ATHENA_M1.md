# P04 — Athena integration

## Fase / hito
M1→M2

## Repositorios afectados
Athena

## Prerrequisitos versionados
P03 disponible

## Entradas
Capability/Skill manifests, ExecutionFingerprint

## Decisiones normativas obligatorias
No elevar permisos; effective model siempre registrado.

## Entregables exclusivos
Manifests, run correlation, execution fingerprint, model invocation refs, context evidence hooks, event outbox, approval recognition opcional sin saltar PermissionEngine.

## Fuera de alcance
Planner/scheduling.

## Pruebas con fixtures / aisladas
permission invariants, strict model set, fallback evidence, replay.

## Pruebas reales
Smoke run real si posible.

## Evidencia de aceptación
run trace + fixtures.

## Condición de cierre
Standalone intacto e integración respeta constraints.

## Artefactos a reabrir si cambia una decisión
Approval trust si cambia.
