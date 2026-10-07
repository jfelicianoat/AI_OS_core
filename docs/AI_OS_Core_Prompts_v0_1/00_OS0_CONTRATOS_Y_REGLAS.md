# Fase 00 — Congelar contratos y reglas del AI OS

## ROL

Actúa como arquitecto principal de un ecosistema multiagente local-first. Tu misión es convertir la especificación OS-0 en contratos implementables y verificables, **sin implementar todavía lógica de negocio ni modificar otros repositorios**.

## OBJETIVO REAL

Congelar los contratos interoperables que utilizarán AI OS Core y las aplicaciones existentes, evitando interpretaciones distintas entre repositorios.

## CONTEXTO

Sistemas propietarios:

- `AI_OS_Core`: Goals, Objectives, Resource Graph, Decisions, Policies globales, Capability Registry, Context Packages.
- `Gestion-tareas-IA`: Tasks, calendario, planificación humana/IA.
- `Agora_AGR`: Jobs/Cards y ejecución IA durable.
- `Athena`: Agent Runs, skills del runtime, permisos, verificación y repair.
- `AI_Broker`: modelos, inferencias, routing, capacidad de hardware/modelos.
- `Knowledge_Orchestrator`: conocimiento, claims, evidencias, vigencia.
- `Model_Drift`: certificaciones skill/model/runtime.
- `Local-AI-Lab`: experimentos/evidencia.
- `ChatyGPT`: cliente/UI.
- `YT_Capture_Plugin`: captura de YouTube.

## TAREA

Crear en el nuevo repositorio `AI_OS_Core` una carpeta `contracts/` con esquemas y documentación de:

1. `ResourceReference`
2. `Goal`
3. `Objective`
4. `CapabilityManifest`
5. `SkillManifest`
6. `ExecutionFingerprint`
7. `Certification`
8. `Event`
9. `Policy`
10. `ContextRequest`
11. `ContextPackage`
12. `Decision`
13. `Task`
14. `TaskDependency`
15. `AICapacitySnapshot`
16. `AIDurationEstimate`
17. `Job`
18. `AgentRun`
19. `Artifact`
20. `Failure`
21. `ApprovalRequest`
22. `ApprovalDecision`
23. `CommandEnvelope`

Usar versión de contrato `1.0`.

## REGLAS DE IDENTIDAD

- IDs interoperables: `<namespace>_<ULID>`.
- Toda operación distribuida: `correlation_id`.
- Eventos causados por otro evento: `causation_id`.
- Toda escritura remota: `idempotency_key`.
- Campos imposibles de verificar: `null`, nunca inferidos.

## REGLAS DE PROPIEDAD

Un sistema puede referenciar datos ajenos, pero no convertirse en propietario de ellos por duplicación.

AI OS Core nunca debe leer SQLite de otras aplicaciones.

## EVENTOS

Definir la matriz de autoridad de eventos. Como mínimo:

- AI Broker: `model.*`, `broker.capacity_changed`
- Athena: `agent.*`, `skill.updated`
- Agora: `job.*`, `artifact.created`, `worker.*`
- Gestión Tareas: `task.*`, `schedule.changed`, `human.capacity_changed`
- KO: `knowledge.*`
- Model Drift: `certification.*`
- Local AI Lab: `experiment.completed`, `evidence.available`

## VERIFICACIÓN

Crear tests de contrato que demuestren:

- campos obligatorios;
- compatibilidad aditiva;
- rechazo de enums inválidos;
- source autorizado por tipo de evento;
- `metadata` no introduce comportamiento;
- `Skill` no puede ampliar permisos;
- cambios de fingerprint invalidan aplicabilidad de certificación.

## GUARDRAILS

- No tocar repositorios externos.
- No implementar Planner.
- No implementar routing de modelos.
- No crear UI.
- No crear scheduler.
- No inventar endpoints que impliquen escrituras externas.
- No borrar ni migrar datos existentes.

## CRITERIOS DE ACEPTACIÓN

- Todos los contratos tienen schema version `1.0`.
- Existen fixtures válidos e inválidos.
- Existe una tabla de ownership.
- Existe una tabla de event authority.
- Existen tests automatizados para los contratos.
- La documentación distingue explícitamente Command vs Event.
- No existe lógica de negocio fuera de validación y serialización.
