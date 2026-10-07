# Changelog — Normative Spec 0.6

## S01
Restituidas como invariantes normativos:
- default DENY;
- classification ceiling efectivo;
- ServiceRegistration allowlist/SSRF;
- prohibición de forwarding de credenciales a destino no autorizado.

## S02
Acceptance Registry/verifier:
- concordancia decisión ↔ AcceptanceRecord por ID/revisión/hash;
- dependencias transitivas;
- referencias inexistentes;
- ciclos;
- aceptación invalidada;
- compatibilidad explícita de pre-P01 con la revisión normativa.

## S03
Añadida matriz de conservación 0.4→0.6 y anchors obligatorios para:
identidad/revisiones, approvals exact/scoped, idempotencia atómica, contexto histórico,
Task DAG, roles de Artifact, frontera del Planner y gates de autonomía.

## S04
El verificador ahora:
- prohíbe P10 como provider;
- exige provider == verifier o precedencia transitiva;
- cruza Test↔Requirement en ambos sentidos;
- declara expresamente que no certifica semántica funcional de los tests.
