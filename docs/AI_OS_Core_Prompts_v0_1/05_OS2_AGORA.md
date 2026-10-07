# Fase 05 — Adaptación mínima de Agora / AGR

## OBJETIVO REAL

Convertir Agora en el Work Runtime durable del AI OS sin hacerla propietaria del calendario ni de Goals.

## CAMBIOS

### Job Contract
Extender Cards/Jobs con referencias:
- source_task_id;
- goal_id;
- objective_id;
- capability_ref;
- correlation_id;
- certification requirements;
- resource requirements.

### Worker Advertisement
Cada worker anuncia:
- capabilities;
- versions;
- resources;
- runtimes;
- status;
- last_seen.

### Eventos
- `job.created`
- `job.claimed`
- `job.started`
- `job.completed`
- `job.failed`
- `job.cancelled`
- `artifact.created`
- `worker.available`
- `worker.unavailable`

### Certification Gate
Una Card puede requerir:
- skill certification;
- capability certification;
- fingerprint constraints.

Si no se cumple:
- no ejecutar;
- estado bloqueado explícito;
- failure `MODEL_UNCERTIFIED` o equivalente.

### Task Correlation
Agora nunca modifica la Task de Gestión-tareas-IA.
Sólo publica Job state.

## GUARDRAILS

No:
- calendario humano;
- Goal Engine;
- model routing;
- knowledge lifecycle.

## VERIFICACIÓN

- Board sigue siendo source of truth de Jobs;
- claim atómico sigue intacto;
- reinicio conserva correlación;
- worker incompatible no reclama Job;
- certificación ausente bloquea sin perder Card;
- funciona standalone sin Core.
