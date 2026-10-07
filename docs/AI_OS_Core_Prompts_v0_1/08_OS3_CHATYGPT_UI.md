# Fase 08 — ChatyGPT como ventana humana del AI OS

## OBJETIVO REAL

Añadir superficies de interacción con AI OS Core sin trasladar lógica de orquestación a ChatyGPT.

## CAMBIOS

### AI OS Client
Cliente tipado para:
- Goals
- Objectives
- Events
- Decisions
- Approvals
- Context explanations
- Capability status

### Vista Goals
Mostrar:
- active;
- blocked;
- progress;
- próximos review/deadline;
- Objectives relacionados.

### Approval Inbox
Centralizar solicitudes pendientes:
- capability;
- riesgo;
- consecuencias;
- recursos afectados;
- approve once / approve scope / reject.

### Trazabilidad
Mostrar cadena cuando exista:
`Goal → Objective → Task → Job → Run → Artifact`

### Context Inspector
Además de qué contexto recibió el LLM, mostrar:
- por qué fue seleccionado;
- fuente;
- vigencia;
- qué se excluyó y por qué.

## GUARDRAILS

ChatyGPT no:
- evalúa policies;
- decide certificaciones;
- crea Jobs directamente;
- modifica calendario;
- lee bases de otros proyectos.

## VERIFICACIÓN

- Core apagado no rompe chat normal;
- approvals son explícitas;
- trazabilidad no expone secretos/rutas sensibles;
- Goal UI no modifica Task Manager directamente.
