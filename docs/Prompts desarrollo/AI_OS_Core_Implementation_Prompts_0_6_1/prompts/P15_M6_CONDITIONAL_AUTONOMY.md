# P15 — M6: autonomía condicional

## ROL
Safety/control-plane engineer.

## OBJETIVO REAL
Permitir autonomía gradual sólo sobre gates ya validados.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
AI OS Core + executors relevantes.

## PRERREQUISITOS
M5 estable y Policy/Approval/Certification/Admission E2E.

## ENTRADAS
Spec, EffectiveExecutionDecision, Policies y evidence.

## TAREA Y CAMBIOS EXACTOS
Implementar authorization gate→certification gate→admission gate→mínimo de ceilings A0–A5. Mantener executable, blocked_reasons, constraints, obligations. Promotion explícita y medible. A5 repair con límites de intentos/coste/acciones/stop/escalation.

## NO HACER
No blocked=A0; no autoejecutar borrado/datos críticos/publicación/comunicaciones/compras/acciones irreversibles; no self-modification ilimitada.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Unknown cert, revoked approval, no admission, conflicting ceilings, repair exhaustion y hard-confirmation classes.

## PRUEBAS REALES
Canary reversible low-risk únicamente.

## EVIDENCIAS A ENTREGAR
DecisionTrace por gate y canary evidence.

## CRITERIOS DE ACEPTACIÓN
Ninguna capa eleva autonomía por encima de ceilings/policies y clases irreversibles siguen humanas.

## FORMATO DE SALIDA DEL AGENTE
Findings, policy/config, tests/canary evidence, PHASE_RESULT.
