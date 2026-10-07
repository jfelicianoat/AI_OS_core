# Fase 02 — AI OS Core: Registry, Events, Policies y Reconciliation

## OBJETIVO REAL

Completar la parte determinista del control plane antes de conectar aplicaciones reales.

## TAREA

Implementar:

### Service Registry
Estados:
- REGISTERED
- HEALTHY
- DEGRADED
- UNREACHABLE
- STALE
- REMOVED

Heartbeat configurable, por defecto 45 s.

### Capability Registry
- múltiples providers por capability;
- `declared_status`;
- `derived_status`;
- disponibilidad efectiva:
  - AVAILABLE
  - DEGRADED
  - BLOCKED
  - UNAVAILABLE
  - UNKNOWN.

### Event Authority Matrix
Rechazar eventos publicados por un sistema que no sea propietario/autorizado.

### Policy Engine v1
Operadores:
- equals
- not_equals
- in
- not_in
- greater_than
- less_than
- contains
- exists

Precedencia:
`DENY > REQUIRE_APPROVAL > CONSTRAIN > ALLOW`

Después:
- prioridad;
- especificidad.

### Reconciliation
El propietario externo siempre gana frente a una proyección local.

### Context Engine básico
Resolver:
- Goals;
- Objectives;
- Decisions;
- Policies;
- Resources;
- referencias.

Registrar exclusiones por:
- sensibilidad;
- expiración;
- superseded;
- scope incorrecto.

## VERIFICACIÓN

Casos:
- `model.changed` desde `task_manager` debe rechazarse;
- servicio stale vuelve a healthy tras heartbeat válido;
- provider healthy + certification failed => capability BLOCKED;
- policy DENY gana frente a ALLOW;
- reconciliación actualiza proyección sin modificar servicio externo.

## GUARDRAILS

No integrar aún repos reales.
No hacer requests mutables a servicios.
No usar LLM.
