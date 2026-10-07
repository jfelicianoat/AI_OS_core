# P10B — M2-contextual: E2E con conocimiento

## ROL
Verificador E2E del perfil contextual.

## OBJETIVO REAL
Demostrar M2-minimal + contexto reproducible de KO.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Repos M2 + Knowledge_Orchestrator.

## PRERREQUISITOS
P07 ha entregado KO→Core ContextPackage→Athena. Aplicar `E2E_ACCEPTANCE_PROTOCOL.md`. Alias `P10-contextual`. Elegir `INHERIT_MINIMAL` con AcceptanceRecord M2-minimal vigente/compatible o `FULL_22`. PASS locales P02–P08 sin evidencia E2E mínima aceptada no bastan para heredar.

## ENTRADAS
Spec y caso real que necesite knowledge/context.

## TAREA Y CAMBIOS EXACTOS
Verificar KO→ContextPackage autorizado Core→Athena→Run/Artifact, M2-CONTEXT-EVIDENCE y M2-REPLAY-KO. En INHERIT_MINIMAL validar AcceptanceRecord y compatibilidad de contratos/builds/config/model constraints; si cambia algo incompatible, revalidar o usar FULL_22. En FULL_22 verificar directamente los 22. Mantener matriz 22/22 marcando evidencia OWN o INHERITED y sus refs/fingerprints.

## NO HACER
No Planner ni semantic ranking global; no copiar vault completo.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C12,C04,C05 específicos KO/context.

## PRUEBAS REALES
Recurso controlado; cambiar fuente después y reproducir evidencia histórica.

## EVIDENCIAS A ENTREGAR
Context evidence/snapshot/hash/revision/replay trace.

## CRITERIOS DE ACEPTACIÓN
TECHNICAL_RESULT=PASS sólo con 22/22 SATISFIED por evidencia propia o herencia vigente. C12+replay KO solos no promueven el hito. Después preparar/solicitar la AcceptanceRecord M2-contextual. `GATE_STATUS=ACCEPTED` sólo cuando exista una AcceptanceRecord accepted y vigente; solicitarla no equivale a obtenerla. Cambios incompatibles en evidencia heredada obligan a revalidar.

## FORMATO DE SALIDA DEL AGENTE
E2E_PROFILE=M2-contextual; EVIDENCE_MODE=INHERIT_MINIMAL|FULL_22; matriz 22/22 OWN/INHERITED; refs de AcceptanceRecords/dependencias; TECHNICAL_RESULT; M2_CONTEXTUAL_ACCEPTANCE_CANDIDATE; GATE_STATUS.
