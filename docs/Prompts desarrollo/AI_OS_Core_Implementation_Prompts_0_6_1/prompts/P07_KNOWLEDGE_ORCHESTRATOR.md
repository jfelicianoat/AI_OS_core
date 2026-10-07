# P07 — Knowledge Orchestrator: contexto reproducible

## ROL
Maintainer de KO sin mover knowledge lifecycle al Core.

## OBJETIVO REAL
Dar garantías para M2-contextual y M3 Context Engine.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
Knowledge_Orchestrator.

## PRERREQUISITOS
P01 PASS; obligatorio sólo para M2-contextual.

## ENTRADAS
Spec, API KO, versioning/provenance actual.

## TAREA Y CAMBIOS EXACTOS
Proporcionar stable ResourceReference, immutable revision o materialized snapshot, content hash/provenance/classification, retrieved_at, validity_at_use, usable_until, historical_evidence_retention_until, durable query adapter, full_state events/outbox/replay y soporte consumer_safe/privileged_audit. Si KO no retiene suficiente historial, materializar exactamente el fragmento consumido.

## NO HACER
No Goal Engine/scheduler; no DB/vault privado desde Core; hash no sustituye retención.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C12,C04,C05; superseded/expired, polling, snapshot round-trip.

## PRUEBAS REALES
Smoke KO real sin mutaciones destructivas.

## EVIDENCIAS A ENTREGAR
Immutable ref/snapshot + provenance/replay.

## CRITERIOS DE ACEPTACIÓN
M2-contextual puede demostrar contenido exacto consumido.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests/evidence, PHASE_RESULT.
