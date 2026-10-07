# P07 — KO evidence/version support

## Fase / hito
M1 prereq mínimo; M3 completo

## Repositorios afectados
Knowledge_Orchestrator

## Prerrequisitos versionados
API KO inventariada

## Entradas
Resource refs/revisions/hashes/provenance

## Decisiones normativas obligatorias
Immutable revision o materialized snapshot; expiry != retention.

## Entregables exclusivos
stable refs; provenance; durable query adapter; events outbox; exact fragment materialization hook.

## Fuera de alcance
Full Context Engine.

## Pruebas con fixtures / aisladas
C12, superseded, polling, fragment roundtrip.

## Pruebas reales
Smoke KO real.

## Evidencia de aceptación
example ref/snapshot + trace.

## Condición de cierre
M2 puede auditar context evidence.

## Artefactos a reabrir si cambia una decisión
Retention decision si hace falta.
