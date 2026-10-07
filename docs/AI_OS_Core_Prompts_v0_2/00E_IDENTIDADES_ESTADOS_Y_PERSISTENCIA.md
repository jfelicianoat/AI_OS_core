# Prompt 00E — Identidades nativas/globales, estados y persistencia

## FASE ARQUITECTÓNICA
OS-0.

## OBJETIVO REAL
Evitar migraciones peligrosas y estados inconsistentes.

## IDENTIDADES
No imponer ULID sobre objetos legacy.
Definir `IdentityBinding`:
- `global_id` (AI OS);
- `owner_system`;
- `owner_instance`;
- `native_type`;
- `native_id`;
- `native_revision`;
- `first_seen`;
- `last_seen`;
- estado binding.

Para Agora:
- conservar filename/card identity nativa;
- `external_reference` no se asume única;
- no renombrar Cards;
- el adaptador mantiene binding durable.

## ESTADOS
Crear tablas de transición para:
- Goal;
- Objective;
- Task;
- Job;
- AgentRun;
- Approval;
- Certification applicability;
- Service registration.

Definir:
- precondiciones;
- terminales;
- cancelación concurrente;
- resume/recovery;
- optimistic concurrency mediante `expected_revision`.

## TASK CON VARIOS JOBS
Definir política explícita:
- all_required;
- any_success;
- quorum;
- ordered pipeline;
como atributo de Task/plan, no inferido.

Un Job completed no implica automáticamente Task completed.
Task completed no implica automáticamente Objective achieved.
Goal progress sólo cambia por regla/criterio explícito.

## CICLOS
TaskDependency graph debe rechazar ciclos salvo tipos expresamente no bloqueantes (si existieran).

## PERSISTENCIA
Crear matriz:
`campo contractual → tabla/proyección → productor → lector → retention`.

Incluir:
- Goal success criteria;
- constraints;
- project refs;
- autonomy policy;
- Objective dependencies;
- Capability manifest completo;
- Skill/Certification provenance;
- pagination/order stable para list endpoints.

## CRITERIOS DE ACEPTACIÓN
Round-trip sin pérdida para todos los contratos persistidos.
No hay campos normativos “sin casa”.
