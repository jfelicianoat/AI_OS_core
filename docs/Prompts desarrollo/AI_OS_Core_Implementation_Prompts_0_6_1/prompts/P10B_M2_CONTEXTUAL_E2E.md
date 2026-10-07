# P10B — M2-contextual: E2E con conocimiento

## ROL
Verificador E2E del perfil contextual.

## OBJETIVO REAL
Demostrar M2-minimal + contexto reproducible de KO.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
Repos M2 + Knowledge_Orchestrator.

## PRERREQUISITOS
P02–P08 PASS incluido P07.

## ENTRADAS
Spec y caso real que necesite knowledge/context.

## TAREA Y CAMBIOS EXACTOS
Verificar M2-CONTEXT-EVIDENCE y M2-REPLAY-KO: revision/snapshot exacto, provenance/retention, trace hasta Run/Artifact y replay KO. No crear todavía el Context Engine global.

## NO HACER
No Planner ni semantic ranking global; no copiar vault completo.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C12,C04,C05 específicos KO/context.

## PRUEBAS REALES
Recurso controlado; cambiar fuente después y reproducir evidencia histórica.

## EVIDENCIAS A ENTREGAR
Context evidence/snapshot/hash/revision/replay trace.

## CRITERIOS DE ACEPTACIÓN
Perfil contextual suma exactamente dos requisitos al minimal.

## FORMATO DE SALIDA DEL AGENTE
E2E_PROFILE M2-contextual, requirement→evidence, PHASE_RESULT.
