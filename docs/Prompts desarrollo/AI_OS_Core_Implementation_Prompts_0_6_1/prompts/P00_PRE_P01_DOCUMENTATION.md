# P00 — Materializar puerta documental pre-P01

## ROL
Arquitecto de contratos/documentación; no escribas código de producto.

## OBJETIVO REAL
Materializar los nueve artefactos exigidos antes de P01 sin reinterpretar la arquitectura.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

## REPOSITORIOS AFECTADOS
AI_OS_Core/docs y contratos.

## PRERREQUISITOS
Spec 0.6.1 aprobada para derivación de prompts; no requiere apps funcionando.

## ENTRADAS
Spec, documentación actual y APIs públicas observadas sólo para no inventar contratos.

## TAREA Y CAMBIOS EXACTOS
Crear exactamente: Contract Inventory, Data Dictionary, State Transition Tables, Authorization Matrix, Event Authority Matrix, Persistence Mapping, Contract Schemas 0.6.1, Fixtures válidos/invalidos y Acceptance Registry bootstrap. Cubrir todos los contratos canónicos; required/null/formato/unidades; estados Goal/Objective/Approval/Task/Job/AgentRun/restore; default DENY/classification/scopes; autoridad de eventos; persistencia/proyecciones.

## NO HACER
No FastAPI, DB productiva, endpoints reales ni cambios en otros repos.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Parsear/validar schemas y fixtures; comprobar ownership, nombres canónicos y ausencia de contratos retirados.

## PRUEBAS REALES
No aplica salvo lectura no mutante de interfaces existentes.

## EVIDENCIAS A ENTREGAR
Diff documental, inventario, validación y lista de gaps.

## CRITERIOS DE ACEPTACIÓN
Los nueve artefactos existen y no dejan decisiones M0 de alta prioridad implícitas.

## FORMATO DE SALIDA DEL AGENTE
CURRENT_STATE_FINDINGS, artefactos creados, pruebas, SPEC_GAP_REPORT si aplica, PHASE_RESULT.
