# P08 — ChatyGPT: UI del AI OS

## ROL
Maintainer ChatyGPT/UI segura.

## OBJETIVO REAL
Exponer Goals/approvals/trazabilidad sin trasladar seguridad al cliente.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
ChatyGPT.

## PRERREQUISITOS
P02 PASS; traces P01; integración completa ideal con P03–P06.

## ENTRADAS
Spec, APIs Core y UI/state actual.

## TAREA Y CAMBIOS EXACTOS
Cliente tipado para Goals/Objectives/Decisions; Approval Inbox exact/scoped con expiry/freshness; Goal→Task→Job→Run→Artifact; owner vs projection; effective model/cert applicability; consumer-safe context exclusions; degradación Core sin romper chat normal. Toda autorización se valida en servidor.

## NO HACER
No Policies locales, Jobs directos, calendario ni filtrado sensible sólo en UI.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
UI-M2, approval expirado, stale projection, exclusion privacy.

## PRUEBAS REALES
Desktop smoke con Core real si posible.

## EVIDENCIAS A ENTREGAR
UI tests/screenshots + API traces.

## CRITERIOS DE ACEPTACIÓN
Usuario comprende trace/aprobación sin que UI sea security boundary.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests/evidence; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
