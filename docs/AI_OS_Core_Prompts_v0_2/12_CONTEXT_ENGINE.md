# Prompt 12 — OS-7 Context Engine reproducible y autorizado

## OBJETIVO
Construir contexto federado mínimo, reproducible y autorizado.

## AUTHORIZATION FIRST
Antes de ranking:
1. principal/scopes;
2. classification;
3. policy;
4. destination capability ceiling;
5. existence privacy.

## SOURCES
- Core: Goals, Decisions, Policies.
- Task Manager: Tasks.
- Agora: Jobs.
- Athena: Runs.
- KO: knowledge.
- artifacts por su custodian/owner.

## MATERIALIZATION
ContextPackage debe contener para cada item consumido:
- source ref;
- immutable revision o snapshot ref;
- content hash;
- retrieved_at;
- validity_at_use;
- classification;
- provenance.

`ContextPackage` es inmutable, pero no basta con referencias mutables.

## CUSTODIA
Definir quién guarda materialized fragments:
- Core si son pequeños y policy lo permite, o
- evidence store del Run/Athena,
pero siempre con retención acordada.

## RETENTION
Separar:
- package usable until;
- historical evidence retention.

## EXCLUSIONS
Dos vistas:
- consumer-safe;
- privileged audit.

## PRUEBAS
- resource changed;
- KO unavailable;
- expired source;
- sensitive ref hidden;
- reproducir contenido exacto del Run.
