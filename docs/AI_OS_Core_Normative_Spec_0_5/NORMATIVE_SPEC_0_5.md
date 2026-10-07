# AI OS Core — Normative Specification 0.5


**Estado:** `draft-reviewable`  
**Naturaleza:** especificación normativa candidata, previa a implementación  
**Fecha:** 2026-09-12

# 0. Fuente normativa y estados de cierre

Este documento es la única fuente normativa de arquitectura para la versión 0.5.

Precedencia única:
1. `NORMATIVE_SPEC_0_5.md`
2. contratos formales 0.5 derivados de esta especificación
3. `AcceptanceRecord` aceptados y ligados a una revisión exacta
4. OS-0, OS-1 y paquetes v0.1–v0.4 como históricos/referencia

Una decisión sólo tiene autoridad si su estado es `approved` y existe un `AcceptanceRecord` vigente que identifica decisión, revisión/hash, persona que acepta, fecha y evidencia.

Estados: `proposed`, `approved`, `superseded`, `rejected`.

Esta entrega mantiene todas las decisiones obligatorias como `proposed`.

## 0.1 Tres resultados distintos

- `CANDIDATE_CONSISTENT`: la candidata es internamente coherente.
- `SPEC_APPROVED`: además, todas las decisiones obligatorias tienen aceptación humana válida para esta revisión.
- `PRE_P01_READY`: además, los artefactos documentales de la puerta pre-P01 existen y están aceptados.

Ningún resultado implica software implementado o integrado.

# 1. Propósito y ownership

AI OS Core es un control plane determinista y federado para objetivos, contexto, capacidades, Policies, eventos, decisiones, trazabilidad y relaciones.

| Dominio | Autoridad |
|---|---|
| Goal, Objective, Decision, Policy global | AI OS Core |
| Resource Graph, Approval*, ContextPackage | AI OS Core |
| CertificationApplicability | AI OS Core como proyección |
| Task, calendario, scheduling, HumanWorkSegment | Gestión Tareas IA |
| Job integrado, WorkerAdmission | Agora |
| AgentRun, permisos, skills, verification/repair | Athena |
| Model routing/inference, InferenceAdmission | AI Broker |
| Comparability/Evaluation/Certification histórica | Model Drift |
| Knowledge/evidence | Knowledge Orchestrator |
| UI | ChatyGPT |

# 2. Contratos canónicos

Identidad: `ResourceReference`, `IdentityBinding`, `ResourceRevision`, `ProducerStreamIdentity`.

Goals: `Goal`, `Objective`.

Capabilities: `CapabilityManifest`, `SkillManifest`, `CapabilityAvailability`.

Modelo/certificación: `ModelIdentityEvidence`, `ExecutionFingerprint`, `ModelExecutionConstraint`, `ModelInvocationEvidence`, `ComparabilityAssessment`, `EvaluationVerdict`, `Certification`, `CertificationApplicability`, `CertificationRequest`.

Policy/approval: `Policy`, `PolicyDecision`, `PolicyObligation`, `ConstraintSet`, `ApprovalRequest`, `ApprovalAuthorization`, `ApprovalUse`, `ApprovalRevocation`, `ApprovalEffectiveState`, `BudgetReservation`.

Eventos/restore: `EventEnvelope`, `CommandEnvelope`, `EventDeliveryReceipt`, `ReplayCursor`, `ReplayGap`, `OperationStatusQuery`, `OperationExecutionStatus`, `OperationReceipt`.

Scheduling/ejecución: `Task`, `HumanWorkSegment`, `TaskDependency`, `AICapacityForecast`, `WorkerAdmission`, `InferenceAdmission`, `Job`, `JobDispatchRequest`, `AgentRun`, `Artifact`, `VerificationResult`, `Failure`.

Context/Planner/autonomía: `ContextRequest`, `ContextPackage`, `TypedPlanProposal`, `EffectiveExecutionDecision`.

Servicios/audit: `ServiceRegistration`, `ServiceHealth`, `AuthorizationPrincipal`, `DecisionTrace`, `AcceptanceRecord`.

Nombres retirados: `HumanInterval`, `HumanIntervalRequirement`, `ComparabilityResult`, `ApprovalGrant`, `AIReservation`, `ExecutionAdmission`.

# 3. Policy semantics

Cada Policy declara `condition_mode = all | any`, por defecto `all`.

Lógica ternaria TRUE/FALSE/UNKNOWN.

ALL: algún FALSE→FALSE; sin FALSE y algún UNKNOWN→UNKNOWN; todos TRUE→TRUE.

ANY: algún TRUE→TRUE; sin TRUE y algún UNKNOWN→UNKNOWN; todos FALSE→FALSE.

## 3.1 Policy incondicional

`conditions=[]` sólo es válido con `unconditional=true`. En ese caso el resultado es TRUE independientemente de `condition_mode`.

`unconditional=true` con condiciones no vacías es inválido.

## 3.2 Missing/null

- `exists(field)`: presente incluso null→TRUE; ausente→FALSE.
- `equals(field,null)`: presente null→TRUE; presente no-null→FALSE; ausente→UNKNOWN.
- comparación/rango con null/ausente→UNKNOWN.
- operador no soportado→Policy inválida.

## 3.3 Revisión y resultado

Para `(policy_key, scope)` sólo puede existir una revisión efectiva por instante. Policies disabled/expiradas no aplican.

`PolicyDecision` contiene `authorization`, `constraints`, `obligations`, `matched_policy_refs`, `unknown_inputs`.

Precedencia: DENY > REQUIRE_APPROVAL > INDETERMINATE > ALLOW.

Constraints y obligations se conservan.

## 3.4 Combinación por significado

- allowed→AND
- forbidden→OR
- requires_*→OR
- max_*→mínimo
- min_*→máximo
- allowlist→intersección
- denylist→unión
- autonomy ceiling→mínimo sólo A0–A5

Restricción incompatible conocida, p.ej. min100/max80→DENY. Si depende de UNKNOWN→INDETERMINATE.

Obtener Approval no resuelve un UNKNOWN de seguridad. Si sigue siendo bloqueante: `executable=false`, no se compromete ApprovalUse+Command.

# 4. Presupuesto

Policy puede emitir `budget_reservation_required`.

P02 entrega una autoridad mínima en AI OS Core mediante `BudgetReservation`.

Estados: `reserved`, `consumed`, `released`, `expired`.

Antes de iniciar un efecto, una reserva debe convertirse en consumed o renovarse/arrendarse según dominio; no expira silenciosamente durante una operación ya iniciada.

Dos operaciones concurrentes no pueden reservar el mismo saldo.

# 5. Approval model

`ApprovalAuthorization` es inmutable.

`ApprovalUse` + `CommandEnvelope/outbox` se crean en la misma transacción.

Antes del commit se valida:
- expiry;
- revocation;
- max_uses;
- digest o scope predicate;
- resource revisions;
- capability/version;
- policy revision;
- cualquier condición de seguridad obligatoria.

Dos operaciones concurrentes por el último uso:
- sólo una puede hacer commit.

Mismo `operation_id` con digest distinto:
- conflict.

Después del commit la operación queda autorizada. Una revocación posterior impide nuevas operaciones; cancelar una ya comprometida requiere comando separado si el receptor lo soporta.

`ApprovalUse` demuestra autorización comprometida, no ejecución.

# 6. Eventos y guarantees

Cada stream declara:
- producer_id
- stream_id
- stream_epoch
- source_sequence

Un nuevo epoch requiere productor autenticado, razón y full_state baseline o reconciliación explícita.

## 6.1 Representación MVP

Sólo `full_state` modifica proyección canónica en M0–M2.

`delta`, `audit`, `notification` se conservan, pero no actualizan la proyección canónica en el MVP.

La aplicación de delta se difiere.

## 6.2 Outbox

### `transactional_outbox`
Si cambio de negocio y outbox comparten persistencia controlada:
- ambos se escriben en la misma transacción.

### `reconciliable_state_only`
Si no puede garantizarse atomicidad:
- el productor/adaptador lo declara;
- debe ofrecer full_state snapshot/reconciliation;
- se garantiza recuperar estado final, no todos los hechos intermedios.

## 6.3 Core inbox

Core persiste evento + cursor/receipt, commit y después ACK.

Handler local:
- efecto local + processed en una transacción.

Efecto externo:
- command outbox;
- no HTTP dentro de transacción DB.

## 6.4 Replay gap

Si la secuencia no puede recuperarse:
- REPLAY_GAP
- congelar proyección incremental
- pedir snapshot
- establecer baseline
- reanudar

Eventos de epoch anterior después del cambio:
- audit only.

# 7. Restore: estado de operación

`EventDeliveryReceipt` confirma recepción/persistencia de evento. No prueba ejecución de comando.

Para restore:

## `OperationStatusQuery`
Consulta por `operation_id`.

## `OperationExecutionStatus`
Estados:
- `not_seen`
- `accepted`
- `in_progress`
- `succeeded`
- `failed_terminal`
- `cancelled`
- `unknown`

## `OperationReceipt`
Evidencia durable del resultado cuando el receptor la conserva.

Reglas:

### succeeded
Reconstruir estado. No reenviar.

### accepted / in_progress
Continuar seguimiento. No reenviar automáticamente.

### not_seen
Puede reenviarse con el mismo `operation_id` sólo después de revalidar Policy/Approval si corresponde.

### failed_terminal / cancelled
No reenviar automáticamente sin nueva decisión/operación.

### unknown
`manual_reconciliation_required`.

Cada receptor declara:
- horizonte de deduplicación por operation_id;
- horizonte de retención de status/receipts.

Si el horizonte ha expirado:
- status = unknown.

# 8. Idempotencia

Namespace:
`principal + operation_name + idempotency_key`.

Estados:
- in_progress
- completed
- failed_retryable
- failed_terminal

Misma key + mismo request hash:
- misma operación.

Misma key + body/hash distinto:
- 409.

# 9. SQLite

MVP:
- una SQLite
- WAL
- synchronous=FULL
- foreign_keys=ON
- busy_timeout
- transacciones cortas

Backup: SQLite Backup API.

Restore:
- `reconciliation_required`.

# 10. Certificación

Separar:
1. ModelIdentityEvidence
2. ComparabilityAssessment
3. EvaluationVerdict
4. Certification histórica
5. CertificationApplicability

P02 entrega:
- almacenamiento/proyección/query local de `CertificationApplicability`.

P03 entrega:
- integración con Model Drift;
- actualización de proyección;
- candidate-set enforcement;
- ModelInvocationEvidence;
- InferenceAdmission.

Mandatory certification:
- applicable/certified → puede continuar;
- degraded → Policy explícita;
- stale/not_applicable/indeterminate/unknown → bloqueo salvo Policy explícita que permita ese estado concreto.

# 11. Contexto

Cada item consumido incluye:
- source ref
- immutable revision o materialized snapshot
- content hash
- provenance
- validity
- classification

Una referencia mutable no basta.

M2 define dos perfiles:

## M2-minimal
No requiere contexto federado de KO.
P07 no es dependencia obligatoria.

## M2-contextual
Añade evidencia KO/contexto.
Requiere P07.

P10 debe declarar qué perfil verifica.

# 12. Scheduling

`HumanWorkSegment` bloquea agenda humana.

No hay hard GPU reservation futura en MVP.

`AICapacityForecast` es forecast.

En ejecución:
- Agora produce `WorkerAdmission`;
- Broker produce `InferenceAdmission`.

`confirmed` significa admisión al inicio, no reserva futura garantizada.

# 13. Autonomía — mínimo normativo

Orden obligatorio:

1. authorization gate
2. certification gate
3. admission gate
4. autonomy ceiling

`EffectiveExecutionDecision`:
- executable: bool
- blocked_reasons[]
- autonomy_ceiling: A0..A5 | null
- constraints
- obligations

Si falla authorization/certification/admission:
- executable=false
- blocked_reasons conserva el motivo
- autonomy_ceiling puede ser null
- no se representa como A0

A0 significa sólo “observe”.

El mínimo se calcula únicamente entre ceilings A0–A5:
- capability ceiling
- project/user policy ceiling
- deployment ceiling

# 14. M0 y M2 — cobertura normativa

## 14.1 M0 requisitos obligatorios

- M0-REGISTRY
- M0-GOALS
- M0-RESOURCE-GRAPH
- M0-IDEMPOTENCY
- M0-AUDIT
- M0-POLICY-BASE
- M0-APPROVAL
- M0-BUDGET
- M0-CERT-PROJECTION
- M0-EVENTS
- M0-RESTORE-FAKE

## 14.2 M2-minimal

- M2-APPROVAL
- M2-BUDGET
- M2-CERT
- M2-MODEL-ENFORCEMENT
- M2-MODEL-EVIDENCE
- M2-INFERENCE-ADMISSION
- M2-JOB
- M2-WORKER-ADMISSION
- M2-TASKJOB
- M2-AGGREGATION
- M2-HUMAN-SEGMENTS
- M2-TRACE
- M2-REPLAY-EACH-PRODUCER
- M2-RESTORE-EACH-RECEIVER

## 14.3 M2-contextual

Todos los de M2-minimal +
- M2-CONTEXT-EVIDENCE

## 14.4 Provider vs verifier

Cada Requirement declara:
- owner(s)
- provider_phase(s)
- verifier_phase(s)
- contracts
- tests

P10 es verifier de M2, nunca provider de una función necesaria para M2.

# 15. Acceptance Registry

`AcceptanceRecord` obligatorio para decisiones, contratos, hitos y artefactos pre-P01.

Campos:
- acceptance_id
- artifact_type
- artifact_id
- artifact_revision
- artifact_hash
- status
- accepted_by
- accepted_at
- evidence_refs
- depends_on[]
- invalidates_if_changed[]

Estados:
- pending
- accepted
- rejected
- invalidated

Un cambio incompatible invalida aceptaciones consumidoras.

# 16. Puerta pre-P01

Deben existir y tener AcceptanceRecord `accepted` para esta revisión:

1. Contract Inventory
2. Data Dictionary
3. State Transition Tables
4. Authorization Matrix
5. Event Authority Matrix
6. Persistence Mapping
7. Contract Schemas 0.5
8. Fixtures
9. Acceptance Registry bootstrap

`SPEC_APPROVED` y `PRE_P01_READY` son resultados separados.

# 17. Casos de aceptación

## C01 duplicate concurrent
Misma key/request → una operación.
Misma key/body distinto → 409.

## C02 late full_state
completed rev8 seguido de started rev7 → rev8 permanece.

## C03 same revision
dos full_state misma revisión con state_digest distinto → quarantine.
audit/notification misma revisión → permitido.

## C04 offline/replay
transactional_outbox recupera eventos dentro de retención.

## C05 replay gap
gap no recuperable → freeze + snapshot baseline.

## C06 approval expiry
expira antes de ApprovalUse+Command commit → no operación.

## C07 approval concurrency
último uso + dos operaciones → una commit.
mismo operation_id con digest distinto → conflict.

## C08 policy obligation
requires_approval true + false → obligación permanece.

## C09 budget
dos reservas 80 sobre saldo 100 → sólo una.

## C10 candidate enforcement
allowed {A,B}; C no debe ser invocado como fallback válido.
La evidencia debe mostrar el modelo efectivo.

## C11 certification applicability
mandatory + applicability stale/not_applicable/indeterminate → ejecución bloqueada según Policy definida.

## C12 historical context
fuente cambia → evidencia histórica exacta permanece.

## C13 multi-job
all_required con un fail → Task no completed.

## C14 hybrid
5m inicio + IA +15m revisión → 20m humanos bloqueados.

## C15 restore
- succeeded → no resend
- accepted/in_progress → follow, no resend
- not_seen → retry sólo bajo reglas
- unknown/receipt expirado → manual reconciliation

## C16 worker admission
sin worker/capacidad compatible:
- WorkerAdmission denied/waiting
- Job no entra en running
- dos admisiones exclusivas no consumen simultáneamente el mismo recurso

## C17 inference admission
sin capacidad/modelo permitido:
- InferenceAdmission denied/waiting
- no se ejecuta inferencia fuera de constraint

## C18 policy unconditional
conditions=[] + unconditional=true → TRUE con any/all.
unconditional=true + conditions no vacías → inválida.

## C19 impossible constraints
min100/max80 conocidos → DENY.
si depende de UNKNOWN → INDETERMINATE.

## C20 approval + security unknown
approval satisfecha pero security UNKNOWN bloqueante → executable=false.

## M0-REG
Registrar servicio y capability:
- identidad válida
- owner correcto
- no duplicación ilegítima
- lectura conserva revisión/estado

## UI-M2
ChatyGPT muestra:
- Goal→Task→Job→Run→Artifact
- owner state vs projection
- freshness
- effective model
- approval status
sin revelar recurso excluido no autorizado.

# 18. Verificador — alcance normativo

El verificador debe leer:
- `spec_registry.json`
- `acceptance_registry.json`
- `test_catalog.json`
- `manifest.json`

## 18.1 Candidata coherente
Comprobar:
- source_of_truth exacta
- precedencia exacta
- contratos obligatorios
- decisiones obligatorias presentes
- requirements obligatorios por milestone/profile
- owners/providers/verifiers
- tests conocidos
- dependencias sin ciclos
- artefactos pre-P01 por identidad y sin duplicados

## 18.2 SPEC_APPROVED
Además:
- todas las decisiones obligatorias = approved
- AcceptanceRecord accepted para revisión/hash correctos
- accepted_by/accepted_at/evidence_refs no vacíos
- no acceptance invalidada

## 18.3 PRE_P01_READY
Además:
- nueve artefactos pre-P01 registrados
- cada uno con revisión/hash
- AcceptanceRecord accepted vigente

El verificador nunca afirma implementación real.

# 19. Regla para futuros prompts

No derivar prompts si:
- CandidateConsistency=false
- SpecApproved=false

P01 además requiere:
- PreP01Ready=true

P03 además requiere:
- repo servidor AI Broker identificado y aceptado en inventario.

# 20. Cierre

La Spec puede recibir dictamen documental positivo cuando:
- verifier detecta cero inconsistencias
- registry reproduce fielmente M0/M2
- test catalog cubre realmente cada Requirement
- decisiones están suficientemente definidas para aprobación

La aprobación humana se registra aparte.
La puerta P01 se evalúa aparte.
