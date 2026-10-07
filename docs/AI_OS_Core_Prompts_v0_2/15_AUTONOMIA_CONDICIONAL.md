# Prompt 15 — OS-10 Autonomía condicional

## PRERREQUISITOS
Planner tipado validado, Policy Engine estable, approvals exactas, certification gate end-to-end.

## AUTONOMY LEVELS
A0 Observe
A1 Recommend
A2 Prepare
A3 Execute with approval
A4 Execute automatically
A5 Execute/repair/escalate

## REGLA
Nivel efectivo = mínimo de:
- capability ceiling;
- policy;
- certification/applicability;
- principal/deployment scope;
- current risk/resource constraints.

El LLM nunca lo aumenta.

## PROMOCIÓN
No implementar “aprendizaje mágico”.
Toda promoción requiere policy/config explícita y evidencia medible:
- success count;
- verification pass rate;
- recency;
- no blocking incidents.

## SIEMPRE CONFIRMACIÓN
Como mínimo:
- borrado;
- modificación de datos críticos;
- publicación;
- comunicaciones externas;
- compras/pagos;
- acciones difícilmente reversibles.

## A5
Repair está acotado:
- max attempts;
- max cost;
- allowed actions;
- stop conditions;
- escalation.

## PRUEBAS
- model upgrade no hereda A4 si certification unknown;
- approval no borra cost constraint;
- irreversible action stays human-confirmed;
- revoked policy stops future actions.
