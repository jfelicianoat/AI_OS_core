# P05 — Agora: Job, binding, WorkerAdmission y restore

## ROL
Maintainer de Agora/AGR respetando Board e IDs nativos.

## OBJETIVO REAL
Hacer Agora autoridad de Jobs integrados sin reemplazar su modelo durable.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Agora Board/API + Runner.

## PRERREQUISITOS
P03 PASS.

## ENTRADAS
Spec, Cards/API/Runner/claim/recovery actuales.

## TAREA Y CAMBIOS EXACTOS
Implementar IdentityBinding global↔Card nativa sin renombrar; Job/JobDispatchRequest versionado e idempotente; blocked state; worker capabilities/resources; WorkerAdmission con exclusividad; Artifact authority/producer/custodian; full_state events/outbox/replay; OperationStatusQuery/OperationExecutionStatus/OperationReceipt. Si schema usa extra=forbid, crear versión/adaptador explícito.

## NO HACER
No calendario/Goal Engine/model routing; no asumir external_reference única.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C02,C03,C13,C16,C26,C04,C05,C15; retry dispatch, worker race, delayed state, restore.

## PRUEBAS REALES
Smoke Board/API+Runner reales si disponible.

## EVIDENCIAS A ENTREGAR
Binding, event timeline, WorkerAdmission, restore receipt.

## CRITERIOS DE ACEPTACIÓN
Task Manager puede reintentar sin duplicar Card y Agora conserva identidad/autoridad.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests/evidence, PHASE_RESULT; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
