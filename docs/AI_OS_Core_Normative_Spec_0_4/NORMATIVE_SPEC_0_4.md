# AI OS Core — Normative Specification 0.4

**Estado:** `draft-reviewable`
**Naturaleza:** especificación normativa candidata, previa a implementación
**Fecha:** 2026-09-12

## 0. Fuente normativa

Este documento es la única fuente normativa de arquitectura para la versión 0.4.

Precedencia:
1. `NORMATIVE_SPEC_0_4.md`
2. contratos formales 0.4 derivados de esta especificación
3. registros de aceptación vinculados a una revisión concreta
4. OS-0, OS-1 y kits v0.1–v0.3 como históricos/referencia

Una decisión `proposed` no adquiere autoridad por su posición. Estados permitidos:
`proposed`, `approved`, `superseded`, `rejected`.

Todas las decisiones de esta entrega parten como `proposed`.

## 1. Propósito

AI OS Core es un control plane determinista y federado para:
- objetivos;
- contexto;
- capacidades;
- reglas;
- eventos;
- decisiones;
- trazabilidad;
- relaciones entre recursos.

No sustituye al propietario de cada dominio.

## 2. Ownership

| Dominio | Autoridad |
|---|---|
| Goal, Objective, Decision, Policy global | AI OS Core |
| Resource Graph, Approval*, ContextPackage | AI OS Core |
| CertificationApplicability | AI OS Core como proyección |
| Task, calendario, scheduling, HumanWorkSegment | Gestión Tareas IA |
| Job del flujo integrado, worker admission | Agora |
| AgentRun, permisos, skills, verification/repair | Athena |
| modelos, routing, inferencia, candidate enforcement | AI Broker |
| Comparability/Evaluation/Certification histórica | Model Drift |
| documentos/claims/evidencia | Knowledge Orchestrator |
| UI | ChatyGPT |

Agora sólo es autoridad de Jobs del flujo integrado; no de toda operación durable del ecosistema.

## 3. Contratos canónicos

Identidad:
`ResourceReference`, `IdentityBinding`, `ResourceRevision`, `ProducerStreamIdentity`.

Goals:
`Goal`, `Objective`.

Capabilities:
`CapabilityManifest`, `SkillManifest`, `CapabilityAvailability`.

Modelos/certificación:
`ModelIdentityEvidence`, `ExecutionFingerprint`, `ModelExecutionConstraint`,
`ModelInvocationEvidence`, `ComparabilityAssessment`, `EvaluationVerdict`,
`Certification`, `CertificationApplicability`, `CertificationRequest`.

Policies/approval:
`Policy`, `PolicyDecision`, `PolicyObligation`, `ConstraintSet`,
`ApprovalRequest`, `ApprovalAuthorization`, `ApprovalUse`,
`ApprovalRevocation`, `ApprovalEffectiveState`, `BudgetReservation`.

Eventos/comandos:
`EventEnvelope`, `CommandEnvelope`, `EventDeliveryReceipt`, `ReplayCursor`, `ReplayGap`.

Scheduling/ejecución:
`Task`, `HumanWorkSegment`, `TaskDependency`, `AICapacityForecast`,
`WorkerAdmission`, `InferenceAdmission`, `Job`, `JobDispatchRequest`,
`AgentRun`, `Artifact`, `VerificationResult`, `Failure`.

Context/plan:
`ContextRequest`, `ContextPackage`, `TypedPlanProposal`, `EffectiveExecutionDecision`.

Servicios/audit:
`ServiceRegistration`, `ServiceHealth`, `AuthorizationPrincipal`,
`DecisionTrace`, `AcceptanceRecord`.

Nombres retirados:
- `HumanInterval`, `HumanIntervalRequirement` → `HumanWorkSegment`
- `ComparabilityResult` → `ComparabilityAssessment`
- `ApprovalGrant` → `ApprovalAuthorization` + uso/revocación separados
- `AIReservation` fuera del MVP
- `ExecutionAdmission` dividido en `WorkerAdmission` y `InferenceAdmission`

## 4. Identidad y revisiones

Distinguir siempre:
`schema_version`, `resource_revision`, `service_version`, `capability_version`,
`skill_version`, `policy_revision`, `stream_epoch`, `source_sequence`,
`model_identity`, `artifact_hash`.

Los recursos nuevos del Core usan `<namespace>_<ULID>`.
Los objetos legacy conservan su identidad nativa mediante `IdentityBinding`.

## 5. Policy semantics

Cada Policy declara `condition_mode = all | any`; default `all`.

Lógica ternaria: TRUE, FALSE, UNKNOWN.

ALL:
- algún FALSE → FALSE
- sin FALSE y algún UNKNOWN → UNKNOWN
- todos TRUE → TRUE

ANY:
- algún TRUE → TRUE
- sin TRUE y algún UNKNOWN → UNKNOWN
- todos FALSE → FALSE

Una lista vacía sólo es válida si `unconditional=true`. En otro caso la Policy es inválida.

Null/missing:
- `exists(field)`: presente, incluso null → TRUE; ausente → FALSE
- `equals(field,null)`: null → TRUE; no-null → FALSE; ausente → UNKNOWN
- comparación/rango con null/ausente → UNKNOWN
- operador desconocido → Policy inválida al cargar

Sólo una revisión efectiva de una misma `(policy_key, scope)` para un instante.

`PolicyDecision` contiene:
- authorization: ALLOW | DENY | REQUIRE_APPROVAL | INDETERMINATE
- constraints
- obligations
- matched_policy_refs
- unknown_inputs

Combinación:
- allowed → AND
- forbidden → OR
- requires_* → OR
- max_* → mínimo
- min_* → máximo
- allowlist → intersección
- denylist → unión
- autonomy ceiling → mínimo sólo entre A0–A5

Precedencia de authorization:
DENY > REQUIRE_APPROVAL > INDETERMINATE > ALLOW.

Constraints y obligations no desaparecen por elegir la autorización principal.

Default DENY para mutaciones, administración, acciones externas/sensibles y lectura sin scope.
UNKNOWN de seguridad nunca produce ALLOW.

## 6. Presupuesto

Policy no reserva presupuesto. Puede emitir `budget_reservation_required`.

Para M0/M2, AI OS Core posee una autoridad presupuestaria mínima mediante `BudgetReservation`.

La reserva:
- controla saldo atómicamente;
- usa `operation_id`;
- tiene expiración y estado.

Dos operaciones concurrentes no pueden reservar el mismo saldo.

P02 entrega esta autoridad mínima. P13 puede ampliarla, no introducirla por primera vez.

## 7. Approval model

`ApprovalAuthorization` es inmutable e incluye:
- requester/approver;
- scope_mode;
- exact action digest o scope predicate;
- resources + revisions;
- capability/version;
- policy revision;
- expires_at;
- max_uses;
- risk ceiling.

`ApprovalUse` es append-only e incluye:
- authorization_id
- operation_id
- concrete_action_digest
- command_id
- used_at

UNIQUE `(authorization_id, operation_id)`.

`ApprovalRevocation` es append-only.
`ApprovalEffectiveState`: active/exhausted/expired/revoked/superseded.

### exact_action
Cambio de payload, destino, capability version, resource revision o policy relevante requiere nueva autorización.

### scoped
Cada operación concreta genera su propio ApprovalUse.

### Commit
Antes de ejecutar una acción externa:
1. validar expiración, revocación, max_uses, digest/predicate, revisions y Policy;
2. crear `ApprovalUse` + `CommandEnvelope/outbox` en la misma transacción;
3. commit.

Después del commit la operación queda autorizada. Una revocación posterior impide nuevas operaciones; cancelar una ya comprometida requiere una cancelación separada si el destino la soporta.

Retry técnico conserva `operation_id`. Mismo operation_id + digest diferente = conflict.

## 8. Eventos y replay

Cada productor:
- producer_id
- stream_id
- stream_epoch
- source_sequence

`stream_epoch` cambia ante reset/reinstall/restore que rompe continuidad.

Resource revision:
1. nativa si existe;
2. si no, `adapter_revision` durable y marcada como tal.

Representaciones:
- full_state
- delta
- audit
- notification

### Regla MVP
Sólo `full_state` actualiza la proyección canónica en M0–M2.

Los `delta`, `audit` y `notification` se almacenan/auditan pero no cambian por sí solos la proyección canónica durante el MVP.

La aplicación de deltas queda diferida y exigirá `base_revision`.

Conflictos:
- mismo event_id + digest distinto → integrity conflict
- eventos distintos misma revision → permitido
- dos full_state mismo recurso/revision con state_digest distinto → contradiction/quarantine

### Garantía del productor
Si business state y outbox comparten persistencia controlada por el productor:
- deben escribirse en la misma transacción.

Si no es posible:
- el adaptador declara `delivery_guarantee=reconciliable_state_only`;
- snapshot reconciliation recupera estado final;
- no se garantiza recuperar todos los hechos intermedios.

### Core inbox
Persistir evento + cursor/receipt, commit, luego ACK.

### Handler local
Efecto local + processed en una sola transacción.

### Gap
Si una secuencia no puede recuperarse:
- REPLAY_GAP
- suspender proyección incremental
- solicitar full_state snapshot
- establecer nuevo baseline
- continuar desde cursor confirmado

Eventos de epoch anterior después del cambio:
- audit only
- no actualizan proyección actual

## 9. Idempotencia

Namespace:
`principal_id + operation_name + idempotency_key`.

Estados:
in_progress, completed, failed_retryable, failed_terminal.

Misma key + mismo request hash → misma operación lógica.
Misma key + request hash diferente → 409.

Operación Core + registro idempotente se escriben atómicamente cuando comparten DB.

## 10. SQLite y restore

MVP:
- una única SQLite
- WAL
- synchronous=FULL
- foreign_keys=ON
- busy_timeout
- transacciones cortas

No hay perfil por tabla.

Backup: SQLite Backup API.

Restore:
- estado `reconciliation_required`;
- no reenviar efectos externos a ciegas.

Todo comando externo relevante usa `operation_id` y `command_id`.

Tras restore:
1. consultar receipt/status en receptor por operation_id;
2. si ejecutado → reconstruir estado, no reenviar;
3. si no ejecutado → reevaluar Policy y reenviar si sigue permitido;
4. si desconocido → `manual_reconciliation_required`.

M0 prueba esto con receptor simulado.
M2 lo verifica con receptores reales que soporten receipt/status.

## 11. Certificación y modelo efectivo

Separar:
1. ModelIdentityEvidence
2. ComparabilityAssessment
3. EvaluationVerdict
4. Certification histórica
5. CertificationApplicability actual

Una Certification histórica no cambia al cambiar el candidato.

P03 debe entregar antes de M2:
- allowed candidate set;
- no-fallback fuera del set cuando requirement=mandatory;
- ModelInvocationEvidence con modelo efectivo.

P11 sólo automatiza triggers.

Mandatory + certification stale/unknown/indeterminate según Policy → bloqueo.
No usar cache obsoleta como permiso sin Policy explícita.

## 12. Contexto reproducible

Cada item consumido en ContextPackage incluye:
- source ref
- immutable revision o materialized snapshot ref
- content hash
- retrieved_at
- validity_at_use
- classification
- provenance

Una referencia mutable no basta.

Distinguir:
- usable_until
- historical_evidence_retention_until

Exclusiones:
- consumer-safe
- privileged-audit

## 13. Autorización y seguridad

`classification_ceiling` solicitado no es autorización.

Techo efectivo = intersección de:
- principal;
- Policy;
- destination/capability;
- request.

Matriz obligatoria pre-P01:
`principal × operation × resource type × scope`.

ServiceRegistration usa allowlist por service identity:
- host/IP/CIDR
- puerto
- protocolo
- redirects
- timeout
- max response size

No reenviar credenciales a destino distinto.

## 14. Scheduling humano + IA

Task actor:
human, ai, hybrid, system.

`HumanWorkSegment` representa múltiples tramos humanos dentro de una Task híbrida.

Sólo esos segmentos bloquean agenda.

IA distingue:
- queue wait
- compute/service time
- wall-clock

P80/P95 = forecast, no SLA.

No hay hard reservation futura de GPU en MVP.

Gestión Tareas usa `AICapacityForecast`.

En ejecución:
- Agora produce `WorkerAdmission`;
- Broker produce `InferenceAdmission`.

`confirmed` significa que la ejecución ha sido admitida al comenzar, no que exista una reserva futura garantizada.

## 15. Task multi-Job

Aggregation policy:
- all_required
- any_success
- quorum
- ordered_pipeline

Job completed ≠ Task completed.
Task completed ≠ Objective achieved.

TaskDependency bloqueante debe ser acíclica.

## 16. Artifact

Separar:
- owner authority
- producer
- custodian/storage owner
- retention
- immutable hash/revision

## 17. Milestones

### M0 Core aislado
Entrega:
- Service/Capability registry
- Goals/Decisions/Resource Graph
- Event inbox/store/replay
- idempotencia/audit
- Approval API
- BudgetReservation mínima
- Policy base
- CertificationApplicability projection/query
- restore test con receptor simulado

### M1 Observación integrada
Apps reales publican health/capabilities/full_state/model/job/run state.
No dispatch obligatorio.

### M2 E2E manual
Requiere:
- P02 Approval + BudgetReservation + CertificationApplicability projection
- P03 Broker candidate enforcement
- P04 Athena model evidence
- P05 Agora Job API + WorkerAdmission
- P06 Task→Job bridge
- P07 context evidence mínimo si aplica
- P08 UI trace

P10 sólo verifica.

### M3
Auto-certification + Context Engine.

### M4
Policy Engine completo.

### M5
Typed Planner en `AI OS Core / PlanningService`.
Broker sólo infiere.
Gestión Tareas crea Tasks y conserva calendario.
Core no crea Jobs directamente.

### M6
Autonomía condicional.

## 18. Acceptance Registry

`AcceptanceRecord`:
- acceptance_id
- artifact_type
- artifact_id
- artifact_revision/hash
- status: pending/accepted/rejected/invalidated
- accepted_by
- accepted_at
- evidence_refs
- depends_on[]
- invalidates_if_changed[]

Cambio incompatible en dependencia invalida aceptaciones consumidoras.

Ejemplo: cambio incompatible ApprovalAuthorization invalida:
- UI ChatyGPT approval;
- reconocimiento Athena;
- tests C06/C07.

## 19. Cobertura M2

| Requisito | Owner | Contrato | Proveedor | Test |
|---|---|---|---|---|
| approvals | Core | ApprovalAuthorization/Use | P02 | C06,C07 |
| budget | Core | BudgetReservation | P02 | C09 |
| cert projection | Core+Model Drift | CertificationApplicability | P02/P03 | C11 |
| model enforcement | Broker | ModelExecutionConstraint | P03 | C10 |
| model evidence | Broker+Athena | ModelInvocationEvidence | P03/P04 | C10 |
| Job API | Agora | Job/JobDispatchRequest | P05 | C02,C13 |
| worker admission | Agora | WorkerAdmission | P05 | C13 |
| inference admission | Broker | InferenceAdmission | P03 | C10 |
| Task→Job | Gestión Tareas | JobDispatchRequest | P06 | C01,C13 |
| aggregation | Gestión Tareas | Task policy | P06 | C13 |
| human segments | Gestión Tareas | HumanWorkSegment | P06 | C14 |
| context evidence | KO/Athena/Core | ContextPackage | P07/P04 | C12 |
| UI trace | ChatyGPT | DecisionTrace | P08 | UI-M2 |
| replay | cada productor | EventEnvelope/ReplayCursor | P03–P07 | C04,C05 |
| restore receipt | Core+receptor | CommandEnvelope/EventDeliveryReceipt | P01 fake, P10 real | C15 |

## 20. Casos críticos

C01 duplicate concurrent:
misma key/request → una operación; misma key/body distinto → 409.

C02 late full_state:
completed rev8 + started rev7 → rev8 permanece.

C03 same revision:
dos full_state mismo revision con state_digest distinto → quarantine.
audit/notification misma revision → permitido.

C04 Core offline:
transactional outbox → replay completo dentro de retención.
reconciliable_state_only → recuperar estado final, no prometer hechos intermedios.

C05 replay gap:
REPLAY_GAP → freeze incremental → snapshot/reconcile.

C06 approval expiry:
expira antes de commit ApprovalUse+Command → no uso ni comando.

C07 approval concurrency:
un uso restante + dos operations → sólo una commit.
mismo operation_id con digest distinto → conflict.

C08 policy obligation:
requires_approval true + false → obligación permanece.

C09 budget:
dos reservas 80 con saldo100 → sólo una reserva completa.

C10 model fallback:
allowed {A,B}, intento C → ejecución C no válida.

C11 identity enrichment:
unavailable→verified → recalcular comparability, no declarar automáticamente model change.

C12 context historical:
KO cambia fuente → Run antiguo conserva evidencia exacta.

C13 multi-job:
all_required con un fail → Task no completed.

C14 hybrid:
5m inicio + IA + 15m review → agenda bloquea sólo 20m humanos.

C15 restore:
si receptor confirma operation ejecutada → no reenviar.
si no puede determinarlo → manual_reconciliation_required.

## 21. Puerta pre-P01

Debe existir y estar aceptado:
1. Contract Inventory
2. Data Dictionary
3. State Transition Tables
4. Authorization Matrix
5. Event Authority Matrix
6. Persistence Mapping
7. Contract Schemas 0.4
8. Fixtures
9. Acceptance Registry inicial

AI Broker real debe estar identificado antes de P03; no bloquea P01.

## 22. Regla para futuros prompts

No generar prompts de implementación si el verificador detecta:
- contrato usado no registrado;
- milestone requirement sin owner/provider/test;
- fase desconocida/circular;
- conflicto de precedencia;
- decisión requerida no approved;
- acceptance invalidada.

## 23. Cierre 0.4

Promover de `draft-reviewable` a `approved` sólo cuando:
- verifier sin errores;
- decisiones obligatorias approved;
- contratos registrados;
- cobertura M0/M2 completa;
- C01–C15 inequívocos;
- revisión humana aprobada.

Hasta entonces no derivar nuevos prompts.
