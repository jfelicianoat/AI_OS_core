# Fase 12 — Context Engine federado

## OBJETIVO REAL

Construir el contexto mínimo necesario para cada capacidad sin convertir el AI OS Core en un segundo Knowledge Orchestrator.

## FUENTES

- Goals/Objectives: AI OS Core
- Decisions/Policies: AI OS Core
- Tasks: Gestión-tareas-IA
- Jobs: Agora
- Runs: Athena
- Knowledge: KO
- Artifacts: owner correspondiente
- model/capability status: Broker/Core projections

## CAPAS

- Global
- User
- Project
- Goal
- Task
- Execution

## PROCESO

ContextRequest
→ resolver scope
→ consultar fuentes autorizadas
→ filtrar sensibilidad
→ filtrar vigencia
→ aplicar decisiones/policies
→ limitar tamaño
→ generar ContextPackage inmutable
→ registrar exclusiones y provenance.

## REGLAS

- no meter toda la memoria;
- no duplicar knowledge;
- no usar LLM para decidir seguridad;
- se puede usar ranking semántico sólo después de filtros deterministas;
- package entregado a Run es snapshot auditable.

## VERIFICACIÓN

- conocimiento superseded no aparece como activo;
- sensitive no cruza ceiling;
- context package reproduce exactamente referencias usadas;
- KO apagado produce degradación explícita, no inventa contexto;
- límites de tokens respetados.
