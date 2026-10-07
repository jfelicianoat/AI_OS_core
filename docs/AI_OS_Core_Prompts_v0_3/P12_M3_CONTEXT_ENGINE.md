# P12 — Context Engine

## Fase / hito
M3

## Repositorios afectados
Core + KO/Task/Agora/Athena read APIs

## Prerrequisitos versionados
M2; P07; auth matrix

## Entradas
Context contracts

## Decisiones normativas obligatorias
Authorization before ranking; mutable refs no bastan.

## Entregables exclusivos
federated resolver; principal/classification filters; materialized refs; safe/audit exclusions; retention; reproducibility.

## Fuera de alcance
Planner.

## Pruebas con fixtures / aisladas
C12 + auth leakage.

## Pruebas reales
Smoke con contexto real.

## Evidencia de aceptación
historical reproduction report.

## Condición de cierre
Context exacto reproducible.

## Artefactos a reabrir si cambia una decisión
Retention si cambia.
