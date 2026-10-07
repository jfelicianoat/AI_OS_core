# Fase 04 — Adaptación mínima de Athena

## OBJETIVO REAL

Hacer que Athena sea descubrible por el AI OS como Agent Runtime, sin convertirla en scheduler ni control plane.

## CAMBIOS

### Capability Advertisement
Exponer manifest para capacidades reales, por ejemplo:
- `analyze_repository`
- `modify_repository`
- `verify_repository`

No declarar capacidades no implementadas.

### Skill Advertisement
Exponer:
- key;
- version;
- instructions_hash;
- required toolsets;
- applicable capabilities;
- risk constraints.

### Execution Fingerprint
Cada Agent Run debe capturar:
- capability/version;
- skill/version/hash;
- model fingerprint disponible;
- runtime version;
- toolset versions/schema hashes;
- policy version;
- generation config observable.

### Context Package Input
Permitir que un run reciba un `context_package_ref` o snapshot validado.

El paquete es input, no autoridad para ampliar permisos.

### Eventos
- `agent.run.started`
- `agent.run.completed`
- `agent.run.failed`
- `agent.verification.failed`
- `agent.repair.started`
- `agent.repair.completed`
- `skill.updated`

### Correlación
Aceptar y propagar:
- goal_id;
- objective_id;
- task_id;
- job_id;
- correlation_id.

## INVARIANTES

- permisos siguen dentro de Athena;
- skills no conceden permisos;
- verifier no escribe;
- no Planner global;
- no scheduling;
- no acceso a DB del Core.

## VERIFICACIÓN

- Athena funciona standalone sin Core;
- manifests son válidos OS-0;
- run conserva fingerprint;
- Context Package no aumenta capabilities;
- eventos llevan source correcto;
- cancelación y recuperación siguen intactas.
