# Fase 10 — Integración end-to-end sin autonomía

## OBJETIVO REAL

Conectar los servicios reales y demostrar un recorrido completo, todavía con decisiones sensibles bajo control humano.

## ESCENARIO DE REFERENCIA

Goal:
`Preparar un informe técnico sobre un proyecto`

Flujo:

1. ChatyGPT crea Goal en AI OS Core.
2. Usuario/plan manual crea Objective.
3. Gestión-tareas-IA crea:
   - una Task humana inicial si hace falta;
   - una Task IA de análisis.
4. Gestión Tareas consulta capacidad/ETA.
5. Task IA se convierte en Job de Agora.
6. Agora selecciona worker compatible.
7. Athena ejecuta capability.
8. AI Broker sirve modelo elegible.
9. Athena verifica.
10. Agora publica Artifact.
11. Gestión Tareas marca Task según Job.
12. AI OS actualiza Goal progress.
13. ChatyGPT muestra trazabilidad.

## CONDICIONES

- sin Planner LLM todavía;
- sin creación autónoma de Tasks;
- certificación requerida sólo donde la policy lo declare;
- approvals explícitas para acciones sensibles.

## PRUEBAS E2E

1. happy path;
2. Broker unavailable;
3. model uncertified;
4. worker unavailable;
5. Athena verification failed;
6. Job recovery after restart;
7. Core restart;
8. stale service;
9. duplicate event;
10. cancelled human dependency.

## EVIDENCIAS

Guardar:
- correlation_id;
- IDs de Goal/Task/Job/Run;
- artifact hash;
- verification result;
- events timeline.

## CRITERIO DE ACEPTACIÓN

El sistema debe poder explicar:
- por qué se creó la Task;
- qué capability necesitaba;
- qué worker la ejecutó;
- qué modelo se usó;
- qué certificación aplicó;
- cuánto tiempo humano ocupó;
- qué artifact produjo;
- cómo se verificó.
