# P14 — M5: Typed Planner

## ROL
Arquitecto de PlanningService.

## OBJETIVO REAL
Introducir planificación LLM tipada sin ejecución de texto libre.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
AI OS Core PlanningService, AI Broker y cliente Gestión Tareas.

## PRERREQUISITOS
M3 Context + M4 Policy + M2 estable.

## ENTRADAS
Spec, Goals, ContextPackage, Registry, Policies y Task API.

## TAREA Y CAMBIOS EXACTOS
Goal+Context→Broker inference→TypedPlanProposal→schema validation→DAG→Policy→capability/cert checks→human review→request de creación de Tasks a Gestión Tareas. Incluir Objectives, Tasks, actors, HumanWorkSegments, dependencies, capabilities, expected artifacts, acceptance criteria y assumptions. Core no crea Jobs.

## NO HACER
No saltarse Task Manager/Google Calendar; no tool execution desde texto; no auto-commit inicial.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
Invalid graph/C25, unsupported capability, unknown certification, budgets, assumptions.

## PRUEBAS REALES
Proposal-only de bajo riesgo.

## EVIDENCIAS A ENTREGAR
`TypedPlanProposal` contract/schema versionado, fixtures válidos/invalidos, proposal real, validation/DecisionTrace y revisión humana; preparar AcceptanceCandidate del contrato si cambia/se formaliza.

## CRITERIOS DE ACEPTACIÓN
El contrato TypedPlanProposal queda identificado por revisión/hash y validado por consumidores; Planner propone sin romper ownership ni ejecutar directamente.

## FORMATO DE SALIDA DEL AGENTE
Findings, implementation, examples/tests, PHASE_RESULT; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
