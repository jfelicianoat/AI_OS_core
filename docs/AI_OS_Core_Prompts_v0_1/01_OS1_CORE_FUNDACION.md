# Fase 01 — AI OS Core: fundación del servicio

## ROL

Actúa como arquitecto y desarrollador backend senior. Implementa la base del nuevo servicio `AI_OS_Core` respetando estrictamente los contratos OS-0.

## OBJETIVO REAL

Construir un control plane durable, determinista y pequeño que pueda arrancar sin servicios externos.

## STACK

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLite + WAL
- `httpx`
- SQL explícito mediante capa Repository o un ORM ligero sólo si reduce complejidad sin ocultar invariantes.

## ESTRUCTURA

Crear:

```text
src/ai_os_core/
  app.py
  config.py
  bootstrap.py
  domain/
  application/
  infrastructure/
    db/
    http/
    events/
    security/
  api/
  workers/
tests/
  unit/
  integration/
  contract/
```

## MÓDULOS

Implementar sólo:

- Goals
- Objectives
- Services
- Resources/Relations
- Events
- Policies
- Decisions
- Approvals
- Context Packages básicos
- Idempotency
- Audit

## PERSISTENCIA

SQLite bajo `%LOCALAPPDATA%\AIOSCore\data\ai_os_core.db`.

Activar:
- WAL
- foreign keys
- busy timeout
- transacciones cortas
- migraciones forward-only.

Tablas mínimas:

- `schema_versions`
- `goals`
- `objectives`
- `services`
- `capabilities`
- `capability_providers`
- `skills`
- `certifications`
- `resources`
- `resource_relations`
- `policies`
- `decisions`
- `events`
- `event_processing`
- `approvals`
- `context_packages`
- `audit_log`
- `idempotency_keys`

## API MÍNIMA

Implementar:

- `GET /api/v1/health`
- Goals/Objectives CRUD lógico
- Service Registry
- Capability Registry
- Events
- Policies read/evaluate
- Decisions
- Resource Graph read
- Context resolve básico
- Approvals read/decision

No DELETE físico para entidades de negocio.

## EVENT STORE

- append-only;
- persistir antes de procesar;
- `at-least-once`;
- handlers idempotentes;
- `event_processing` separado.

## REINICIO

Al arrancar:

1. aplicar migraciones;
2. validar DB;
3. recuperar `event_processing` pendiente;
4. marcar servicios obsoletos/stale;
5. arrancar API;
6. arrancar workers.

## SEGURIDAD

- tokens fuera de SQLite en texto plano;
- secretos mediante Windows Credential Manager/DPAPI;
- logs sin prompts, documentos, credenciales o cabeceras auth.

## VERIFICACIÓN

Pruebas obligatorias:

- migraciones desde DB vacía;
- reinicio tras evento persistido pero no procesado;
- idempotencia misma key/mismo body;
- 409 misma key/body distinto;
- Resource Graph;
- Goal CRUD;
- Policy evaluator;
- audit;
- arranque con 0 dependencias externas.

## GUARDRAILS

No implementar:
- Planner LLM;
- ejecución de Jobs;
- scheduling;
- Model Drift execution;
- semantic search;
- model routing;
- acceso a bases externas.

## CRITERIOS DE ACEPTACIÓN

El Core debe poder arrancar aislado y responder correctamente a:
- servicios registrados;
- goals activos;
- capabilities registradas;
- eventos persistidos;
- policies aplicables;
- resource relations;
- context package básico.
