# P15 — M6: autonomía condicional

## ROL
Safety/control-plane engineer.

## OBJETIVO REAL
Permitir autonomía gradual sólo sobre gates ya validados.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
AI OS Core + executors relevantes.

## PRERREQUISITOS
M5 estable/aceptado; Policy/Approval/Certification/Admission E2E; y `AutonomyPolicyDefinition` versionada con AcceptanceRecord vigente conforme a `AUTONOMY_POLICY_GATE.md`. Sin esa policy: BLOCKED, no inventar A1–A5/promoción/repair.

## ENTRADAS
Spec, EffectiveExecutionDecision, evidence y la AutonomyPolicyDefinition aceptada: semántica A0–A5, acciones, promoción/degradación, métricas/umbrales, hard-confirmation classes y límites repair/escalado.

## TAREA Y CAMBIOS EXACTOS
Implementar exactamente la AutonomyPolicyDefinition aceptada. Mantener authorization→certification→admission→mínimo de ceilings A0–A5; executable/blocked_reasons/constraints/obligations. Promotion/degradation, métricas y thresholds se leen de la policy; no se inventan. A5 repair usa sus límites explícitos y cada DecisionTrace registra la versión de policy.

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
Findings, policy/config, tests/canary evidence,; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
