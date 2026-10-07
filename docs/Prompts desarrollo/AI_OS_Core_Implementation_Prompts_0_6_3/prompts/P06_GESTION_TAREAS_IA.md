# P06 — Gestión Tareas IA: humano+IA y Task→Job

## ROL
Maintainer del planificador/calendario humano.

## OBJETIVO REAL
Añadir Tasks IA/híbridas y puente a Agora sin equiparar compute con agenda humana.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Gestion Tareas IA.

## PRERREQUISITOS
P05 y P03 PASS.

## ENTRADAS
Spec, Tasks/calendario actual, Google Calendar read-only, Agora/Broker contracts.

## TAREA Y CAMBIOS EXACTOS
Añadir actor human/ai/hybrid/system; HumanWorkSegment múltiples; TaskDependency DAG; Task→Job idempotent bridge; aggregation all_required/any_success/quorum/ordered_pipeline; consumo Job lifecycle; AICapacityForecast como forecast no reserva; provisional vs confirmed al producirse admissions; queue/compute/wall-clock separados; timezone/DST; outbox/replay. Sólo HumanWorkSegment bloquea agenda.

## NO HACER
No routing/agent runtime/hard future GPU reservation; Google Calendar sigue read-only.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C01,C13,C14,C25,C04,C05; H→AI→AI→H, no-history, ETA, DST, multi-job.

## PRUEBAS REALES
Smoke con Agora real y verificar cero escrituras Google Calendar.

## EVIDENCIAS A ENTREGAR
Task→Job trace, calendario/segments/aggregation.

## CRITERIOS DE ACEPTACIÓN
P10 no descubre puentes faltantes y la agenda humana sigue correcta.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests/evidence,; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
