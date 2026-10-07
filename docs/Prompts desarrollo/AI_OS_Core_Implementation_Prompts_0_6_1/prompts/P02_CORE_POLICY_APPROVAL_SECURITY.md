# P02 — Core: Policy, Approval, seguridad, budget y cert projection

## ROL
Security/backend engineer del Core.

## OBJETIVO REAL
Cerrar el bloque M0 de seguridad/control antes de M2.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
AI_OS_Core.

## PRERREQUISITOS
P01 PASS.

## ENTRADAS
Spec, matrices P00 y Core M0.

## TAREA Y CAMBIOS EXACTOS
Implementar Policy TRUE/FALSE/UNKNOWN, all/any/unconditional; combinación por significado; default DENY; classification ceiling; PolicyDecision con constraints/obligations/unknowns; ApprovalRequest/Authorization/Use/Revocation/EffectiveState; commit atómico ApprovalUse+Command/outbox; exact_action vs scoped; AuthorizationPrincipal; BudgetReservation concurrente; almacenamiento/proyección/query de CertificationApplicability. Approval no resuelve security UNKNOWN.

## NO HACER
No Planner/autonomía/auto-certification; no relajar Athena permissions.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C06,C07,C08,C09,C18,C19,C20,C21,C22 y M0-CERT-PROJ; incluir carreras reales de approval/budget.

## PRUEBAS REALES
Smoke API local con dos principals/scopes.

## EVIDENCIAS A ENTREGAR
PolicyDecision/approval/budget/cert traces.

## CRITERIOS DE ACEPTACIÓN
M0 completo, default DENY demostrado, seguridad no depende de UI.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests, evidence, PHASE_RESULT.
