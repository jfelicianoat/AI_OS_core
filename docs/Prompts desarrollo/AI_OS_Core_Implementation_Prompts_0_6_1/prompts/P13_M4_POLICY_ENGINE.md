# P13 — M4: Policy Engine completo

## ROL
Security/rules engineer.

## OBJETIVO REAL
Expandir P02 a Policy Engine de producción sin cambiar la semántica normativa.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
AI OS Core.

## PRERREQUISITOS
M2 PASS; P02 estable.

## ENTRADAS
Spec, Policy corpus previsto y audit M2.

## TAREA Y CAMBIOS EXACTOS
Completar constraint merge por tipo, obligations, revision activation/expiry, budget/quota protocol ampliado, explainability/DecisionTrace y dry-run. Mantener default DENY y determinismo.

## NO HACER
No Planner/autonomy ni excepciones implícitas; no LLM para decidir seguridad.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C08,C09,C18,C19,C20,C21,C22 y policies conflictivas.

## PRUEBAS REALES
Dry-run sobre operaciones M2 antes de enforcement.

## EVIDENCIAS A ENTREGAR
PolicyDecision traces y corpus versionado.

## CRITERIOS DE ACEPTACIÓN
Mismos inputs producen decisión/constraints/obligations deterministas.

## FORMATO DE SALIDA DEL AGENTE
Findings, test matrix, PHASE_RESULT.
