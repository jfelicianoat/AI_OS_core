# P07 — Knowledge Orchestrator: contexto reproducible

## ROL
Maintainer de KO sin mover knowledge lifecycle al Core.

## OBJETIVO REAL
Dar garantías para M2-contextual y M3 Context Engine.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Knowledge_Orchestrator y AI OS Core únicamente para la capacidad mínima de ContextPackage previa a M2-contextual.

## PRERREQUISITOS
P01 aceptado para Core y P04 disponible para validar consumo Athena. Obligatorio sólo para M2-contextual.

## ENTRADAS
Spec, API KO, versioning/provenance actual.

## TAREA Y CAMBIOS EXACTOS
KO: stable ResourceReference, immutable revision/materialized snapshot, hash/provenance/classification, retrieved_at, validity_at_use, usable_until, historical retention, durable query, full_state events/outbox/replay y consumer_safe/privileged_audit.

Core mínimo: recibir selección explícita de refs/revisiones KO; autenticar principal y aplicar Authorization Matrix/Policy/classification; validar revisión/hash/snapshot; crear/persistir `ContextPackage` inmutable bajo autoridad Core; devolver ref; registrar provenance/exclusiones. Sin ranking semántico ni descubrimiento federado. Athena consume ese paquete y conserva evidencia.

Demostrar KO → ContextPackage autorizado por Core → Athena → Run con evidencia histórica exacta.

## NO HACER
No Goal Engine/scheduler; no DB/vault privado desde Core; hash no sustituye retención.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C12,C04,C05; superseded/expired, polling, snapshot round-trip.

## PRUEBAS REALES
Smoke KO real sin mutaciones destructivas.

## EVIDENCIAS A ENTREGAR
Immutable ref/snapshot + provenance/replay.

## CRITERIOS DE ACEPTACIÓN
Antes de P10B existe y está probada la ruta KO→Core ContextPackage→Athena→evidencia histórica. P10B sólo la verifica. P12 sigue siendo el primer proveedor del Context Engine federado/ranking completo.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests/evidence; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
