# Decisión candidata — Policy semantics
Estado: proposed

## Condiciones
Cada Policy declara `condition_mode`: `all` (default) o `any`.
Lista vacía = TRUE.

## Lógica ternaria
TRUE / FALSE / UNKNOWN.

ALL:
- algún FALSE => FALSE
- sin FALSE y algún UNKNOWN => UNKNOWN
- todos TRUE => TRUE

ANY:
- algún TRUE => TRUE
- sin TRUE y algún UNKNOWN => UNKNOWN
- todos FALSE => FALSE

## Missing/null
- exists(field): presente incluso null => TRUE; ausente => FALSE
- equals(field,null): presente null => TRUE; presente no-null => FALSE; ausente => UNKNOWN
- orden/rango sobre null o ausente => UNKNOWN
- operador desconocido => Policy inválida al cargar

## Resultado
PolicyDecision:
- authorization: ALLOW | DENY | REQUIRE_APPROVAL | INDETERMINATE
- constraints
- obligations
- matched_policy_refs
- unknown_inputs

## Combinación por significado
- permission `allowed` => AND/intersección
- prohibition `forbidden` => OR/unión
- obligation `requires_*` => OR; una obligación activa no se pierde
- max_* => mínimo de máximos
- min_* => máximo de mínimos
- allowlist => intersección
- denylist => unión
- autonomy ceiling => mínimo sólo entre A0–A5

Restricciones incompatibles => DENY si incompatibilidad cierta; INDETERMINATE si depende de UNKNOWN.

## Defaults
Mutaciones, admin, acciones externas/sensibles y lectura de recursos: default DENY salvo permiso explícito.
UNKNOWN en seguridad nunca => ALLOW.

## Presupuesto concurrente
Policy sólo emite obligación `budget_reservation_required`.
La autoridad del presupuesto reserva atómicamente antes del efecto.
