# P10A — M2-minimal: verificación E2E

## ROL
Integrador/verificador E2E; no implementes funciones faltantes.

## OBJETIVO REAL
Demostrar los 20 requisitos M2-minimal con servicios reales.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Core, Broker, Model Drift, Athena, Agora, Gestión Tareas IA, ChatyGPT.

## PRERREQUISITOS
P02,P03,P04,P05,P06,P08 con resultado técnico PASS y gates/aceptaciones exigibles vigentes. Aplicar `E2E_ACCEPTANCE_PROTOCOL.md`. Alias normativo: `P10-minimal`.

## ENTRADAS
Spec, builds reales y evidencias previas.

## TAREA Y CAMBIOS EXACTOS
Ejecutar escenarios reales/reversibles que cubran los 20 requisitos M2-minimal. Mantener matriz `requirement_id → SATISFIED|FAILED|NOT_VERIFIED → evidence_refs → provider_phase → build/config fingerprints`. El flujo principal registra IDs, certification applicability, candidate set, effective model, WorkerAdmission, InferenceAdmission, Job/Run/Artifact y aggregation. Approval/budget siguen siendo requisitos: añadir escenarios que los activen. Si falta función, atribuirla y devolver FAIL/BLOCKED; P10A no implementa infraestructura.

## NO HACER
No Planner/auto-cert/autonomy ni quick fixes de infraestructura.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C01,C02,C04,C05,C06,C07,C09,C10,C11,C13,C14,C15,C16,C17,C25,C26 y UI-M2 según corresponda.

## PRUEBAS REALES
Servicios reales, operaciones reversibles/no destructivas.

## EVIDENCIAS A ENTREGAR
E2E timeline, IDs/revisions, effective model, admissions, artifact hash, verification/recovery.

## CRITERIOS DE ACEPTACIÓN
TECHNICAL_RESULT=PASS sólo con 20/20 SATISFIED. Cualquier FAILED→FAIL. Cualquier NOT_VERIFIED indispensable→BLOCKED. Un rechazo esperado demostrado sí cuenta como SATISFIED. Diagnosticar una carencia no satisface el requisito. Tras PASS técnico preparar/solicitar la AcceptanceRecord M2-minimal. `GATE_STATUS=ACCEPTED` sólo cuando esa AcceptanceRecord exista, esté en estado accepted y sea vigente para las revisiones/dependencias usadas; solicitarla no equivale a obtenerla.

## FORMATO DE SALIDA DEL AGENTE
E2E_PROFILE=M2-minimal; matriz 20/20 requisito→estado/evidencia/fingerprint; fallos/provider_phase; TECHNICAL_RESULT; M2_MINIMAL_ACCEPTANCE_CANDIDATE; GATE_STATUS.
