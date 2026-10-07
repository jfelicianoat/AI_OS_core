He cerrado OS-0 como \*\*contrato de integración\*\*, no como diseño de implementación. La idea es que, a partir de aquí, cada repositorio tenga una frontera técnica inequívoca y podamos preparar después los prompts por proyecto sin inventar decisiones nuevas.



\# AI OS Core — OS-0 Contratos Maestros v0.1



\*\*Estado:\*\* propuesta normativa previa a implementación

\*\*Objetivo:\*\* congelar los contratos entre AI OS Core y las aplicaciones existentes antes de escribir código.



\---



\# 1. Objetivo de OS-0



OS-0 no implementa funcionalidad.



Define:



```text

qué entidades existen

quién es propietario de cada una

cómo se identifican

cómo se versionan

qué estados pueden tener

cómo se relacionan

qué eventos se publican

qué APIs mínimas se necesitan

qué datos puede modificar cada aplicación

qué datos sólo puede consultar

```



Una vez aprobado OS-0, cualquier cambio incompatible deberá tratarse como:



```text

contract change

```



y no como una modificación informal de implementación.



\---



\# 2. Principio de propiedad



Cada entidad tiene un único `owner\_system`.



| Entidad             | Sistema propietario        |

| ------------------- | -------------------------- |

| Goal                | AI OS Core                 |

| Objective           | AI OS Core                 |

| Resource Graph      | AI OS Core                 |

| Decision            | AI OS Core                 |

| Policy global       | AI OS Core                 |

| Capability Registry | AI OS Core                 |

| Context Package     | AI OS Core                 |

| Human Task          | Gestión-tareas-IA          |

| AI Task             | Gestión-tareas-IA          |

| Hybrid Task         | Gestión-tareas-IA          |

| Calendar            | Gestión-tareas-IA          |

| Job/Card            | Agora                      |

| Agent Run           | Athena                     |

| Inference           | AI Broker                  |

| Model catalogue     | AI Broker                  |

| Knowledge document  | Knowledge Orchestrator     |

| Knowledge claim     | Knowledge Orchestrator     |

| Skill               | runtime que la proporciona |

| Certification       | Model Drift                |

| Experiment          | Local AI Lab               |

| Capture             | YT Capture Plugin          |



Un sistema externo puede mantener:



```text

reference

projection

cache

snapshot

```



pero nunca convertirse en propietario por duplicación.



\---



\# 3. Identificadores globales



Todos los objetos interoperables usarán:



```text

<namespace>\_<ulid>

```



Ejemplos:



```text

goal\_01K...

obj\_01K...

task\_01K...

job\_01K...

run\_01K...

cap\_01K...

skill\_01K...

cert\_01K...

evt\_01K...

decision\_01K...

artifact\_01K...

resource\_01K...

```



\## 3.1 Motivo



ULID permite:



```text

unicidad global

orden temporal aproximado

generación offline

legibilidad mayor que UUID aleatorio

```



\---



\# 4. Correlation ID



Toda operación distribuida deberá llevar:



```text

correlation\_id

```



El mismo valor seguirá el flujo:



```text

Goal

&#x20;↓

Objective

&#x20;↓

Task

&#x20;↓

Job

&#x20;↓

Agent Run

&#x20;↓

Broker Task

&#x20;↓

Artifact

```



No sustituye a los IDs propios.



\---



\# 5. Causation ID



Todo Event podrá declarar:



```text

causation\_id

```



Ejemplo:



```text

evt\_model\_changed

&#x20;     ↓

causa

&#x20;     ↓

evt\_certification\_requested

```



Así se reconstruye:



```text

qué ocurrió

qué lo provocó

```



\---



\# 6. Idempotency Key



Toda operación de escritura entre servicios deberá aceptar:



```text

idempotency\_key

```



Regla:



> Repetir exactamente la misma petición con la misma clave no puede crear un segundo objeto.



\---



\# 7. Versionado contractual



Todos los documentos interoperables llevarán:



```yaml

schema:

&#x20; name: goal

&#x20; version: "1.0"

```



Reglas:



\### Compatible



```text

1.0 → 1.1

```



Puede añadir campos opcionales.



\### Incompatible



```text

1.x → 2.0

```



Puede cambiar significado, obligatoriedad o estructura.



\---



\# 8. Envelope común



Todos los objetos importantes utilizarán conceptualmente:



```yaml

schema:

&#x20; name:

&#x20; version:



id:



created\_at:

updated\_at:



owner\_system:



correlation\_id:



metadata:

```



`metadata` no puede utilizarse para introducir comportamiento oculto.



\---



\# 9. Resource Reference



Éste será uno de los contratos fundamentales.



Permite referenciar un objeto propiedad de otra aplicación.



```yaml

resource\_reference:



&#x20; resource\_id:

&#x20;   type: string



&#x20; resource\_type:

&#x20;   type: string



&#x20; owner\_system:

&#x20;   enum:

&#x20;     - ai\_os

&#x20;     - task\_manager

&#x20;     - agora

&#x20;     - athena

&#x20;     - ai\_broker

&#x20;     - knowledge\_orchestrator

&#x20;     - model\_drift

&#x20;     - local\_ai\_lab

&#x20;     - chatygpt

&#x20;     - yt\_capture



&#x20; uri:

&#x20;   type: string



&#x20; version:

&#x20;   type: string | null



&#x20; display\_name:

&#x20;   type: string | null



&#x20; immutable:

&#x20;   type: boolean



&#x20; observed\_at:

&#x20;   type: datetime

```



Ejemplos:



```text

athena://run/run\_...

agora://job/job\_...

knowledge://claim/claim\_...

broker://model/ollama/qwen...

tasks://task/task\_...

```



\---



\# 10. Contrato Goal



Goal representa un resultado deseado.



Nunca una instrucción de ejecución.



```yaml

goal:



&#x20; id: goal\_...



&#x20; title: string



&#x20; description: string



&#x20; scope:

&#x20;   enum:

&#x20;     - global

&#x20;     - personal

&#x20;     - project



&#x20; owner:

&#x20;   enum:

&#x20;     - user

&#x20;     - system



&#x20; project\_refs: \[]



&#x20; status:

&#x20;   enum:

&#x20;     - proposed

&#x20;     - active

&#x20;     - paused

&#x20;     - blocked

&#x20;     - achieved

&#x20;     - cancelled



&#x20; priority:

&#x20;   enum:

&#x20;     - critical

&#x20;     - high

&#x20;     - normal

&#x20;     - low



&#x20; success\_criteria:

&#x20;   - type:

&#x20;     description:

&#x20;     verification\_method:



&#x20; constraints: \[]



&#x20; parent\_goal\_id:

&#x20;   string | null



&#x20; deadline:

&#x20;   datetime | null



&#x20; review\_at:

&#x20;   datetime | null



&#x20; autonomy\_policy\_id:

&#x20;   string | null



&#x20; progress:

&#x20;   type: number

&#x20;   minimum: 0

&#x20;   maximum: 1



&#x20; provenance:

&#x20;   source:

&#x20;   source\_ref:



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 11. Reglas Goal



No se permite:



```text

Goal → ejecutar directamente una herramienta

```



Debe existir:



```text

Goal

&#x20;↓

Objective

&#x20;↓

Task

```



Puede haber Goals sin Tasks.



Ejemplo:



```text

Mantener los proyectos de IA documentados y coherentes.

```



\---



\# 12. Contrato Objective



Objective representa un resultado intermedio verificable.



```yaml

objective:



&#x20; id: obj\_...



&#x20; goal\_id:



&#x20; title:

&#x20; description:



&#x20; status:

&#x20;   enum:

&#x20;     - proposed

&#x20;     - active

&#x20;     - blocked

&#x20;     - achieved

&#x20;     - cancelled



&#x20; acceptance\_criteria: \[]



&#x20; dependencies:

&#x20;   - objective\_id:



&#x20; related\_task\_ids: \[]



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 13. Goal → Objective



Cardinalidad:



```text

Goal 1 ───── 0..N Objectives

```



Un Goal puede existir inicialmente sin descomposición.



\---



\# 14. Contrato Capability



Capability representa algo que el ecosistema sabe hacer.



Ejemplos:



```text

analyze\_repository

query\_knowledge

generate\_summary

verify\_codebase

compare\_model\_behavior

extract\_claims

```



\---



\# 15. Capability Manifest



```yaml

capability:



&#x20; id: cap\_...



&#x20; key:

&#x20;   type: string

&#x20;   example: analyze\_repository



&#x20; version:

&#x20;   type: string



&#x20; description:



&#x20; provider:

&#x20;   system:

&#x20;   service:

&#x20;   endpoint\_ref:



&#x20; execution\_type:

&#x20;   enum:

&#x20;     - synchronous

&#x20;     - asynchronous

&#x20;     - durable



&#x20; actor:

&#x20;   enum:

&#x20;     - human

&#x20;     - ai

&#x20;     - hybrid

&#x20;     - deterministic



&#x20; input\_schema\_ref:



&#x20; output\_schema\_ref:



&#x20; permissions\_required: \[]



&#x20; skills\_required: \[]



&#x20; resources\_required: \[]



&#x20; risk\_class:

&#x20;   enum:

&#x20;     - R0

&#x20;     - R1

&#x20;     - R2

&#x20;     - R3

&#x20;     - R4



&#x20; cancellable:

&#x20;   boolean



&#x20; resumable:

&#x20;   boolean



&#x20; produces\_artifacts:

&#x20;   boolean



&#x20; verification:

&#x20;   required:

&#x20;   verifier\_capability:



&#x20; certification:

&#x20;   required:

&#x20;   policy\_id:



&#x20; autonomy\_ceiling:

&#x20;   enum:

&#x20;     - A0

&#x20;     - A1

&#x20;     - A2

&#x20;     - A3

&#x20;     - A4

&#x20;     - A5



&#x20; tags: \[]



&#x20; status:

&#x20;   enum:

&#x20;     - available

&#x20;     - degraded

&#x20;     - unavailable

&#x20;     - deprecated

```



\---



\# 16. Capability key



`key` debe ser estable y semántico.



Ejemplo:



```text

analyze\_repository

```



No:



```text

athena\_analyze\_repository\_v4

```



El proveedor puede cambiar sin cambiar la necesidad.



\---



\# 17. Capability Provider



Una misma Capability puede tener varios providers.



Ejemplo futuro:



```text

analyze\_repository

&#x20;   │

&#x20;   ├── Athena

&#x20;   ├── Agent-X

&#x20;   └── servicio remoto

```



El Registry podrá elegir posteriormente.



En MVP puede existir un único proveedor.



\---



\# 18. Contrato Skill



Skill representa conocimiento procedimental utilizado por un runtime.



```yaml

skill:



&#x20; id: skill\_...



&#x20; key:



&#x20; version:



&#x20; provider\_system:



&#x20; runtime:



&#x20; description:



&#x20; applicable\_capabilities: \[]



&#x20; instructions\_hash:



&#x20; required\_toolsets: \[]



&#x20; required\_context: \[]



&#x20; output\_expectations: \[]



&#x20; risk\_constraints: \[]



&#x20; test\_suite\_ref:



&#x20; status:

&#x20;   enum:

&#x20;     - active

&#x20;     - deprecated

&#x20;     - disabled



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 19. Skill no concede permisos



Regla obligatoria:



```text

Skill permissions

&#x20;       ≤

Runtime permissions

```



Nunca:



```text

Skill

&#x20; ↓

aumenta privilege

```



Athena ya sigue este principio y debe conservarse.



\---



\# 20. Skill Execution Fingerprint



Cada ejecución relevante deberá poder producir:



```yaml

execution\_fingerprint:



&#x20; skill:

&#x20;   key:

&#x20;   version:

&#x20;   instructions\_hash:



&#x20; capability:

&#x20;   key:

&#x20;   version:



&#x20; model:

&#x20;   provider:

&#x20;   deployment:

&#x20;   family:

&#x20;   version:

&#x20;   artifact\_hash:

&#x20;   quantization:

&#x20;   chat\_template\_hash:



&#x20; runtime:

&#x20;   name:

&#x20;   version:



&#x20; tools:

&#x20;   - key:

&#x20;     version:

&#x20;     schema\_hash:



&#x20; policy:

&#x20;   version:



&#x20; generation:

&#x20;   temperature:

&#x20;   top\_p:

&#x20;   seed:

&#x20;   context\_limit:



&#x20; observed\_at:

```



Los campos que no puedan verificarse:



```text

null

```



Nunca se inferirán.



\---



\# 21. Contrato Certification



Propietario:



```text

Model Drift

```



```yaml

certification:



&#x20; id: cert\_...



&#x20; skill\_ref:



&#x20; capability\_ref:



&#x20; fingerprint:



&#x20; suite\_ref:



&#x20; baseline\_ref:



&#x20; status:

&#x20;   enum:

&#x20;     - unknown

&#x20;     - testing

&#x20;     - certified

&#x20;     - degraded

&#x20;     - failed

&#x20;     - revoked



&#x20; started\_at:

&#x20; completed\_at:



&#x20; policy\_ref:



&#x20; blocking\_failures: \[]



&#x20; warnings: \[]



&#x20; evidence\_refs: \[]



&#x20; valid\_until:

&#x20;   datetime | null



&#x20; supersedes:

&#x20;   certification\_id | null

```



\---



\# 22. Cambio de fingerprint



Si cambia cualquier componente bloqueante:



```text

model

model version

quantization

runtime

skill

toolset

policy

chat template

```



la certificación previa pasa conceptualmente a:



```text

not\_applicable

```



La nueva combinación comienza como:



```text

UNKNOWN

```



\---



\# 23. Evento model.changed



AI Broker publicará:



```yaml

event:



&#x20; type: model.changed



&#x20; subject:

&#x20;   resource\_type: model

&#x20;   resource\_id:



&#x20; payload:



&#x20;   previous\_fingerprint:

&#x20;   current\_fingerprint:



&#x20;   changed\_fields: \[]



&#x20;   observed\_at:

```



\---



\# 24. Reacción a model.changed



AI OS Core:



```text

model.changed

&#x20;      ↓

buscar certifications afectadas

&#x20;      ↓

marcarlas no aplicables al nuevo fingerprint

&#x20;      ↓

evaluar Policy

&#x20;      ↓

crear Certification Request

```



No debe certificar por sí mismo.



\---



\# 25. Certification Request



```yaml

certification\_request:



&#x20; id:



&#x20; skill\_ref:



&#x20; capability\_ref:



&#x20; candidate\_fingerprint:



&#x20; baseline\_certification\_ref:



&#x20; reason:

&#x20;   enum:

&#x20;     - model\_changed

&#x20;     - skill\_changed

&#x20;     - runtime\_changed

&#x20;     - tool\_changed

&#x20;     - policy\_changed

&#x20;     - manual



&#x20; priority:



&#x20; requested\_at:



&#x20; correlation\_id:

```



\---



\# 26. Contrato Event



```yaml

event:



&#x20; schema:

&#x20;   name: event

&#x20;   version: "1.0"



&#x20; id: evt\_...



&#x20; type:



&#x20; source:

&#x20;   system:

&#x20;   instance\_id:



&#x20; subject:

&#x20;   resource\_type:

&#x20;   resource\_id:



&#x20; occurred\_at:



&#x20; recorded\_at:



&#x20; correlation\_id:



&#x20; causation\_id:

&#x20;   string | null



&#x20; idempotency\_key:



&#x20; severity:

&#x20;   enum:

&#x20;     - debug

&#x20;     - info

&#x20;     - notice

&#x20;     - warning

&#x20;     - error

&#x20;     - critical



&#x20; payload:



&#x20; classification:

&#x20;   enum:

&#x20;     - public

&#x20;     - internal

&#x20;     - confidential

&#x20;     - sensitive

```



\---



\# 27. Eventos mínimos del ecosistema



\## AI Broker



```text

model.discovered

model.changed

model.removed

model.capability\_changed



broker.capacity\_changed

broker.task.started

broker.task.completed

broker.task.failed

```



\## Athena



```text

agent.run.started

agent.run.completed

agent.run.failed



agent.verification.failed

agent.repair.started

agent.repair.completed



skill.updated

```



\## Agora



```text

job.created

job.claimed

job.started

job.completed

job.failed

job.cancelled



artifact.created



worker.available

worker.unavailable

```



\## Gestión-tareas-IA



```text

task.created

task.updated

task.started

task.completed

task.blocked

task.cancelled



schedule.changed



human.capacity\_changed

```



\## Knowledge Orchestrator



```text

knowledge.created

knowledge.updated

knowledge.superseded

knowledge.contradicted

knowledge.expired

```



\## Model Drift



```text

certification.started

certification.completed

certification.degraded

certification.failed

certification.revoked

```



\## Local AI Lab



```text

experiment.completed

evidence.available

```



\---



\# 28. Events son hechos



No utilizar eventos como comandos.



Incorrecto:



```text

event:

&#x20; type: run\_tests

```



Correcto:



```text

command:

&#x20; capability: run\_tests

```



Y posteriormente:



```text

event:

&#x20; type: tests.completed

```



\---



\# 29. Contrato Policy



```yaml

policy:



&#x20; id:



&#x20; key:



&#x20; version:



&#x20; scope:

&#x20;   enum:

&#x20;     - global

&#x20;     - project

&#x20;     - capability

&#x20;     - skill

&#x20;     - model

&#x20;     - task



&#x20; type:

&#x20;   enum:

&#x20;     - security

&#x20;     - privacy

&#x20;     - autonomy

&#x20;     - resource

&#x20;     - scheduling

&#x20;     - certification

&#x20;     - cost

&#x20;     - approval



&#x20; priority:

&#x20;   integer



&#x20; effect:

&#x20;   enum:

&#x20;     - allow

&#x20;     - deny

&#x20;     - require\_approval

&#x20;     - constrain



&#x20; conditions: \[]



&#x20; constraints: \[]



&#x20; valid\_from:

&#x20; valid\_until:



&#x20; enabled:



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 30. Resolución de Policies



Principio:



```text

DENY > REQUIRE\_APPROVAL > CONSTRAIN > ALLOW

```



Una Policy específica puede restringir una global.



Nunca ampliarla más allá del máximo estructural del sistema.



\---



\# 31. Autonomy Contract



```yaml

autonomy:



&#x20; level:

&#x20;   enum:

&#x20;     - A0

&#x20;     - A1

&#x20;     - A2

&#x20;     - A3

&#x20;     - A4

&#x20;     - A5



&#x20; capability\_ceiling:



&#x20; requires\_certification:



&#x20; requires\_recent\_success\_count:



&#x20; requires\_human\_approval\_for: \[]



&#x20; forbidden\_actions: \[]

```



\---



\# 32. Definición de niveles



```text

A0 OBSERVE

&#x20;   no propone ni ejecuta



A1 RECOMMEND

&#x20;   propone



A2 PREPARE

&#x20;   prepara plan/artefacto



A3 EXECUTE\_WITH\_APPROVAL

&#x20;   puede ejecutar tras aprobación



A4 EXECUTE\_AUTOMATICALLY

&#x20;   ejecuta dentro de política



A5 EXECUTE\_REPAIR\_ESCALATE

&#x20;   ejecuta, verifica, intenta reparar y escala

```



\---



\# 33. Contrato Context Request



```yaml

context\_request:



&#x20; id:



&#x20; purpose:



&#x20; requester:

&#x20;   system:

&#x20;   capability\_ref:



&#x20; scope:



&#x20;   project\_refs: \[]

&#x20;   goal\_refs: \[]

&#x20;   task\_refs: \[]



&#x20; query:



&#x20; requested\_types:

&#x20;   - fact

&#x20;   - decision

&#x20;   - constraint

&#x20;   - knowledge

&#x20;   - task

&#x20;   - artifact

&#x20;   - history

&#x20;   - status



&#x20; limits:

&#x20;   max\_items:

&#x20;   max\_tokens:

&#x20;   max\_age:



&#x20; sensitivity\_ceiling:



&#x20; correlation\_id:

```



\---



\# 34. Context Package



```yaml

context\_package:



&#x20; id:



&#x20; request\_id:



&#x20; generated\_at:



&#x20; objective:



&#x20; constraints: \[]



&#x20; decisions: \[]



&#x20; facts: \[]



&#x20; knowledge\_refs: \[]



&#x20; task\_refs: \[]



&#x20; artifact\_refs: \[]



&#x20; history\_refs: \[]



&#x20; capability\_refs: \[]



&#x20; excluded:



&#x20;   - reason:

&#x20;     resource\_ref:



&#x20; provenance: \[]



&#x20; estimated\_tokens:



&#x20; freshness:

```



\---



\# 35. Context Package es snapshot



Una vez entregado a un Run:



```text

immutable

```



La ejecución debe poder demostrar:



```text

qué contexto recibió

```



aunque el conocimiento cambie después.



\---



\# 36. Knowledge Context



AI OS Core no copia el contenido completo de Knowledge Orchestrator salvo necesidad.



Preferencia:



```text

knowledge\_ref

```



y recuperación bajo demanda.



Knowledge Orchestrator ya dispone de API local para documentos, claims y consultas fundamentadas, por lo que puede conservar la propiedad del conocimiento.



\---



\# 37. Decision Contract



```yaml

decision:



&#x20; id: decision\_...



&#x20; title:



&#x20; status:

&#x20;   enum:

&#x20;     - proposed

&#x20;     - active

&#x20;     - superseded

&#x20;     - rejected



&#x20; decision:



&#x20; rationale:



&#x20; scope:



&#x20; affects: \[]



&#x20; alternatives: \[]



&#x20; evidence\_refs: \[]



&#x20; supersedes:

&#x20;   decision\_id | null



&#x20; created\_at:



&#x20; approved\_by:

```



\---



\# 38. Decision Rule



Una Decision activa debe entrar en Context cuando:



```text

scope coincida

\+

afecte a la capability

```



Ejemplo:



```text

Agora no gestiona calendario humano.

```



Ese principio deberá acompañar cualquier planificación que implique Agora.



\---



\# 39. Contrato Task



Propietario:



```text

Gestión-tareas-IA

```



```yaml

task:



&#x20; id: task\_...



&#x20; title:

&#x20; description:



&#x20; actor:

&#x20;   enum:

&#x20;     - human

&#x20;     - ai

&#x20;     - hybrid

&#x20;     - system



&#x20; status:

&#x20;   enum:

&#x20;     - proposed

&#x20;     - planned

&#x20;     - ready

&#x20;     - running

&#x20;     - blocked

&#x20;     - waiting\_human

&#x20;     - waiting\_ai

&#x20;     - completed

&#x20;     - cancelled

&#x20;     - failed



&#x20; goal\_ref:

&#x20; objective\_ref:



&#x20; priority:



&#x20; scheduling:



&#x20;   earliest\_start:

&#x20;   latest\_finish:



&#x20;   fixed\_start:

&#x20;   fixed\_end:



&#x20;   flexible:



&#x20; duration:



&#x20;   wall\_clock\_estimate:

&#x20;   human\_active\_estimate:

&#x20;   ai\_compute\_estimate:



&#x20;   confidence:



&#x20;   source:

&#x20;     enum:

&#x20;       - manual

&#x20;       - historical

&#x20;       - statistical

&#x20;       - heuristic



&#x20; dependencies: \[]



&#x20; resource\_requirements: \[]



&#x20; capability\_requirements: \[]



&#x20; approval\_requirements: \[]



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 40. Task Dependency



```yaml

task\_dependency:



&#x20; predecessor\_task\_id:



&#x20; successor\_task\_id:



&#x20; type:

&#x20;   enum:

&#x20;     - finish\_to\_start

&#x20;     - start\_to\_start

&#x20;     - finish\_to\_finish

&#x20;     - human\_approval

&#x20;     - artifact\_required

&#x20;     - resource\_required



&#x20; lag:

&#x20;   duration | null



&#x20; required\_artifact\_type:

&#x20;   string | null

```



\---



\# 41. Dependencias permitidas



```text

Human → Human

Human → AI

AI → Human

AI → AI

Hybrid → cualquiera

```



\---



\# 42. Human calendar



La planificación humana utilizará:



```text

human\_active\_estimate

```



No:



```text

wall\_clock\_estimate

```



para bloquear calendario.



\---



\# 43. Ejemplo



Tarea IA:



```text

Analizar 40 documentos

```



```yaml

wall\_clock\_estimate: 150m

human\_active\_estimate: 5m

ai\_compute\_estimate: 145m

```



El calendario humano reserva:



```text

5m

```



no 150m.



\---



\# 44. Contrato AI Capacity



Proveedor principal:



```text

AI Broker

```



```yaml

ai\_capacity\_snapshot:



&#x20; observed\_at:



&#x20; host:



&#x20; resources:



&#x20;   cpu:

&#x20;     utilization:



&#x20;   ram:

&#x20;     total:

&#x20;     available:



&#x20;   gpu:

&#x20;     total\_memory:

&#x20;     available\_memory:

&#x20;     utilization:



&#x20;   npu:

&#x20;     available:



&#x20; models:



&#x20;   - model\_ref:



&#x20;     status:

&#x20;       enum:

&#x20;         - unloaded

&#x20;         - loading

&#x20;         - ready

&#x20;         - busy

&#x20;         - unavailable



&#x20;     queue\_depth:



&#x20;     estimated\_available\_at:



&#x20; confidence:

```



\---



\# 45. Capacity es observación



AI Broker informa.



Gestión-tareas-IA decide planificación.



No al revés.



\---



\# 46. AI Duration Estimate



```yaml

ai\_duration\_estimate:



&#x20; capability\_ref:



&#x20; execution\_fingerprint\_partial:



&#x20; workload:



&#x20;   input\_tokens:

&#x20;   files:

&#x20;   pages:

&#x20;   expected\_output\_tokens:



&#x20; historical\_samples:



&#x20; estimates:



&#x20;   p50:

&#x20;   p80:

&#x20;   p95:



&#x20; estimated\_queue\_wait:



&#x20; generated\_at:



&#x20; confidence:

```



\---



\# 47. Valor recomendado



Para scheduling inicial:



```text

duration = P80

```



P95 puede reservarse para:



```text

deadlines críticos

```



\---



\# 48. Contrato Job



Propietario:



```text

Agora

```



```yaml

job:



&#x20; id: job\_...



&#x20; source\_task\_id:



&#x20; goal\_id:

&#x20; objective\_id:



&#x20; capability\_ref:



&#x20; status:

&#x20;   enum:

&#x20;     - pending

&#x20;     - ready

&#x20;     - claimed

&#x20;     - running

&#x20;     - blocked

&#x20;     - completed

&#x20;     - failed

&#x20;     - cancelled

&#x20;     - recovery\_pending



&#x20; worker\_requirements: \[]



&#x20; resource\_requirements: \[]



&#x20; certification\_requirements: \[]



&#x20; inputs: \[]



&#x20; outputs: \[]



&#x20; retry\_policy:



&#x20; timeout:



&#x20; correlation\_id:



&#x20; created\_at:

&#x20; updated\_at:

```



\---



\# 49. Task ↔ Job



```text

Task

&#x20; │

&#x20; ├── 0..N Jobs

```



Un Job nunca modifica directamente el calendario.



\---



\# 50. Job puede existir sólo para AI/System



Para:



```text

actor = human

```



normalmente:



```text

0 Jobs

```



Para:



```text

actor = ai

```



normalmente:



```text

1..N Jobs

```



\---



\# 51. Job Dispatch Contract



```yaml

job\_dispatch:



&#x20; job\_id:



&#x20; capability\_ref:



&#x20; inputs:



&#x20; context\_package\_ref:



&#x20; certification\_policy\_ref:



&#x20; autonomy\_level:



&#x20; timeout:



&#x20; idempotency\_key:



&#x20; correlation\_id:

```



\---



\# 52. Contrato Agent Run



Propietario:



```text

Athena

```



```yaml

agent\_run:



&#x20; id: run\_...



&#x20; job\_id:



&#x20; capability\_ref:



&#x20; skill\_refs: \[]



&#x20; execution\_fingerprint:



&#x20; context\_package\_ref:



&#x20; permissions:



&#x20; status:



&#x20; started\_at:

&#x20; finished\_at:



&#x20; verification:



&#x20; repair\_cycles:



&#x20; artifact\_refs: \[]



&#x20; broker\_task\_refs: \[]



&#x20; correlation\_id:

```



Athena ya dispone de sesiones recuperables, permisos, verificación y repair, por lo que este contrato encaja con su arquitectura existente sin convertirlo en scheduler global.



\---



\# 53. Contrato Artifact



```yaml

artifact:



&#x20; id: artifact\_...



&#x20; type:



&#x20; producer:

&#x20;   system:

&#x20;   resource\_ref:



&#x20; task\_ref:

&#x20; job\_ref:

&#x20; run\_ref:



&#x20; uri:



&#x20; media\_type:



&#x20; hash:

&#x20;   algorithm: sha256

&#x20;   value:



&#x20; size:



&#x20; created\_at:



&#x20; immutable:



&#x20; provenance:



&#x20; verification:

```



\---



\# 54. Artifact Rule



Un resultado relevante no debe viajar únicamente como texto en un Event.



Debe existir un Artifact si:



```text

es reutilizable

es auditable

es grande

es necesario como dependencia

```



\---



\# 55. Verification Result



```yaml

verification\_result:



&#x20; status:

&#x20;   enum:

&#x20;     - passed

&#x20;     - failed

&#x20;     - partial

&#x20;     - not\_run



&#x20; verifier:



&#x20; checks:



&#x20;   - key:

&#x20;     status:

&#x20;     evidence\_ref:



&#x20; started\_at:

&#x20; completed\_at:

```



\---



\# 56. Failure Contract



```yaml

failure:



&#x20; category:

&#x20;   enum:

&#x20;     - transient

&#x20;     - capability\_unavailable

&#x20;     - model\_uncertified

&#x20;     - resource\_unavailable

&#x20;     - dependency\_blocked

&#x20;     - policy\_blocked

&#x20;     - approval\_required

&#x20;     - verification\_failed

&#x20;     - contract\_violation

&#x20;     - permanent



&#x20; code:



&#x20; message:



&#x20; retryable:



&#x20; retry\_after:



&#x20; evidence\_refs: \[]



&#x20; occurred\_at:

```



\---



\# 57. Error humano



`message` debe poder mostrarse en UI.



No:



```text

NullReference in foo.py line 188

```



como única explicación.



Puede existir adicionalmente:



```text

technical\_details

```



para diagnóstico.



\---



\# 58. Command Envelope



Cuando AI OS solicita que otro sistema haga algo:



```yaml

command:



&#x20; id:



&#x20; type:



&#x20; target\_system:



&#x20; capability\_ref:



&#x20; subject\_ref:



&#x20; payload:



&#x20; requested\_by:



&#x20; autonomy\_level:



&#x20; approval\_ref:



&#x20; correlation\_id:



&#x20; idempotency\_key:



&#x20; created\_at:

```



\---



\# 59. Command ≠ Event



```text

COMMAND

&#x20; algo debería ocurrir



EVENT

&#x20; algo ocurrió

```



Nunca mezclarlos.



\---



\# 60. API AI OS Core — v1 mínima



Base conceptual:



```text

/api/v1

```



\---



\# 61. Health



```text

GET /api/v1/health

```



Respuesta:



```yaml

status: healthy | degraded | unhealthy

version:

contract\_version:

time:

```



\---



\# 62. Goals



```text

GET    /api/v1/goals

POST   /api/v1/goals

GET    /api/v1/goals/{id}

PATCH  /api/v1/goals/{id}

```



No DELETE físico.



Utilizar:



```text

status = cancelled

```



\---



\# 63. Objectives



```text

GET  /api/v1/goals/{goal\_id}/objectives

POST /api/v1/goals/{goal\_id}/objectives

```



\---



\# 64. Capabilities



```text

GET  /api/v1/capabilities

GET  /api/v1/capabilities/{key}

POST /api/v1/capabilities/register

```



`register` requiere autenticación de servicio.



\---



\# 65. Skills



AI OS no administra contenido de skills.



Mantiene referencias.



```text

GET /api/v1/skills

```



Los providers publican/describen.



\---



\# 66. Certifications



AI OS mantiene proyección.



```text

GET /api/v1/certifications

GET /api/v1/certifications/{id}

```



Creación real:



```text

Model Drift

```



\---



\# 67. Events



```text

POST /api/v1/events



GET /api/v1/events

GET /api/v1/events/{id}

```



Filtros:



```text

type

source

subject

correlation\_id

since

```



\---



\# 68. Context



```text

POST /api/v1/context/resolve

```



Entrada:



```text

ContextRequest

```



Salida:



```text

ContextPackage

```



\---



\# 69. Decisions



```text

GET  /api/v1/decisions

POST /api/v1/decisions

GET  /api/v1/decisions/{id}

```



\---



\# 70. Resource Graph



```text

GET /api/v1/resources

GET /api/v1/resources/{id}



GET /api/v1/relations

```



\---



\# 71. Plans



OS-0 sólo define preview.



```text

POST /api/v1/plans/preview

```



No implica ejecución.



Respuesta futura:



```yaml

plan:



&#x20; goal\_ref:



&#x20; proposed\_objectives: \[]



&#x20; proposed\_tasks: \[]



&#x20; dependencies: \[]



&#x20; required\_capabilities: \[]



&#x20; unresolved: \[]



&#x20; policy\_findings: \[]

```



\---



\# 72. Orchestration



Se reserva el contrato:



```text

POST /api/v1/orchestrations

```



pero OS-1 puede no implementarlo todavía.



\---



\# 73. Service Registration



Cada aplicación deberá poder anunciarse.



```yaml

service\_registration:



&#x20; system:



&#x20; instance\_id:



&#x20; version:



&#x20; contract\_versions:



&#x20; base\_url:



&#x20; capabilities\_endpoint:



&#x20; events\_supported: \[]



&#x20; health\_endpoint:



&#x20; authentication:



&#x20; observed\_at:

```



\---



\# 74. Authentication



Primer objetivo:



```text

service-to-service

```



Mínimo aceptable para entorno local:



```text

Bearer service token

```



Objetivo posterior:



```text

OAuth2/OIDC

```



No guardar secretos en:



```text

event payload

resource graph

logs

context package

```



\---



\# 75. Data Classification



Valores comunes:



```text

PUBLIC

INTERNAL

CONFIDENTIAL

SENSITIVE

```



Todo Context Package debe tener:



```text

classification\_ceiling

```



\---



\# 76. Aplicación de privacidad



Una capability con:



```text

max\_classification = INTERNAL

```



no puede recibir:



```text

CONFIDENTIAL

```



aunque el modelo lo solicite.



\---



\# 77. Contrato mínimo AI Broker → AI OS



AI Broker deberá exponer:



```text

GET models

GET capabilities

GET capacity

GET model identity

```



y publicar:



```text

model.\*

broker.capacity\_changed

```



El Broker ya posee catálogo, routing, estrategias y telemetría, por lo que el cambio requerido debe limitarse a exponer información adicional, no trasladar allí planificación u objetivos.



\---



\# 78. Contrato mínimo AI OS → AI Broker



AI OS no enviará inferencias normalmente.



Las enviarán:



```text

Athena

Atomic Worker

otros clientes

```



AI OS sólo podrá consultar:



```text

availability

capabilities

identity

capacity

```



\---



\# 79. Contrato mínimo Model Drift



Debe aceptar conceptualmente:



```text

CertificationRequest

```



y producir:



```text

Certification

```



Model Drift ya posee políticas bloqueantes, manifests, fingerprints y comparación formal, por lo que su ampliación natural es convertir algunas suites en suites de certificación.



\---



\# 80. Contrato mínimo Gestión-tareas-IA



Debe exponer:



```text

GET tasks

GET task/{id}

POST task

PATCH task



GET schedule

GET human-capacity



POST ai-duration-estimate/request

```



y consumir:



```text

AI Capacity

Capability availability

Job status

```



\---



\# 81. Calendario externo



Google Calendar seguirá siendo una fuente externa leída por Gestión-tareas-IA.



AI OS Core no accede directamente a Google Calendar.



Gestión-tareas-IA ya mantiene actualmente la integración de calendario en modo de solo lectura, por lo que seguirá siendo su frontera natural.



\---



\# 82. Contrato mínimo Gestión Tareas → Agora



Cuando una Task IA esté lista:



```yaml

create\_job\_request:



&#x20; source\_task\_id:



&#x20; capability\_ref:



&#x20; inputs:



&#x20; deadline:



&#x20; resource\_requirements:



&#x20; certification\_requirements:



&#x20; context\_package\_ref:



&#x20; correlation\_id:



&#x20; idempotency\_key:

```



\---



\# 83. Agora responde



```yaml

create\_job\_response:



&#x20; job\_id:



&#x20; status:



&#x20; accepted\_at:

```



\---



\# 84. Agora → Gestión Tareas



Eventos:



```text

job.started

job.completed

job.failed

job.blocked

```



Gestión Tareas actualiza su Task.



No accede al Board interno.



\---



\# 85. Agora Capability Worker Contract



Todo worker deberá anunciar:



```yaml

worker:



&#x20; id:



&#x20; capabilities:



&#x20;   - key:

&#x20;     version:



&#x20; resources:



&#x20; runtimes: \[]



&#x20; status:



&#x20; last\_seen:

```



Agora ya funciona como runtime durable con Board y workers que reclaman tarjetas de forma atómica, por lo que esta ampliación mantiene su responsabilidad actual.



\---



\# 86. Athena Capability Advertisement



Athena debe anunciar al menos:



```text

analyze\_repository

modify\_repository

verify\_repository

```



si están disponibles.



No se debe inferir capacidad por nombre.



\---



\# 87. Athena Skill Advertisement



Endpoint conceptual:



```text

GET /capabilities

GET /skills

```



Cada skill devuelve:



```text

key

version

hash

tool requirements

applicable capabilities

```



\---



\# 88. AI OS → Athena



En operación normal no necesariamente llama directamente a Athena.



Ruta preferida para trabajo durable:



```text

AI OS

&#x20;↓

Gestión Tareas

&#x20;↓

Agora

&#x20;↓

Athena

```



Ruta directa sólo para capacidades síncronas expresamente diseñadas.



\---



\# 89. Knowledge Orchestrator API



AI OS consumirá únicamente APIs públicas del Orchestrator:



```text

query

documents

claims

entities

```



Nunca:



```text

SQLite

vault interno

```



\---



\# 90. Knowledge Events



Ejemplo:



```yaml

event:



&#x20; type: knowledge.superseded



&#x20; subject:

&#x20;   resource\_type: claim

&#x20;   resource\_id: claim\_...



&#x20; payload:



&#x20;   previous\_ref:

&#x20;   replacement\_ref:

&#x20;   reason:

```



AI OS decidirá si esto afecta a:



```text

Goal

Project

Task

Decision

```



\---



\# 91. ChatyGPT Contract



ChatyGPT será inicialmente:



```text

AI OS Client

```



Consumirá:



```text

Goals

Events

Decisions

Approvals

Context explanations

```



No será propietario del estado global.



\---



\# 92. Approval Request



```yaml

approval\_request:



&#x20; id:



&#x20; requested\_action:



&#x20; capability\_ref:



&#x20; risk:



&#x20; consequences:



&#x20; affected\_resources: \[]



&#x20; expires\_at:



&#x20; status:

&#x20;   enum:

&#x20;     - pending

&#x20;     - approved

&#x20;     - rejected

&#x20;     - expired



&#x20; created\_at:

```



\---



\# 93. Approval Decision



```yaml

approval\_decision:



&#x20; approval\_id:



&#x20; decision:

&#x20;   enum:

&#x20;     - approve\_once

&#x20;     - approve\_scope

&#x20;     - reject



&#x20; decided\_by:



&#x20; decided\_at:



&#x20; scope:

```



\---



\# 94. Local AI Lab



No entra en ruta crítica.



Puede publicar:



```text

evidence.available

```



con:



```text

hardware benchmark

model benchmark

retrieval evidence

```



Model Drift puede utilizarlo posteriormente.



Local AI Lab ya dispone de puente formal hacia Model Drift, por lo que no hace falta crear una dependencia nueva fuerte.



\---



\# 95. YT Capture Plugin



Sin cambio obligatorio en OS-0.



Su contrato actual termina en:



```text

captura Markdown

&#x20;↓

Knowledge Orchestrator

```



Esto ya respeta propiedad de dominio.



\---



\# 96. Resource Graph mínimo



Tipos iniciales:



```text

PROJECT

GOAL

OBJECTIVE

TASK

JOB

RUN

CAPABILITY

SKILL

MODEL

CERTIFICATION

ARTIFACT

DECISION

KNOWLEDGE

APPLICATION

POLICY

```



\---



\# 97. Relaciones permitidas



```text

HAS

DEPENDS\_ON

BLOCKS

USES

REQUIRES

PROVIDES

PRODUCES

VERIFIED\_BY

CERTIFIED\_FOR

OWNED\_BY

RELATED\_TO

SUPERSEDES

PART\_OF

TRIGGERED\_BY

```



\---



\# 98. Ejemplo de grafo



```text

Goal

&#x20;│ HAS

&#x20;▼

Objective

&#x20;│ HAS

&#x20;▼

Task

&#x20;│ REQUIRES

&#x20;▼

Capability

&#x20;│ PROVIDED\_BY

&#x20;▼

Athena

&#x20;│ USES

&#x20;▼

Skill

&#x20;│ CERTIFIED\_FOR

&#x20;▼

Model Fingerprint

```



\---



\# 99. Estado externo



AI OS no debe considerar su copia de estado como autoridad absoluta.



Cada referencia externa incluirá:



```text

observed\_at

```



y opcionalmente:



```text

etag/version

```



\---



\# 100. Reconciliación



Si:



```text

AI OS dice Job RUNNING

Agora dice Job COMPLETED

```



gana:



```text

Agora

```



por ser propietario.



AI OS actualiza su proyección.



\---



\# 101. Prohibiciones arquitectónicas



\## PROHIBIDO



AI OS Core leyendo SQLite de:



```text

Agora

Athena

Broker

KO

Gestión Tareas

```



\## PROHIBIDO



AI OS modificando directamente:



```text

Google Calendar

Obsidian Vault

repositorio Git

model files

```



\## PROHIBIDO



Un LLM escribiendo directamente:



```text

state global

policies

certifications

```



\---



\# 102. Regla del Planner futuro



Cuando llegue el Planner:



```text

LLM

&#x20;↓

Plan Proposal

&#x20;↓

Schema Validation

&#x20;↓

Policy Engine

&#x20;↓

Capability Validation

&#x20;↓

Certification Validation

&#x20;↓

User Approval si procede

&#x20;↓

Task creation

```



Nunca:



```text

LLM → ejecución

```



\---



\# 103. Estados de servicio



Todos los servicios deberán poder anunciar:



```text

healthy

degraded

unavailable

```



`degraded` significa:



```text

servicio operativo

pero alguna capability no disponible

```



\---



\# 104. Capability Health



Ejemplo:



```yaml

capability\_health:



&#x20; capability\_ref:



&#x20; status:

&#x20;   available | degraded | unavailable



&#x20; reason:



&#x20; dependencies:



&#x20; observed\_at:

```



\---



\# 105. Model Certification Gate



Antes de ejecutar una Capability que exige certificación:



```text

Capability

&#x20;↓

required skill

&#x20;↓

current execution fingerprint

&#x20;↓

Certification Registry

```



Resultado:



```text

CERTIFIED

&#x20;   → permitir



DEGRADED

&#x20;   → aplicar Policy



UNKNOWN

&#x20;   → bloquear / solicitar test



FAILED

&#x20;   → bloquear



REVOKED

&#x20;   → bloquear

```



\---



\# 106. Excepción controlada



Puede existir:



```text

manual\_override

```



pero debe requerir:



```text

approval

reason

expiration

audit event

```



Nunca override permanente silencioso.



\---



\# 107. Estimación IA y scheduling



Flujo:



```text

Task propuesta

&#x20;   ↓

Capability

&#x20;   ↓

candidate execution profile

&#x20;   ↓

Broker historical data

&#x20;   ↓

P50/P80/P95

&#x20;   ↓

Gestión Tareas

&#x20;   ↓

planificación AI capacity

```



\---



\# 108. Reestimación dinámica



Si una Job empieza:



```text

10:00

```



y su ETA cambia:



```text

11:00 → 12:30

```



Gestión Tareas sólo debe replanificar tareas humanas si existe una dependencia:



```text

AI → H

```



que quede afectada.



\---



\# 109. No solapamiento falso



No existe conflicto porque:



```text

Humano ocupado

\+

IA ocupada

```



ocurran simultáneamente.



Sólo existe conflicto si comparten:



```text

human resource

AI hardware resource

exclusive resource

dependency

```



\---



\# 110. Schedule Snapshot



```yaml

schedule\_snapshot:



&#x20; generated\_at:



&#x20; human\_slots: \[]



&#x20; ai\_slots: \[]



&#x20; dependencies: \[]



&#x20; resource\_constraints: \[]



&#x20; confidence:

```



\---



\# 111. Auditoría



Toda decisión automatizada relevante debe generar:



```text

Event

```



incluyendo:



```text

qué se decidió

qué Policy intervino

qué Capability

qué Certification

qué contexto

```



\---



\# 112. Explicabilidad mínima



El sistema debe poder responder:



```text

¿Por qué se creó esta tarea?

¿Por qué se eligió esta capability?

¿Por qué se bloqueó?

¿Por qué no se usó este modelo?

¿Por qué se movió en el calendario?

¿Por qué necesita mi aprobación?

```



\---



\# 113. Registro de decisiones automatizadas



```yaml

decision\_trace:



&#x20; id:



&#x20; subject:



&#x20; inputs: \[]



&#x20; policies\_applied: \[]



&#x20; capabilities\_considered: \[]



&#x20; certifications\_checked: \[]



&#x20; result:



&#x20; reason:



&#x20; created\_at:

```



\---



\# 114. Contratos que deben congelarse al final de OS-0



Antes de programar OS-1 deben quedar aprobados:



```text

ResourceReference v1

Goal v1

Objective v1

CapabilityManifest v1

SkillManifest v1

ExecutionFingerprint v1

Certification v1

Event v1

Policy v1

ContextRequest v1

ContextPackage v1

Decision v1

Task v1

TaskDependency v1

AICapacitySnapshot v1

AIDurationEstimate v1

Job v1

AgentRun v1

Artifact v1

Failure v1

ApprovalRequest v1

```



\---



\# 115. Cambios mínimos obligatorios por repo



\## AI OS Core



Crear:



```text

Goals

Objectives

Resources

Relations

Capabilities

Policies

Events

Decisions

Context metadata

```



\---



\## AI Broker



Añadir:



```text

model fingerprint

capacity snapshot

model lifecycle events

```



Opcional posterior:



```text

certification-aware routing

```



\---



\## Model Drift



Añadir:



```text

CertificationRequest

Skill Certification Suite

CertificationResult

```



\---



\## Gestión-tareas-IA



Añadir:



```text

actor

dependencies

human\_active\_duration

ai\_compute\_duration

AI resource constraints

Task↔Job relation

```



\---



\## Agora



Añadir:



```text

capability identity

Task correlation

certification requirements

worker capabilities

events

```



\---



\## Athena



Añadir:



```text

capability manifest

skill manifest export

execution fingerprint

context package input

events

```



\---



\## Knowledge Orchestrator



Añadir:



```text

stable resource refs

events

context-oriented query filters

```



\---



\## ChatyGPT



Añadir:



```text

AI OS client

Goal views

Approval Inbox

decision/context explanation

```



\---



\## Local AI Lab



Opcional:



```text

evidence publication

```



\---



\## YT Capture Plugin



```text

sin cambios obligatorios

```



\---



\# 116. Fases posteriores derivadas



Con OS-0 aprobado:



```text

OS-1 Core Registry

OS-2 Service Discovery

OS-3 Goal/Decision UI

OS-4 Human+AI Task Graph

OS-5 Agora execution bridge

OS-6 Skill Certification

OS-7 Context Engine

OS-8 Policy Engine

OS-9 Planner

OS-10 Conditional Autonomy

```



\---



\# 117. Decisiones arquitectónicas propuestas para congelar



\## ADR-AIOS-001



AI OS Core no ejecuta inferencia directamente.



\## ADR-AIOS-002



Gestión-tareas-IA conserva propiedad exclusiva de calendario y scheduling.



\## ADR-AIOS-003



Agora conserva propiedad exclusiva de ejecución IA durable.



\## ADR-AIOS-004



Athena sigue siendo Agent Runtime, no scheduler.



\## ADR-AIOS-005



AI Broker decide modelo/estrategia, no objetivos.



\## ADR-AIOS-006



Knowledge Orchestrator conserva propiedad del ciclo de vida del conocimiento.



\## ADR-AIOS-007



Model Drift se convierte en autoridad de certificación skill/model/runtime.



\## ADR-AIOS-008



AI OS almacena referencias federadas, no replica bases de datos ajenas.



\## ADR-AIOS-009



Eventos son hechos; Commands son intenciones.



\## ADR-AIOS-010



Toda autonomía está ligada a Capability + Policy, nunca al LLM.



\## ADR-AIOS-011



Toda combinación nueva de Skill/Model/Runtime relevante comienza sin certificación.



\## ADR-AIOS-012



Tiempo humano y tiempo IA son recursos planificables distintos.



\## ADR-AIOS-013



Una Task IA no bloquea tiempo humano salvo `human\_active` o dependencia explícita.



\## ADR-AIOS-014



El Planner futuro sólo genera planes tipados; nunca ejecuta texto libre.



\---



\# 118. Arquitectura contractual resultante



```text

&#x20;                      AI OS CORE

&#x20;                          │

&#x20;         Goals / Context / Policies / State

&#x20;                          │

&#x20;      ┌───────────────────┼────────────────────┐

&#x20;      │                   │                    │

&#x20;      ▼                   ▼                    ▼

Knowledge             Gestión Tareas       Model Drift

Orchestrator               │               Certification

&#x20;                           │

&#x20;                  Human + AI Task Graph

&#x20;                           │

&#x20;                           ▼

&#x20;                         Agora

&#x20;                           │

&#x20;                   Capability + Job

&#x20;                           │

&#x20;            ┌──────────────┼─────────────┐

&#x20;            ▼              ▼             ▼

&#x20;         Athena         Atomic       Deterministic

&#x20;                        Worker          Worker

&#x20;            │              │

&#x20;            └───────┬──────┘

&#x20;                    ▼

&#x20;                AI Broker

&#x20;                    │

&#x20;            certified models

```



\---



\# 119. Criterio de cierre de OS-0



OS-0 se considerará aprobado cuando podamos responder sin ambigüedad:



```text

¿Quién es propietario de este dato?

¿Cómo se referencia?

¿Qué servicio puede modificarlo?

¿Qué evento genera?

¿Qué Capability representa?

¿Qué Policy aplica?

¿Qué certificación necesita?

¿Qué relación tiene con una Task?

¿Qué relación tiene con un Job?

¿Qué parte ocupa mi calendario?

¿Qué parte consume recursos IA?

```



Si alguna de estas respuestas depende de “ya veremos al programarlo”, OS-0 no está cerrado.



\---



\# 120. Resultado



Con estos contratos, AI OS Core puede comenzar como:



```text

FastAPI

\+

SQLite

\+

Registry

\+

Event Store

\+

Resource Graph ligero

\+

Policies

```



sin:



```text

LLM propio

UI propia

scheduler propio

worker propio

knowledge store propio

```



Eso mantiene el Core pequeño y evita duplicar sistemas que ya existen.



La inteligencia del AI OS no vendrá de contenerlo todo.



Vendrá de \*\*saber dónde está cada cosa, qué significa, qué se puede hacer con ella y bajo qué condiciones\*\*.



Hay una decisión especialmente valiosa que sale de OS-0: \*\*la certificación de skills deja de ser una función genérica del AI OS y pasa a tener un propietario claro: Model\_Drift\*\*. Eso evita duplicar motores de evaluación y aprovecha que ya tiene fingerprints, manifests, políticas bloqueantes y separación entre cambio y regresión.



También queda cerrado el tema que te preocupaba del calendario: \*\*Gestión-tareas-IA conserva tu calendario y pasa a planificar dos capacidades distintas —humana e IA— unidas por dependencias\*\*. Una tarea IA sólo ocupa tu agenda por su `human\_active\_estimate`; su tiempo de cómputo se planifica aparte contra recursos de IA.





