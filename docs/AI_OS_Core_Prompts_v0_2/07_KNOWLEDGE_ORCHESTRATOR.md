# Prompt 07 — Knowledge Orchestrator: referencias versionadas y contexto auditable

## FASE ARQUITECTÓNICA
OS-2/OS-7.

## OBJETIVO
Permitir contexto reproducible sin duplicar KO.

## CONTRATO ACTUAL
No asumir que una query IA devuelve contenido síncrono.
Respetar su naturaleza durable y endpoint posterior de resultado.

## RESOURCE REFS
Cada contenido consumible debe ofrecer:
- stable resource id;
- immutable revision/version id cuando exista;
- content hash;
- provenance;
- validity.

## CONTEXT MATERIALIZATION
Para un Run histórico debe poder demostrarse el contenido efectivo:
- preferir immutable revision recuperable;
- si KO no garantiza retención, materializar fragmento/snapshot en el sistema que custodia evidencia del Run;
- hash solo verifica contenido disponible, no lo recupera.

## EVENTS
- knowledge.created
- knowledge.updated
- knowledge.superseded
- knowledge.contradicted
- knowledge.expired
con source sequence/revision.

## RETENTION
Separar:
- expiración para nuevo uso;
- retención histórica de evidencia consumida.

## PRUEBAS
- claim superseded no se usa como actual;
- run antiguo puede auditar fragmento exacto;
- KO cambia documento después del Run;
- query durable se sondea correctamente;
- KO standalone intacto.
