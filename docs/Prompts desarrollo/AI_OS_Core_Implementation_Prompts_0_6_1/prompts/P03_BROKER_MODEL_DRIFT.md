# P03 — AI Broker + Model Drift: model gate y certificación manual

## ROL
Ingeniero de plataforma de inferencia/evaluación.

## OBJETIVO REAL
Entregar antes de M2 enforcement de modelo, evidencia efectiva, admisión y certificación manual.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
Repositorio servidor real de AI Broker + Model_Drift.

## PRERREQUISITOS
P02 PASS; identificar repo Broker real y ref/commit.

## ENTRADAS
Spec, APIs reales Broker/Model Drift, telemetría y contratos.

## TAREA Y CAMBIOS EXACTOS
Broker: ModelIdentityEvidence con provenance/status; ModelExecutionConstraint/candidate set; no-fallback fuera del set cuando mandatory; ModelInvocationEvidence requested/effective/fallback; InferenceAdmission; AICapacityForecast con muestra/confidence/insufficient_data; outbox/replay; OperationStatus/Receipt. Model Drift: ComparabilityAssessment, EvaluationVerdict, Certification histórica inmutable y ejecución manual de CertificationRequest. Actualizar la proyección Core por contratos públicos.

## NO HACER
No auto-trigger todavía, Goal Engine, scheduler ni fallback best-effort que viole constraint mandatory.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C10,C11,C17,C04,C05,C15; partial identity, forbidden fallback, restore.

## PRUEBAS REALES
Smoke con Broker real/modelo local si disponible; documentar lo no verificable.

## EVIDENCIAS A ENTREGAR
Model evidence, suite Model Drift, enforcement/admission/replay/restore traces.

## CRITERIOS DE ACEPTACIÓN
M2 puede exigir candidate set certificado y el punto de inferencia lo hace cumplir.

## FORMATO DE SALIDA DEL AGENTE
Findings, repo Broker identificado, cambios por repo, tests/evidence, PHASE_RESULT.
