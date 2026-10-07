# P11 — M3: auto-certification

## ROL
Integrador Core/Broker/Model Drift.

## OBJETIVO REAL
Automatizar certificación sin reescribir historia ni crear el gate por primera vez.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
AI OS Core, AI Broker, Model Drift; consumidores Athena/Agora.

## PRERREQUISITOS
M2 PASS y gate/manual certification ya existen.

## ENTRADAS
Spec y eventos model/skill/runtime/tool/policy.

## TAREA Y CAMBIOS EXACTOS
Implementar comparability-driven triggers, CertificationRequest durable/idempotente, ejecución Model Drift, Certification histórica inmutable, update CertificationApplicability y CapabilityAvailability, outage/stale fail-closed. Una combinación nueva no hereda certificación.

## NO HACER
No otro evaluador, no unknown→certified, no reescribir Certification histórica.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Duplicate requests, identity enrichment, quantization/runtime/tool changes, Model Drift outage.

## PRUEBAS REALES
Cambio controlado/reversible si posible.

## EVIDENCIAS A ENTREGAR
Certification timeline/evidence refs.

## CRITERIOS DE ACEPTACIÓN
Applicability se actualiza automáticamente manteniendo model gate.

## FORMATO DE SALIDA DEL AGENTE
Findings, changes, tests/evidence,; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
