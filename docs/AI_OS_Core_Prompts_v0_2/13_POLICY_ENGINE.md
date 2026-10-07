# Prompt 13 — OS-8 Policy Engine completo

## OBJETIVO
Implementar la semántica cerrada en 00C.

## NO MEZCLAR CON AUTONOMÍA
Esta fase implementa Policy Engine. No Planner y no promoción automática de autonomía.

## RESULTADO
PolicyDecision:
- ALLOW
- DENY
- REQUIRE_APPROVAL
- INDETERMINATE

Más:
- constraints;
- obligations;
- unknown inputs;
- evidence refs.

## CONSTRAINT MERGE
Implementar por tipo:
- max => mínimo de máximos;
- min => máximo de mínimos;
- allowed_set => intersección;
- denied_set => unión;
- boolean requirement => AND;
- incompatible => deny/indeterminate según definición.

## PRUEBAS
- approval + cost cap;
- two incompatible GPU constraints;
- missing certification;
- unknown classification;
- expired policy;
- no applicable policy default.
