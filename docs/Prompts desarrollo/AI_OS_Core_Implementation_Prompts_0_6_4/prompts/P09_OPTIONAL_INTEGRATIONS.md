# P09 — Local AI Lab y YT Capture opcionales

## ROL
Integrador conservador de componentes opcionales.

## OBJETIVO REAL
Aportar evidencia/captura sin nuevas dependencias críticas.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
Local AI Lab y YT_Capture_Plugin.

## PRERREQUISITOS
Opcional después de P01 cuando el Core esté técnicamente disponible si la integración necesita publicar al Core. No existe una puerta M1 adicional; P09 no bloquea M2.

## ENTRADAS
Spec y flujos actuales.

## TAREA Y CAMBIOS EXACTOS
Local AI Lab: opcional evidence.available con refs/hashes, manteniendo Model Drift como autoridad. YT Capture: sin cambio obligatorio; mantener YouTube→Markdown→KO; capture.completed sólo con consumidor real.

## NO HACER
No Core dependency crítica ni duplicar knowledge/cert authority.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Fixture si se añade evento.

## PRUEBAS REALES
Smoke opcional.

## EVIDENCIAS A ENTREGAR
Sólo si hay cambios.

## CRITERIOS DE ACEPTACIÓN
Esta fase es opcional y no bloquea M2. Antes de ejecutar, declarar `APPLICATION_STATUS=APPLICABLE|SKIPPED`.

Si `SKIPPED`:
- no se interpreta como fallo;
- `TECHNICAL_RESULT=NOT_RUN`;
- `GATE_STATUS=NOT_REQUIRED`;
- se documenta el motivo.

Si `APPLICABLE`, se usa el protocolo normal de TECHNICAL_RESULT/GATE_STATUS.

## FORMATO DE SALIDA DEL AGENTE
`APPLICATION_STATUS=APPLICABLE|SKIPPED`; Findings; cambios/evidencia si aplica; `TECHNICAL_RESULT=PASS|FAIL|BLOCKED|NOT_RUN`; `ACCEPTANCE_CANDIDATE` si aplica; `GATE_STATUS=ACCEPTED|PENDING_ACCEPTANCE|BLOCKED|NOT_REQUIRED`.
