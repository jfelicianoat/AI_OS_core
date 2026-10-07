# Prompt 00C — Semántica de Policies, Approvals y autorización

## FASE ARQUITECTÓNICA
OS-0.

## PRERREQUISITOS
00B aprobado.

## OBJETIVO REAL
Conseguir que dos implementaciones distintas tomen la misma decisión con los mismos datos.

## POLICY SEMANTICS

### Lógica
Usar tres estados en evaluación de condición:
- TRUE
- FALSE
- UNKNOWN

Definir por operador qué ocurre con campo ausente y `null`.

### Resultado de Policy
No devolver sólo un `effect`. Producir:
- `decision`: ALLOW / DENY / REQUIRE_APPROVAL / INDETERMINATE
- `constraints`: conjunto acumulado
- `obligations`: acciones obligatorias
- `matched_policy_refs`
- `unknown_inputs`

### Combinación
- DENY siempre bloquea.
- REQUIRE_APPROVAL añade obligación de aprobación; **no elimina constraints**.
- CONSTRAIN se acumula/intersecta.
- restricciones incompatibles => DENY/INDETERMINATE según causa, nunca “ganador por prioridad”.
- sin policies aplicables: definir default explícito por operación.
- UNKNOWN en controles de seguridad/autorización no puede convertirse implícitamente en ALLOW.

Crear ejemplos de:
- límite de gasto + aprobación;
- límites de recursos incompatibles;
- certification DEGRADED permitido bajo restricciones;
- dato de seguridad desconocido.

## APPROVAL

`ApprovalRequest` debe quedar ligado a:
- principal solicitante;
- principal(es)/rol(es) autorizados para aprobar;
- `action_type`;
- payload canónico o `action_digest`;
- recursos y `resource_revision`;
- capability/version;
- policy/version;
- scope;
- created/expires;
- consumo `single_use` o scope temporal explícito.

`ApprovalGrant` debe:
- ser inmutable;
- registrar quién aprobó;
- vincularse al digest exacto;
- declarar `consumed_at` cuando sea single-use;
- invalidarse si cambia acción/recurso/policy relevante;
- resolver carrera aprobación-expiración transaccionalmente.

`approve_scope` requiere límites:
- capability;
- resource scope;
- duration;
- max uses;
- risk ceiling.

## ATHENA
Documentar relación entre approvals del Core y permisos locales de Athena:
- el Core no amplía permisos de Athena;
- una aprobación del Core sólo sirve si Athena reconoce el grant y su propia Policy/PermissionEngine también permite la acción;
- si no hay protocolo de confianza implementado, son aprobaciones separadas.

## AUTHORIZATION
Crear matriz `principal × operation × resource type × scope`.
El `classification_ceiling` pedido por cliente no es autorización.
Techo efectivo = intersección de:
- identidad;
- policy;
- destino;
- petición.

## PRIVACIDAD DE EXCLUSIONES
El consumidor puede recibir razones genéricas.
La referencia exacta de un recurso excluido sólo aparece si tiene permiso para conocer su existencia; auditoría privilegiada puede conservar más detalle.

## CRITERIOS DE ACEPTACIÓN
Probar documentalmente:
- aprobación expirada;
- acción cambia después de aprobar;
- replay de misma acción;
- principal no autorizado;
- approve_scope excesivo;
- REQUIRE_APPROVAL + CONSTRAIN.
