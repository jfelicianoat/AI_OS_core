# Fase 07 — Knowledge Orchestrator: integración con AI OS

## OBJETIVO REAL

Mantener a Knowledge Orchestrator como autoridad del conocimiento y exponer sólo referencias y eventos útiles para Context.

## CAMBIOS

### Stable Resource References
Definir URIs estables:
- `knowledge://document/...`
- `knowledge://claim/...`
- `knowledge://entity/...`

### Eventos
- `knowledge.created`
- `knowledge.updated`
- `knowledge.superseded`
- `knowledge.contradicted`
- `knowledge.expired`

### Query orientada a Context
Añadir filtros por:
- project;
- goal;
- entity;
- date;
- validity;
- source;
- sensitivity.

### Provenance
Toda respuesta utilizada como conocimiento debe conservar:
- source_id;
- spans/evidence;
- validity;
- observed/version date.

## NO HACER

- no Goal Engine;
- no scheduling;
- no planner global;
- no permitir que Core lea SQLite;
- no autoaplicar cambios semánticos que hoy requieren revisión humana.

## VERIFICACIÓN

- resource refs resuelven de forma estable;
- superseded no desaparece;
- eventos no contienen documentos completos si basta una referencia;
- KO funciona standalone.
