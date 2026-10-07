# Fase 13 — Policy Engine y autonomía condicionada

## OBJETIVO REAL

Permitir automatización progresiva sin que la autoridad dependa del LLM.

## AUTONOMY LEVELS

- A0 OBSERVE
- A1 RECOMMEND
- A2 PREPARE
- A3 EXECUTE_WITH_APPROVAL
- A4 EXECUTE_AUTOMATICALLY
- A5 EXECUTE_REPAIR_ESCALATE

## REGLA CENTRAL

Autonomía pertenece a:
`Capability + Policy + Certification + Scope`

Nunca al modelo.

## EVALUACIÓN

Orden:
1. invariantes estructurales;
2. ownership;
3. security/privacy;
4. certification;
5. resource constraints;
6. autonomy ceiling;
7. approval policy;
8. cost;
9. execution.

## ACCIONES SIEMPRE CON CONFIRMACIÓN

Como mínimo:
- borrar información;
- modificar datos críticos;
- publicar contenido;
- enviar comunicaciones;
- realizar compras;
- cambios difíciles de revertir.

## PLANNER FUTURO

LLM sólo produce `Typed Plan Proposal`.

Flujo:
LLM proposal
→ schema validation
→ policy evaluation
→ capability validation
→ certification validation
→ approval si procede
→ creación de Tasks.

Nunca:
`LLM text → execute`

## VERIFICACIÓN

- LLM no puede elevar A3 a A4;
- policy DENY gana;
- skill certificada no sustituye approval;
- acción irreversible nunca se autoejecuta por error;
- toda decisión automatizada tiene `decision_trace`.
