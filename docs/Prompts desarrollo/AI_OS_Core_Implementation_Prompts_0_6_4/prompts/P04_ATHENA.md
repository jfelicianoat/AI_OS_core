# P04 — Athena: runtime integrado y evidencia

## ROL
Maintainer de Athena preservando PermissionEngine.

## OBJETIVO REAL
Integrar Athena sin convertirla en scheduler ni permitir elevación de permisos.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Athena.

## PRERREQUISITOS
P03 PASS.

## ENTRADAS
Spec y runtime/skills/tools/permissions actuales.

## TAREA Y CAMBIOS EXACTOS
Añadir CapabilityManifest, SkillManifest version/hash/toolsets, AgentRun/correlation, ExecutionFingerprint, model invocation refs/effective model, event outbox/replay y Artifact producer metadata. Para contexto, Athena sólo consume un `ContextPackage`/ref emitido bajo autoridad del Core, valida identidad/revisión/hash y conserva evidencia; no lo autoriza ni construye. P07 entrega el proveedor mínimo antes de M2-contextual. Para mandatory certification exigir enforcement Broker; Approval Core nunca amplía PermissionEngine.

## NO HACER
No scheduler/Goal Engine/global Policy owner/tools nuevos innecesarios.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Permissions invariants, strict model set, fallback evidence, replay, context no amplía tools, Artifact roles.

## PRUEBAS REALES
Smoke de run reversible si es posible.

## EVIDENCIAS A ENTREGAR
Run trace completo con skills/model/verification/artifacts.

## CRITERIOS DE ACEPTACIÓN
Standalone intacto; modo integrado genera evidencia M2 suficiente.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios, tests, trace; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
