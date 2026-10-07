# AI OS Core — OS-1 Diseño Interno del Servicio v0.1

**Estado:** diseño previo a implementación  
**Dependencia:** OS-0 Contratos Maestros v0.1  
**Objetivo:** definir cómo debe organizarse internamente el pequeño servicio AI OS Core sin modificar aún las aplicaciones existentes.

---

# 1. Objetivo de OS-1

OS-1 debe responder:

```text
¿Qué componentes internos necesita AI OS Core?
¿Cómo se almacenan sus datos?
¿Cómo entran y salen eventos?
¿Cómo registra servicios y capabilities?
¿Cómo mantiene Goals, Policies y State?
¿Cómo evita duplicar responsabilidades?
¿Cómo se recupera tras un reinicio?
```

OS-1 NO implementa todavía:

```text
Planner LLM
autonomía
scheduling humano
ejecución de jobs
inferencia
knowledge storage
```

---

# 2. Forma del producto

Primera versión:

```text
AI OS Core Service
```

Características:

```text
headless
local-first
FastAPI
SQLite + WAL
REST
event store durable
typed contracts
sin UI propia
```

Despliegue inicial recomendado:

```text
PC PRINCIPAL
```

junto a:

```text
ChatyGPT
Gestión-tareas-IA
Knowledge Orchestrator
```

No en el PC dedicado a IA.

---

# 3. Motivo del despliegue

AI OS Core gestiona:

```text
intención
contexto
objetivos
estado global
políticas
relaciones
```

No necesita GPU.

Además, debe seguir operativo aunque:

```text
PC IA esté apagado
AI Broker esté parado
Agora Runner esté desconectado
```

Por tanto:

```text
PC Principal = control plane
PC IA        = execution plane
```

---

# 4. Arquitectura interna

```text
┌───────────────────────────────────────────────┐
│                 API LAYER                     │
│ REST · Auth · Validation · Idempotency        │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              APPLICATION LAYER                │
│                                               │
│ GoalsService                                  │
│ ObjectivesService                             │
│ CapabilityRegistry                           │
│ PolicyService                                 │
│ EventService                                  │
│ DecisionService                               │
│ ResourceGraphService                          │
│ ContextService                                │
│ ServiceRegistry                               │
│ ReconciliationService                        │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                 DOMAIN                        │
│ Goal · Event · Policy · Capability · etc.     │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│             INFRASTRUCTURE                    │
│ SQLite · repositories · HTTP clients          │
│ credentials · clock · event dispatcher        │
└───────────────────────────────────────────────┘
```

---

# 5. Módulos internos

## `goals`

Responsable de:

```text
Goals
Objectives
progress
goal hierarchy
```

No crea Tasks directamente en OS-1.

---

# 6. `capabilities`

Responsable de:

```text
Capability Registry
providers
versions
availability
requirements
```

Debe poder responder:

```text
¿qué sistema sabe hacer X?
```

---

# 7. `skills`

AI OS sólo mantiene:

```text
Skill references
version
hash
provider
certification state
```

No contiene las instrucciones completas salvo necesidad futura.

---

# 8. `certifications`

Mantiene una proyección local de resultados cuya autoridad real es:

```text
Model Drift
```

El Core puede responder:

```text
¿esta combinación está certificada?
```

pero no realizar la prueba.

---

# 9. `events`

Uno de los módulos centrales.

Responsable de:

```text
persistir eventos
deduplicarlos
consultarlos
correlacionarlos
proyectarlos
disparar handlers internos
```

---

# 10. `policies`

Responsable de evaluar:

```text
ALLOW
DENY
REQUIRE_APPROVAL
CONSTRAIN
```

En OS-1 se limita a:

```text
almacenar
versionar
consultar
evaluar reglas deterministas simples
```

---

# 11. `decisions`

Mantiene ADRs/decisiones operativas globales.

Debe permitir:

```text
vigentes
superadas
afectadas por proyecto
afectadas por capability
```

---

# 12. `resources`

Implementa el Resource Graph ligero.

No hace falta una base de grafos.

Se modelará mediante:

```text
resources
relations
```

en SQLite.

---

# 13. `context`

En OS-1 será todavía básico.

Construirá Context Packages con:

```text
Goals
Objectives
Decisions
Policies
Resources
references
```

Sin búsqueda semántica avanzada.

Knowledge Orchestrator se conectará más adelante.

---

# 14. `services`

Service Registry.

Representa:

```text
AI Broker
Athena
Agora
Knowledge Orchestrator
Model Drift
Gestión-tareas-IA
ChatyGPT
```

junto con:

```text
endpoint
version
health
last_seen
contracts
```

---

# 15. `reconciliation`

Responsable de mantener sincronizada la proyección local con la autoridad externa.

Ejemplo:

```text
AI OS:
job running

Agora:
job completed

→ corregir proyección
```

---

# 16. `approvals`

OS-1 puede definir persistencia aunque la UI llegue después.

Gestiona:

```text
pending
approved
rejected
expired
```

---

# 17. `audit`

Debe existir desde el principio.

Almacena:

```text
command received
policy decision
state transition
service registration
reconciliation
approval
```

No almacenar:

```text
prompts
tokens
credenciales
documentos confidenciales
```

---

# 18. Estructura propuesta del repositorio

```text
AI_OS_Core/
│
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE
│
├── docs/
│   ├── CURRENT_STATE.md
│   ├── ARCHITECTURE.md
│   ├── CONTRACTS.md
│   ├── SECURITY.md
│   ├── API.md
│   └── adr/
│
├── src/
│   └── ai_os_core/
│       │
│       ├── app.py
│       ├── config.py
│       ├── bootstrap.py
│       │
│       ├── domain/
│       │   ├── goals.py
│       │   ├── objectives.py
│       │   ├── capabilities.py
│       │   ├── skills.py
│       │   ├── certifications.py
│       │   ├── events.py
│       │   ├── policies.py
│       │   ├── decisions.py
│       │   ├── resources.py
│       │   ├── context.py
│       │   ├── approvals.py
│       │   └── failures.py
│       │
│       ├── application/
│       │   ├── goals_service.py
│       │   ├── capability_registry.py
│       │   ├── policy_service.py
│       │   ├── event_service.py
│       │   ├── decision_service.py
│       │   ├── resource_graph.py
│       │   ├── context_service.py
│       │   ├── service_registry.py
│       │   ├── certification_service.py
│       │   ├── approval_service.py
│       │   └── reconciliation_service.py
│       │
│       ├── infrastructure/
│       │   ├── db/
│       │   │   ├── connection.py
│       │   │   ├── migrations/
│       │   │   └── repositories/
│       │   │
│       │   ├── http/
│       │   │   ├── clients/
│       │   │   └── auth.py
│       │   │
│       │   ├── events/
│       │   │   └── dispatcher.py
│       │   │
│       │   ├── security/
│       │   └── clock.py
│       │
│       ├── api/
│       │   ├── dependencies.py
│       │   ├── errors.py
│       │   ├── schemas/
│       │   └── routes/
│       │
│       └── workers/
│           ├── event_processor.py
│           ├── reconciliation_worker.py
│           └── health_worker.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── fixtures/
│
└── scripts/
```

---

# 19. Persistencia

Base:

```text
%LOCALAPPDATA%\AIOSCore\
```

Ejemplo:

```text
AIOSCore/
├── data/
│   └── ai_os_core.db
├── logs/
├── config/
└── backups/
```

---

# 20. SQLite

Configuración:

```text
WAL
foreign_keys = ON
busy_timeout
synchronous = NORMAL
```

No acceso concurrente directo desde aplicaciones externas.

Sólo API.

---

# 21. Tablas iniciales

```text
schema_versions

goals
objectives

services
service_capabilities

capabilities
capability_providers

skills
certifications

resources
resource_relations

policies

decisions

events

event_processing

approvals

context_packages

audit_log

idempotency_keys
```

---

# 22. `goals`

Campos esenciales:

```text
id
title
description
scope
owner
status
priority
parent_goal_id
deadline
review_at
progress
created_at
updated_at
```

---

# 23. `objectives`

```text
id
goal_id
title
description
status
acceptance_json
created_at
updated_at
```

---

# 24. `services`

```text
id
system_key
instance_id
version
base_url
health
last_seen
contract_json
auth_profile
created_at
updated_at
```

---

# 25. `capabilities`

```text
id
key
version
description
risk_class
autonomy_ceiling
input_schema_json
output_schema_json
status
created_at
updated_at
```

---

# 26. `capability_providers`

Permite futuros múltiples providers.

```text
capability_id
service_id
execution_type
actor
priority
status
requirements_json
```

---

# 27. `skills`

```text
id
key
version
provider_system
runtime
instructions_hash
manifest_json
status
observed_at
```

---

# 28. `certifications`

```text
id
skill_id
capability_id
fingerprint_hash
status
policy_ref
evidence_json
valid_until
source_ref
observed_at
```

---

# 29. `resources`

```text
id
type
owner_system
external_uri
display_name
external_version
immutable
observed_at
metadata_json
```

---

# 30. `resource_relations`

```text
source_id
relation_type
target_id
created_at
metadata_json
```

Índice obligatorio:

```text
source_id
target_id
relation_type
```

---

# 31. `events`

Tabla append-only.

```text
id
type
source_system
source_instance
subject_type
subject_id
occurred_at
recorded_at
correlation_id
causation_id
severity
classification
payload_json
idempotency_key
schema_version
```

Nunca:

```text
UPDATE evento
```

salvo metadata técnica excepcional.

---

# 32. `event_processing`

Separada de `events`.

```text
event_id
handler
status
attempts
last_error
next_retry_at
processed_at
```

Así un fallo de un handler no altera el evento.

---

# 33. Event processing model

```text
POST event
   ↓
validate
   ↓
persist event
   ↓
commit
   ↓
dispatcher
   ↓
handlers
```

Primero persistir.

Después procesar.

Nunca al revés.

---

# 34. Garantía básica

Objetivo:

```text
at-least-once processing
+
idempotent handlers
```

No hace falta exactamente-once.

Eso complicaría innecesariamente el sistema.

---

# 35. `policies`

```text
id
key
version
scope
type
priority
effect
conditions_json
constraints_json
enabled
valid_from
valid_until
```

---

# 36. `decisions`

```text
id
title
status
decision_text
rationale
scope_json
affects_json
evidence_json
supersedes
created_at
approved_by
```

---

# 37. `approvals`

```text
id
status
capability_ref
risk
action_json
consequences_json
affected_resources_json
expires_at
decision_json
created_at
updated_at
```

---

# 38. `context_packages`

Guardar únicamente snapshots generados.

```text
id
request_json
package_json
classification
created_at
expires_at
```

No necesitan ser eternos.

Política de retención configurable.

---

# 39. Idempotencia

Tabla:

```text
idempotency_keys
```

Campos:

```text
key
operation
request_hash
response_ref
created_at
expires_at
```

Caso:

```text
misma key
+
mismo request
→ misma respuesta

misma key
+
request distinto
→ 409 conflict
```

---

# 40. API layer

FastAPI.

Todo endpoint:

```text
validate
authenticate
authorize
invoke service
serialize
```

La ruta no contiene lógica de negocio.

---

# 41. API versioning

```text
/api/v1/
```

No utilizar inicialmente:

```text
/v1.1
```

Los contratos internos llevan su propio schema version.

---

# 42. Endpoints OS-1

## Health

```text
GET /api/v1/health
```

---

# 43. Service registry

```text
POST /api/v1/services/register
POST /api/v1/services/{id}/heartbeat

GET /api/v1/services
GET /api/v1/services/{id}
```

---

# 44. Goals

```text
GET   /api/v1/goals
POST  /api/v1/goals
GET   /api/v1/goals/{id}
PATCH /api/v1/goals/{id}
```

---

# 45. Objectives

```text
GET  /api/v1/goals/{id}/objectives
POST /api/v1/goals/{id}/objectives

GET   /api/v1/objectives/{id}
PATCH /api/v1/objectives/{id}
```

---

# 46. Capabilities

```text
GET  /api/v1/capabilities
GET  /api/v1/capabilities/{key}

POST /api/v1/capabilities/register
```

---

# 47. Skills

```text
GET /api/v1/skills
GET /api/v1/skills/{key}
```

Registro sólo mediante identidad de servicio.

---

# 48. Certifications

```text
GET /api/v1/certifications

GET /api/v1/certifications/current
```

Filtro:

```text
skill
model fingerprint
capability
status
```

---

# 49. Events

```text
POST /api/v1/events

GET /api/v1/events
GET /api/v1/events/{id}
```

---

# 50. Policies

```text
GET /api/v1/policies
GET /api/v1/policies/{id}

POST /api/v1/policies/evaluate
```

En OS-1 no se necesita una UI completa para edición.

---

# 51. Decisions

```text
GET  /api/v1/decisions
POST /api/v1/decisions

GET /api/v1/decisions/{id}
```

---

# 52. Resource Graph

```text
GET /api/v1/resources
GET /api/v1/resources/{id}

GET /api/v1/relations
```

---

# 53. Context

```text
POST /api/v1/context/resolve
```

En OS-1 sólo con información local al Core.

---

# 54. Approvals

```text
GET /api/v1/approvals

GET /api/v1/approvals/{id}

POST /api/v1/approvals/{id}/decision
```

---

# 55. Administración

Ruta separada:

```text
/api/v1/admin/
```

Para:

```text
reconciliation
service refresh
diagnostics
```

No para uso normal.

---

# 56. Service Registry

Cada aplicación registra:

```text
system
instance
version
endpoint
contracts
capabilities
events
```

AI OS no presupone que esté disponible.

---

# 57. Estado del servicio

```text
REGISTERED
HEALTHY
DEGRADED
UNREACHABLE
STALE
REMOVED
```

`STALE`:

```text
no heartbeat
pero no se ha confirmado caída
```

---

# 58. Heartbeat

No usar eventos cada segundo.

Intervalo inicial razonable:

```text
30–60 s
```

La frecuencia final es configuración de despliegue.

---

# 59. Health worker

Consulta periódicamente servicios registrados.

Debe comprobar:

```text
health
contract version
service version
```

No ejecutar operaciones mutables.

---

# 60. Reconciliation worker

Frecuencia más baja.

Ejemplo:

```text
cada varios minutos
```

Compara proyecciones importantes.

---

# 61. Event worker

Debe procesar inmediatamente eventos nuevos.

Puede usar:

```text
async queue
```

como acelerador.

Pero la fuente de verdad sigue siendo SQLite.

---

# 62. Reinicio

Al arrancar:

```text
apply migrations
 ↓
validate database
 ↓
load config
 ↓
recover pending event processing
 ↓
mark stale services
 ↓
start API
 ↓
start workers
```

---

# 63. Crash safety

Si cae tras:

```text
persist event
```

pero antes de:

```text
process event
```

el evento sigue pendiente.

Correcto.

---

# 64. Event handlers iniciales

OS-1 debería implementar sólo handlers deterministas.

Ejemplo:

```text
service.registered
→ update Resource Graph
```

---

# 65. Handler `model.changed`

En OS-1:

```text
recibe model.changed
 ↓
actualiza resource model
 ↓
busca certifications relacionadas
 ↓
marca proyección como stale
 ↓
crea aviso/evento interno
```

Todavía NO lanza Model Drift automáticamente.

Eso será OS-6.

---

# 66. Handler `skill.updated`

Igual:

```text
skill.updated
 ↓
actualizar manifest
 ↓
invalidar aplicabilidad de certifications
```

---

# 67. Handler `job.completed`

```text
job.completed
 ↓
actualizar Resource Graph
 ↓
relacionar artifacts
```

Gestión Tareas seguirá siendo quien actualice la Task.

AI OS sólo observa.

---

# 68. Context Engine OS-1

No usar embeddings.

Proceso:

```text
ContextRequest
    ↓
scope
    ↓
Goals
Objectives
Decisions
Policies
Resources
    ↓
filter
    ↓
ContextPackage
```

---

# 69. Context scoring inicial

Determinista:

```text
exact project match
exact goal match
exact capability match
active status
freshness
```

No LLM.

---

# 70. Context exclusion

Context Package debe registrar:

```text
qué se excluyó
por qué
```

Ejemplos:

```text
sensitivity exceeded
expired
superseded
wrong project
irrelevant scope
```

---

# 71. Resource Graph implementation

No realizar consultas recursivas SQL complejas inicialmente.

Profundidad máxima sugerida:

```text
1–3 relaciones
```

según operación.

---

# 72. Resource Graph no es Knowledge Graph semántico

No tratar de inferir automáticamente:

```text
Athena se parece a agente
→ es agente
```

Sólo relaciones explícitas.

---

# 73. Policy Engine OS-1

Primera versión:

```text
JSON conditions
+
deterministic evaluator
```

Operadores:

```text
equals
not_equals
in
not_in
greater_than
less_than
contains
exists
```

Nada de lenguaje de reglas complejo todavía.

---

# 74. Ejemplo

```yaml
policy:
  key: require-certification

  type: certification

  effect: deny

  conditions:
    - field: capability.certification.required
      operator: equals
      value: true

    - field: certification.status
      operator: not_equals
      value: certified
```

---

# 75. Conflictos de Policy

Orden:

```text
DENY
REQUIRE_APPROVAL
CONSTRAIN
ALLOW
```

Después:

```text
priority
specificity
```

---

# 76. No usar LLM en Policies

Nunca:

```text
Pregunta al modelo si esta acción parece segura.
```

para decidir una Policy.

Debe ser determinista.

---

# 77. Authentication OS-1

Dos niveles:

```text
user/client
service
```

---

# 78. Service authentication

Primera implementación:

```text
Bearer token
```

Token por servicio.

Ejemplo:

```text
AI_BROKER_TOKEN != ATHENA_TOKEN != TASK_MANAGER_TOKEN
```

---

# 79. Almacenamiento de tokens

No SQLite en texto plano.

En Windows:

```text
Credential Manager / DPAPI
```

---

# 80. UI clients

ChatyGPT puede recibir un token de usuario/API distinto de los tokens service-to-service.

---

# 81. Network model

Inicialmente:

```text
127.0.0.1
```

cuando todos los consumidores están en PC principal.

Para PC IA:

```text
HTTPS LAN
```

si Agora/Broker necesitan publicar eventos directamente.

---

# 82. Alternativa recomendada

Evitar que AI Broker tenga que conectar directamente al PC principal al principio.

Puede usarse:

```text
Agora Board / bridge
```

o un pequeño cliente emisor.

Pero el contrato no debe depender del transporte.

---

# 83. Deployment

Proceso:

```text
ai-os-core.exe
```

o:

```text
python -m ai_os_core
```

Posteriormente:

```text
Windows Service
```

si merece la pena.

No obligatorio en MVP.

---

# 84. Configuración

Archivo:

```text
config.yaml
```

Sólo datos no secretos:

```yaml
server:
  host: 127.0.0.1
  port: 8780

database:
  path: ...

workers:
  health_interval:
  reconciliation_interval:

logging:
  level:
```

---

# 85. Secretos

Fuera de YAML.

Ejemplo:

```text
Windows Credential Manager
```

---

# 86. Logging

JSON estructurado interno.

Campos:

```text
timestamp
level
component
event
correlation_id
resource_id
message
```

Nunca:

```text
prompt
document content
tokens secretos
auth headers
```

---

# 87. Audit Log vs Log

Diferentes.

### Log

Diagnóstico técnico.

### Audit

Registro durable de decisiones/acciones.

No deben mezclarse.

---

# 88. Audit examples

```text
service_registered
policy_evaluated
goal_created
approval_decided
certification_invalidated
state_reconciled
```

---

# 89. Backup

AI OS Core contiene poca información, pero importante.

Backup:

```text
SQLite backup API
```

No copiar DB abierta de forma bruta.

---

# 90. Backup contents

```text
database
non-secret config
schema version
```

No:

```text
credentials
logs completos
```

---

# 91. Retention

Events:

```text
durables
```

pero puede existir archivado posterior.

Context Packages:

```text
retención limitada
```

Audit:

```text
durable
```

---

# 92. Testing architecture

Cuatro niveles:

```text
unit
integration
contract
end-to-end-local
```

---

# 93. Unit tests

Para:

```text
policy evaluator
state transitions
ULID validation
schema validation
relation rules
context filtering
```

---

# 94. Integration

SQLite real temporal:

```text
repositories
migrations
idempotency
event processing
```

---

# 95. Contract tests

Muy importantes.

Fixtures de:

```text
Event
CapabilityManifest
SkillManifest
Certification
Goal
ContextPackage
```

---

# 96. Compatibility

Lectura:

```text
tolerar campos adicionales
```

Escritura:

```text
sólo contrato conocido
```

---

# 97. Corrupt input

Nunca persistir parcialmente.

Proceso:

```text
validate
 ↓
transaction
 ↓
commit
```

---

# 98. Error API común

```yaml
error:

  code:

  message:

  retryable:

  correlation_id:

  details:
```

---

# 99. HTTP status

Uso consistente:

```text
200 OK
201 Created
202 Accepted
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Contract Validation
503 Dependency Unavailable
```

---

# 100. No devolver 500 como explicación

Errores esperables deben traducirse.

Ejemplo:

```text
CERTIFICATION_REQUIRED
```

no:

```text
Internal Server Error
```

---

# 101. OS-1 no implementa Commands externos

Por ahora:

```text
observe
register
query
evaluate
```

No:

```text
dispatch work
```

Eso reduce riesgo.

---

# 102. Flujo inicial: registrar Athena

```text
Athena
 ↓
POST /services/register
 ↓
AI OS
 ↓
service record
 ↓
capability manifests
 ↓
Skill references
 ↓
Resource Graph
```

---

# 103. Flujo inicial: model changed

```text
AI Broker
 ↓
model.changed
 ↓
AI OS event store
 ↓
resource update
 ↓
certification projections stale
 ↓
audit
```

---

# 104. Flujo inicial: Goal

```text
ChatyGPT
 ↓
POST /goals
 ↓
AI OS
 ↓
Goal persisted
 ↓
goal.created Event
 ↓
Resource Graph
```

No genera tareas.

---

# 105. Flujo inicial: Context

```text
Client
 ↓
ContextRequest
 ↓
AI OS
 ↓
Goals
Decisions
Policies
Resources
 ↓
filter
 ↓
ContextPackage
```

---

# 106. Flujo futuro no implementado aún

```text
Goal
 ↓
Planner
 ↓
Task proposal
 ↓
Gestión Tareas
```

Sólo reservar interfaces.

---

# 107. Service dependencies

AI OS Core debe poder arrancar con:

```text
0 servicios externos
```

Estado:

```text
healthy
```

aunque sus capabilities externas estén:

```text
unavailable
```

---

# 108. Health semantics

Core sano:

```text
database ok
workers ok
API ok
```

No significa:

```text
AI Broker disponible
```

Eso aparece como dependency status.

---

# 109. Evitar dependencia circular

AI OS no debe necesitar AI Broker para arrancar.

AI Broker no debe necesitar AI OS para inferir.

Athena no debe necesitar AI OS para funcionar en modo standalone.

Gestión Tareas tampoco.

Principio:

```text
AI OS integration = additive
```

---

# 110. Modo degradado

Cada aplicación existente debe seguir funcionando sin Core cuando sea razonable.

Ejemplo:

```text
ChatyGPT → Broker
```

debe poder seguir funcionando.

---

# 111. Compatibilidad progresiva

Añadir:

```text
AI OS aware
```

sin romper:

```text
standalone
```

---

# 112. Feature negotiation

Service registration debe anunciar:

```text
contracts
features
capabilities
```

AI OS no presupone campos no anunciados.

---

# 113. Ejemplo

```yaml
features:
  - events_v1
  - capabilities_v1
  - model_fingerprint_v1
```

---

# 114. Migrations

Cada migración:

```text
versioned
forward-only
transactional
tested
```

No editar migraciones aplicadas.

---

# 115. Database version

Tabla:

```text
schema_versions
```

separada de:

```text
API version
contract version
app version
```

---

# 116. Startup compatibility check

Al arrancar:

```text
DB version
 ↓
supported?
 ├── yes → continue
 └── no → fail clearly
```

No realizar downgrade automático.

---

# 117. Código de dominio

Domain no conoce:

```text
FastAPI
SQLite
HTTP
Windows
```

Para mantenerlo testeable.

---

# 118. Repositories

Interfaces:

```text
GoalRepository
EventRepository
ResourceRepository
PolicyRepository
...
```

Implementación:

```text
SQLite...
```

---

# 119. Clock abstraction

Necesario para:

```text
tests
expiry
staleness
policies
```

---

# 120. ID generator abstraction

ULID.

Test sustituible por generador determinista.

---

# 121. Config boundaries

Configuración externa no debe alterar invariantes.

Ejemplo:

No permitir:

```text
disable_policy_validation=true
```

---

# 122. Invariantes estructurales

No configurables:

```text
events append-only
skills cannot grant privilege
only owner is authoritative
policy DENY precedence
idempotency guarantees
```

---

# 123. OS-1 Acceptance Gates

Antes de pasar a OS-2:

### Gate 1

Todos los schemas OS-0 codificados y validados.

### Gate 2

SQLite migrations verdes.

### Gate 3

Event Store durable.

### Gate 4

Idempotency funcional.

### Gate 5

Resource Graph funcional.

### Gate 6

Goal CRUD lógico.

### Gate 7

Capability Registry funcional.

### Gate 8

Policy evaluation determinista.

### Gate 9

Service Registration funcional.

### Gate 10

Context Package básico.

### Gate 11

Restart recovery.

### Gate 12

Contract tests.

---

# 124. Lo que NO debe entrar en OS-1

Bloquear expresamente:

```text
Planner LLM
automatic task creation
Agora dispatch
Google Calendar writes
Model Drift execution
knowledge semantic search
AI scheduling
model routing
agent control
```

---

# 125. Tamaño esperado

AI OS Core OS-1 debería ser relativamente pequeño.

Conceptualmente:

```text
control plane
```

no plataforma gigantesca.

Si OS-1 empieza a incluir:

```text
LLMs
RAG
scheduler
workers
file processing
```

se está desviando.

---

# 126. Arquitectura física inicial

```text
PC PRINCIPAL
│
├── ChatyGPT
├── Gestión-tareas-IA
├── Knowledge Orchestrator
├── AI OS Core
│
└────────────── LAN ──────────────┐
                                  │
PC IA                             │
│                                 │
├── Agora Runner                  │
├── AI Broker                     │
├── Ollama / LM Studio            │
└── modelos                       │
```

Athena puede estar:

```text
PC principal
```

cuando trabaja sobre repositorios locales.

---

# 127. Comunicación futura

```text
ChatyGPT ──► AI OS Core
Tasks    ──► AI OS Core
KO       ──► AI OS Core

AI OS Core ──► consultas

Agora/Broker ──► events
```

---

# 128. Recomendación de tecnología

Para OS-1:

```text
Python 3.12+
FastAPI
Pydantic v2
SQLite
SQLAlchemy opcional
httpx
```

Yo preferiría evitar un ORM pesado si el modelo de datos sigue pequeño.

Una capa Repository con SQL explícito puede ser más transparente.

---

# 129. Concurrencia

FastAPI async para red.

SQLite:

```text
short transactions
single writer semantics
WAL
```

No mantener transacciones mientras se hace HTTP.

---

# 130. Regla crítica

Nunca:

```text
BEGIN TRANSACTION
 ↓
HTTP request externo
 ↓
esperar
 ↓
COMMIT
```

Primero:

```text
persist intent/state
commit
external operation
persist result
```

cuando más adelante existan Commands.

---

# 131. Preparación para Outbox

Aunque OS-1 todavía no ejecute Commands externos, conviene reservar:

```text
outbox
```

para OS posteriores.

---

# 132. Tabla `outbox` futura

```text
id
command
target
status
attempts
next_retry_at
```

Así se evitará:

```text
DB commit succeeded
HTTP dispatch lost
```

---

# 133. Inbox

Eventos externos funcionan conceptualmente como:

```text
inbox
```

con idempotency.

---

# 134. Observabilidad

Endpoint:

```text
GET /api/v1/admin/status
```

Debe mostrar:

```text
DB
workers
event backlog
registered services
stale services
failed handlers
```

Sin secretos.

---

# 135. Métricas futuras

Reservar:

```text
events_processed
events_failed
services_healthy
capabilities_available
certifications_valid
```

No hace falta Prometheus inicialmente.

---

# 136. Seguridad

Principios:

```text
least privilege
service identity
no secrets in payload
no direct filesystem mutation
no remote execution
```

Esto hace que AI OS Core sea un servicio de riesgo relativamente bajo.

---

# 137. Threat model inicial

Riesgos:

```text
service spoofing
malicious event
replay
payload injection
resource reference spoofing
policy tampering
credential exposure
```

Mitigaciones:

```text
auth
schema validation
idempotency
owner validation
audit
DPAPI/Credential Manager
```

---

# 138. Owner validation

Ejemplo:

Si:

```text
source_system = ai_broker
```

intenta publicar:

```text
task.completed
```

AI OS debe rechazarlo.

Porque:

```text
Task owner = Gestión Tareas
```

---

# 139. Event authority matrix

Cada evento tendrá fuentes autorizadas.

Ejemplo:

```text
model.changed
→ AI Broker

job.completed
→ Agora

agent.run.completed
→ Athena

knowledge.updated
→ Knowledge Orchestrator

certification.completed
→ Model Drift
```

---

# 140. Contract test obligatorio

Intentar publicar evento con source incorrecto:

```text
422 / 403
```

según naturaleza.

---

# 141. Resource URI validation

No aceptar libremente:

```text
knowledge://anything
```

Debe validarse namespace y owner.

---

# 142. External URI no implica acceso

AI OS puede almacenar:

```text
knowledge://claim/123
```

sin saber cómo leerlo todavía.

---

# 143. Estado derivado

Ejemplo:

```text
Capability status
```

puede derivarse de:

```text
provider health
+
certification
+
resource availability
```

Pero debe distinguir:

```text
declared_status
derived_status
```

---

# 144. Nunca sobrescribir la fuente

Si Athena dice:

```text
available
```

AI OS puede derivar:

```text
unusable
```

porque certification failed.

Pero no debe modificar Athena.

---

# 145. `CapabilityAvailability`

Modelo derivado:

```yaml
capability_availability:

  capability:

  provider:

  provider_status:

  certification_status:

  policy_status:

  effective_status:

  reasons: []
```

---

# 146. Effective status

```text
AVAILABLE
DEGRADED
BLOCKED
UNAVAILABLE
UNKNOWN
```

---

# 147. Primera UI

No crearla en OS-1.

Para pruebas:

```text
OpenAPI / Swagger
CLI opcional
```

Después ChatyGPT consumirá APIs.

---

# 148. CLI mínima opcional

```text
aios status
aios services
aios goals
aios capabilities
aios events
```

Sólo diagnóstico.

---

# 149. Naming

Nombre técnico del servicio:

```text
AI OS Core
```

package:

```text
ai_os_core
```

Proceso:

```text
ai-os-core
```

---

# 150. Definición final de OS-1

AI OS Core OS-1 debe ser:

> **un control plane durable y determinista que sabe qué existe en el ecosistema, qué capacidades ofrece cada servicio, qué objetivos están activos, qué reglas se aplican y qué hechos han ocurrido.**

No tiene todavía inteligencia autónoma.

---

# 151. Resultado final de OS-1

Con OS-1 implementado podríamos preguntar:

```text
¿Qué servicios están activos?

¿Qué capabilities tengo?

¿Qué modelo cambió?

¿Qué skill ha quedado sin certificación?

¿Qué Goals existen?

¿Qué decisiones afectan a Athena?

¿Qué relaciones existen entre un proyecto y sus recursos?

¿Qué eventos ocurrieron en una ejecución?
```

Y responder sin consultar manualmente siete aplicaciones.

---

# 152. Próxima fase

Una vez construido OS-1:

```text
OS-2 — Service Discovery & Integration
```

tendría como objetivo conectar realmente:

```text
AI Broker
Athena
Agora
Gestión-tareas-IA
Knowledge Orchestrator
Model Drift
```

uno a uno.

Pero todavía sin Planner ni autonomía.

---

# 153. Orden recomendado de conexión en OS-2

```text
1. AI Broker
2. Model Drift
3. Athena
4. Agora
5. Gestión-tareas-IA
6. Knowledge Orchestrator
7. ChatyGPT
8. Local AI Lab
```

Motivo:

```text
primero intelligence/certification
después runtime
después scheduling/context/UI
```

---

# 154. Decisión de arquitectura

Con OS-1 ya podemos contestar la pregunta inicial:

> ¿Hace falta una nueva aplicación?

No todavía.

Hace falta:

```text
un nuevo servicio
```

con una responsabilidad muy concreta.

La interfaz debería seguir perteneciendo inicialmente a:

```text
ChatyGPT
+
Gestión-tareas-IA
```

según lo que se esté visualizando.

---

# 155. Regla de éxito

AI OS Core estará bien diseñado si dentro de un año podemos sustituir:

```text
Athena
AI Broker
Model Drift
```

por otros componentes compatibles sin reescribir el Core.

Eso demostraría que realmente hemos construido:

```text
un sistema operativo de capacidades
```

y no:

```text
un conjunto de integraciones pegadas entre sí.
```