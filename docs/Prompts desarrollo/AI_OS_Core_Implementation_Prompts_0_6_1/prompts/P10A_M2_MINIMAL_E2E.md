# P10A — M2-minimal: verificación E2E

## ROL
Integrador/verificador E2E; no implementes funciones faltantes.

## OBJETIVO REAL
Demostrar los 20 requisitos M2-minimal con servicios reales.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
Core, Broker, Model Drift, Athena, Agora, Gestión Tareas IA, ChatyGPT.

## PRERREQUISITOS
P02,P03,P04,P05,P06,P08 PASS.

## ENTRADAS
Spec, builds reales y evidencias previas.

## TAREA Y CAMBIOS EXACTOS
Ejecutar escenario real/reversible Goal/Task→Job→Run→Broker→Artifact. Registrar correlation/operation IDs, approval/budget si aplica, certification applicability, candidate set, effective model, WorkerAdmission, InferenceAdmission, Job/Run/Artifact y aggregation. Si falta una función, señalar la fase proveedora; P10A no la implementa.

## NO HACER
No Planner/auto-cert/autonomy ni quick fixes de infraestructura.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C01,C02,C04,C05,C06,C07,C09,C10,C11,C13,C14,C15,C16,C17,C25,C26 y UI-M2 según corresponda.

## PRUEBAS REALES
Servicios reales, operaciones reversibles/no destructivas.

## EVIDENCIAS A ENTREGAR
E2E timeline, IDs/revisions, effective model, admissions, artifact hash, verification/recovery.

## CRITERIOS DE ACEPTACIÓN
Los 20 requisitos M2-minimal tienen evidencia o un fallo atribuido a provider phase.

## FORMATO DE SALIDA DEL AGENTE
E2E_PROFILE M2-minimal, requirement→evidence, tests/gaps, PHASE_RESULT.
