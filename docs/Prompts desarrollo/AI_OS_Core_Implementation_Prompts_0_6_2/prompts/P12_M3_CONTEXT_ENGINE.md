# P12 — M3: Context Engine federado

## ROL
Arquitecto de contexto/privacidad.

## OBJETIVO REAL
Construir ContextPackage federado, reproducible y autorizado.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
AI OS Core + read APIs KO/Tasks/Agora/Athena.

## PRERREQUISITOS
M2-contextual/P07 y Authorization Matrix vigente.

## ENTRADAS
Spec, evidence APIs, ResourceReferences.

## TAREA Y CAMBIOS EXACTOS
Resolver ContextRequest con orden: principal/scopes→Policy/classification→scope→fetch federado→freshness/validity→ranking/limit→materialización/revision evidence→consumer-safe/audit exclusions. Persistir retrieved_at, validity_at_use, usable_until, historical retention.

## NO HACER
No memoria completa, LLM para seguridad ni refs mutables sin evidencia.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C12 + leakage, KO unavailable, expired source, token limits.

## PRUEBAS REALES
Smoke con contexto controlado.

## EVIDENCIAS A ENTREGAR
ContextPackage sample + reproduction report.

## CRITERIOS DE ACEPTACIÓN
Package histórico se reproduce después de cambios de fuentes.

## FORMATO DE SALIDA DEL AGENTE
Findings, tests/evidence, PHASE_RESULT; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
